#!/usr/bin/python

import logging

from io import TextIOWrapper
from csv import DictReader
from collections import deque
from functools import partial, reduce
from time import sleep
from frontera.strategy.basic import BasicCrawlingStrategy


def coro_give_score(scores):
    print(f"CORO charged, scores = {scores}")
    score_queue = deque(scores)
    current_score = score_queue.popleft()
    print(f"CORO current score = {current_score}, scores left: {scores}")
    while current_score:
        is_empty = yield
        if not is_empty:
            print(f"CORO received '{is_empty}', yielding {current_score}")
            yield current_score  # after first send it stops here
        else:
            try:
                current_score = score_queue.popleft()
                print(f"CORO received '{is_empty}', yielding from TRY: {current_score}")
                yield current_score
            except IndexError:
                print(f"CORO received '{is_empty}', IndexERROR break {current_score}")
                break


class WlwStrategy(BasicCrawlingStrategy):
    def __init__(self, manager, args, scheduled_stream, states_context):
        self.scores = (
            ('page', 0.8),
            ('item', 0.6),
        )
        self.departed = 0
        self.arrived = 0
        self.timetable = {}
        # self.scoregenerator = coro_give_score([x[1] for x in self.scores])
        # TODO: maybe refactor get_score to avoid direct calls to scoregenerator at all!!
        self.scoregenerator = coro_give_score([0.8])  # debugging
        self.scoregenerator.send(None)
        self.logger = logging.getLogger("WlwStrategy")
        self.logger.setLevel(logging.DEBUG)
        super(WlwStrategy, self).__init__(manager, args, scheduled_stream, states_context)

    def read_seeds(self, stream):
        text = TextIOWrapper(stream, encoding='utf-8')
        csv_records = DictReader(text, skipinitialspace=True)
        for entry in csv_records:
            url = entry.pop('url')
            flight = {
                'dest': 'page',
                'from_': '0',
                'to': '1',
                'details': dict(entry),
            }
            r = self.create_request(url.strip(), meta=dict(flight=flight))
            self.schedule(r)

    def page_crawled(self, response):
        self.arrived += 1
        # import pudb; pudb.set_trace()
        fp = response.meta[b'fingerprint'].decode()
        msg = f"page_crawled(), request {fp[:6]}...{fp[-6:]} arrived, total {self.arrived} flights"
        self.logger.info(msg)
        super(WlwStrategy, self).page_crawled(response)

    def filter_extracted_links(self, request, links):
        def add_total_links(counters, link):
            flight = link.meta[b'scrapy_meta']['flight']
            dest = flight['dest']
            flight.update({'links_got': counters[dest]})
            return link
        
        counters = {
            'page': 0,
            'item': 0,
        }
        result = []
        seen = []
        for item in links:
            if item.url not in seen:
                dest = item.meta[b'scrapy_meta']['flight']['dest']
                counters[dest] += 1
                result.append(item)
                seen.append(item.url)
        add_total = partial(add_total_links, counters)
        return list(map(add_total, result))

    def links_extracted(self, request, links):
        # requests come with data:
        # source {'dest': 'page', 'from_': '0', 'to': '1', 'details': {'search': 'Tiefdruck'}}
        # destination {'dest': 'page', 'to': '2'}
        def update_meta(source, destination):
            landed = source.meta['flight']
            template = destination.meta[b'scrapy_meta']['flight']
            flight = dict(template)
            # 1. copy details to destination
            old_details = landed.get('details', {})
            new_details = dict(template.get('details', {}))
            new_details.update(old_details)
            flight.update(details=new_details)
            # 2. destination.from = source.to
            flight.update(from_=landed['to'])
            destination.meta.update(flight=flight)
            return destination
        preflight_check = partial(update_meta, request)

        preflight = list(map(preflight_check, links))
        # score = self.get_score(False)

        scored_flights = map(lambda x: (x.meta[b'fingerprint'], 'planned'),
                             filter(lambda x: x.meta['flight']['dest'] == 'page', preflight)
        )
        self.timetable.update(scored_flights)

        if self.arrived == self.departed:
            # if not self._scheduled_stream._queue.amount_with_score(score):
            amount_planned = reduce(lambda acc, x: acc + 1 if x == 'planned' else acc, self.timetable.values(), 0)
            if amount_planned == 0:
                self.logger.info(f"All {self.arrived} flights returned back. Shift score.")
                self.get_score(True)
        super(WlwStrategy, self).links_extracted(request, preflight)

    def schedule(self, request, score=1.0, dont_queue=False):
        scores = dict(self.scores)
        """ {'page': 0.8,
             'item': 0.6,}
        """
        dest = request.meta['flight']['dest']
        super(WlwStrategy, self).schedule(
            request,
            score=scores[dest],
            dont_queue=dont_queue
        )

    def get_score(self, is_empty):
        try:
            result = self.scoregenerator.send(is_empty)
        except StopIteration:
            return None
        self.scoregenerator.send(None)
        return result

    def register_departed(self, batch):
        departed = map(lambda r: (r.meta[b'fingerprint'], 'departed'), batch)
        self.timetable.update(departed)
