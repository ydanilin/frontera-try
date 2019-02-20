import re
from urllib.parse import urlparse, parse_qsl, urlunparse, urlencode


def filter_qparams(qparams, action, url):
    filter_func = {
        'retain': lambda x: x[0] in qparams,
        'remove': lambda x: x[0] not in qparams,
    }
    # <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    # stupid!!! allow_fragments=False does not drop out fragment, but attaches
    # it to the last query parameter. stupid!!!
    scheme, netloc, path, p, query, _ = urlparse(url, allow_fragments=True)
    qparts = parse_qsl(query)
    filtered = dict(filter(filter_func[action], qparts))
    new_query = urlencode(filtered)
    return urlunparse([scheme, netloc, path, p, new_query, '']), filtered


def get_id_from_path(url):
    part = url.split('?')[0]
    firm = part.rsplit('/', 1)[1]
    grp = re.search(r'\d+', firm)
    if grp:
        return grp.group()
    else:
        return None
