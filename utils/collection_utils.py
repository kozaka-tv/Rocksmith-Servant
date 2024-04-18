import os


def is_empty(collection):
    return not collection


def is_not_empty(collection):
    return bool(collection)


def set_of_the_tuples_from_the_first_position(tuples):
    if tuples is None:
        return None

    return set([item[0] for item in tuples])


def repr_in_multi_line(collection):
    if collection is None:
        return 'None'

    if len(collection) == 0:
        return ''

    if type(collection) is dict:
        return os.linesep + os.linesep.join(f"{k}: ({v})" for k, v in collection.items())

    return os.linesep + os.linesep.join(collection)
