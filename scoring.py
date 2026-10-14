"""Moral Rank scoring (SPEC.md section 5). Constants changes need the owner's approval."""
import math

VER = {"verified": 1.0, "probable": 0.6, "disputed": 0.2, "unverified": 0.0, "misattributed": 0.0}
REL = {"expresses": 1.0, "similar": 0.7, "partial": 0.4, "contrasts": 0.0}
W_Q, W_K, W_T, W_R = 1.0, 1.0, 3.0, 1.5
BETA = 0.2


def ancestors(t, traditions):
    seen, stack = set(), list(traditions.get(t, {}).get("derives_from", []))
    while stack:
        a = stack.pop()
        if a not in seen:
            seen.add(a)
            stack += traditions.get(a, {}).get("derives_from", [])
    return seen


def evidence(quotes, traditions):
    """quotes: list of dicts with ver, rel, conf, thinker, tradition, era. Returns (E, breakdown)."""
    ws = [(q, VER[q["ver"]] * REL[q["rel"]] * q["conf"]) for q in quotes]
    Q = sum(w for _, w in ws)
    best_k, best_t = {}, {}
    for q, w in ws:
        best_k[q["thinker"]] = max(best_k.get(q["thinker"], 0), w)
        best_t[q["tradition"]] = max(best_t.get(q["tradition"], 0), w)
    supporting = {t for t, w in best_t.items() if w > 0}
    T = sum((0.5 if ancestors(t, traditions) & supporting else 1.0) * w for t, w in best_t.items())
    K = sum(best_k.values())
    R = len({q["era"] for q, w in ws if w >= 0.3})
    E = W_Q * math.log(1 + Q) + W_K * math.sqrt(K) + W_T * T + W_R * R
    return E, {"Q": Q, "K": K, "T": T, "R": R, "E": E,
               "traditions": len(supporting)}


def moral_rank(E, edges, beta=BETA, iters=200):
    """E: {concept: evidence}; edges: [(a, b, weight)] undirected. Returns {concept: 0-100}."""
    nodes = list(E)
    tot = sum(E.values()) or 1.0
    e = {c: E[c] / tot for c in nodes}
    nbr = {c: {} for c in nodes}
    for a, b, w in edges:
        if w > 0:
            nbr[a][b] = nbr[a].get(b, 0) + w
            nbr[b][a] = nbr[b].get(a, 0) + w
    r = dict(e)
    for _ in range(iters):
        nxt = {c: (1 - beta) * e[c] for c in nodes}
        for c in nodes:
            s = sum(nbr[c].values())
            if s == 0:  # dangling: redistribute via e
                for d in nodes:
                    nxt[d] += beta * r[c] * e[d]
            else:
                for d, w in nbr[c].items():
                    nxt[d] += beta * r[c] * w / s
        r = nxt
    m = max(r.values()) or 1.0
    return {c: 100 * r[c] / m for c in nodes}, r
