def weight_constraint(w1, w2):
    if w1 is not None and w2 is not None:
        return w1 == w2

    if (w1 is None) != (w2 is None):
        return False

    return True


def core_token_constraint(t1, t2):
    if not t1 or not t2:
        return False

    return t1[0] == t2[0]


def hard_constraints(p1, p2):
    if not core_token_constraint(p1["tokens"], p2["tokens"]):
        return False

    if not weight_constraint(p1["weight"], p2["weight"]):
        return False

    return True