def rev(l: list) -> list:
    """
    >>> rev([1, 2, 3])
    [3, 2, 1]
    """
    return l[::-1]

def reverse_dict(d):
    return {v: k for k, v in d.items()}

def filter_dict(d, keys, inverse=False):
    """ creates a copy of `d` with only the keys present in `keys` (and `d`) """
    if inverse:
        return {k: v for k, v in d.items() if k not in keys}  # note the `not in`
    return {k: v for k, v in d.items() if k in keys}

def map_dict(d, func, on_keys=False):
    """ maps each value of d to func(d) """
    if on_keys:
        return {func(k): v for k, v in d.items()}
    return {k: func(v) for k, v in d.items()}

def show_dict(d):
    return ', '.join(f'{k}: {v}' for k, v in d.items())


def identity(x):
    return x

def all_equal(l: list) -> bool:
    """ https://stackoverflow.com/a/3844832 """
    l = list(l)
    return not l or l.count(l[0]) == len(l)

def class_name(obj: ...) -> str:
    return type(obj).__name__

if __name__ == '__main__':
    import doctest
    doctest.testmod()
