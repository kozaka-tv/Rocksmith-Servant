def is_empty(collection):
    return not collection


def is_not_empty(collection):
    return bool(collection)


def set_of_the_tuples_first_position(tuple_):
    return set([item[0] for item in tuple_])
