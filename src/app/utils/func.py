import re

# returns list of tuple.
# each tuple express (is_url, text).
def detect_url(text):
    t = text if text is not None else ''
    tl = []
    url_pattern = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    for _ in range(10): # url detection limit
        m = re.search(url_pattern, t)
        if m is None:
            break
        else:
            s = m.start()
            e = m.end()
            if s != 0:
                tl.append((False, t[:s]))
            tl.append((True, t[s:e]))
            t = t[e:]
    if len(t) != 0:
        tl.append((False, t))
    return tl
