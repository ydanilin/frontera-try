import logging

from w3lib.util import to_bytes
from frontera.contrib.backends.sqlalchemy import Distributed
from frontera.contrib.backends.sqlalchemy.components import Metadata, Queue, retry_and_rollback
from frontera.core.models import Request


import trace
def traceit(func):
    def wrap(self, *args, **kwargs):
        tracer = trace.Trace(count=0, trace=0, countcallers=1, outfile="trace.bin")
        result = tracer.runfunc(func, *(self, *args), **kwargs)
        r = tracer.results()
        r.write_results(show_missing=True, coverdir=".")
        return result

    return wrap


class WlwBackend(Distributed):
    def __init__(self, manager):
        self.logger = logging.getLogger("WlwBackend")
        super(WlwBackend, self).__init__(manager)


    def _init_db_worker(self, manager):
        settings = manager.settings
        drop = settings.get('SQLALCHEMYBACKEND_DROP_ALL_TABLES')
        clear_content = settings.get('SQLALCHEMYBACKEND_CLEAR_CONTENT')
        metadata_m = self.models['MetadataModel']
        queue_m = self.models['QueueModel']
        self.check_and_create_tables(drop, clear_content, (metadata_m, queue_m))
        self._metadata = Metadata(self.session_cls, metadata_m,
                                  settings.get('SQLALCHEMYBACKEND_CACHE_SIZE'))
        self._queue = WlwQueue(self.session_cls, queue_m, settings.get('SPIDER_FEED_PARTITIONS'))


    def get_next_requests(self, max_next_requests, **kwargs):
        partitions = kwargs.pop('partitions', [0])  # TODO: Collect from all known partitions
        batch = []
        # sending False will not trigger score automata to next score anyway
        score = self.manager.strategy.get_score(False)
        if not score:
            self.logger.info('No more score levels to schedule')
            return []

        for partition_id in partitions:
            batch.extend(self.queue.get_next_requests(max_next_requests, partition_id, score, **kwargs))
        # now, if batch was not empty, score automata will not trigger and
        # will show the same score again. Otherwise it advances to the next score
        # was_empty = False if len(batch) else True
        # next = self.manager.strategy.get_score(was_empty)
        # if next != score:
        #     self.logger.debug('Score changed')
        self.manager.strategy.register_departed(batch)
        self.manager.strategy.departed += len(batch)
        self.logger.info(f"Departed {len(batch)} flights, total {self.manager.strategy.departed}")
        return batch


class WlwQueue(Queue):
    def __init__(self, session_cls, queue_cls, partitions, ordering='default'):
        super(WlwQueue, self).__init__(session_cls, queue_cls, partitions, ordering)
        self.logger.setLevel('DEBUG')

    @traceit
    def get_next_requests(self, max_n_requests, partition_id, score, **kwargs):
        results = []
        try:
            queue = self.queue_model
            query = self.session.query(queue
                ).filter(queue.partition_id == partition_id, queue.score >= score
                ).order_by(queue.created_at
                ).limit(max_n_requests)
            for item in query:
                method = item.method or b'GET'
                r = Request(item.url, method=method, meta=item.meta, headers=item.headers, cookies=item.cookies)
                fp = item.fingerprint
                msg = f"retrieved request {fp[:6]}...{fp[-6:]}"
                self.logger.info(msg)
                r.meta[b'fingerprint'] = to_bytes(item.fingerprint)
                r.meta[b'score'] = item.score
                results.append(r)
                self.session.delete(item)
            self.session.commit()
        except Exception as exc:
            self.logger.exception(exc)
            self.session.rollback()
        self.logger.info(f"Got {len(results)} next requests with score {score}")
        return results

    @retry_and_rollback
    def amount_with_score(self, score):
        return self.session.query(self.queue_model).filter_by(score=score).count()

    @retry_and_rollback
    def schedule(self, batch):
        super(WlwQueue, self).schedule(batch)
