from collections import deque
from itertools import starmap


def give_score(scores):
    score_queue = deque(scores)
    current_score = score_queue.popleft()
    while current_score:
        is_empty = yield
        if not is_empty:
            yield current_score  # after first send it stops here
        else:
            try:
                current_score = score_queue.popleft()
                yield current_score
            except IndexError:
                break


givescore = give_score([5, 4])
givescore.send(None)


def get_score(is_empty):
    try:
        result = givescore.send(is_empty)
    except StopIteration:
        return None
    givescore.send(None)
    return result


# ****** Testing *************

test_array = [
    (False, 5),
    (False, 5),
    (True, 4),
    (False, 4),
    (False, 4),
    (False, 4),
    (True, None),
    (False, None),
]


def testfun(to_send, test_against):
    result = get_score(to_send)
    if result == test_against:
        return 'good', result
    else:
        return 'WRONG', result


print(list(starmap(testfun, test_array)))
