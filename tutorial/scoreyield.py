from collections import deque


def give_score(scores):
    score_queue = deque(scores)
    current_score = score_queue.popleft()
    while current_score:
        is_empty = yield
        if not is_empty:
            yield current_score
        else:
            try:
                current_score = score_queue.popleft()
                yield current_score
            except IndexError:
                break


givescore = give_score([5, 4])
givescore.send(None)

import pudb; pudb.set_trace()
t = givescore.send(False)
t1 = givescore.send(False)
t2 = givescore.send(True)
t3 = givescore.send(False)
t4 = givescore.send(True)



