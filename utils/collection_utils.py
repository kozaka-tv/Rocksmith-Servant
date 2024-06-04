import os


def is_empty(collection):
    return not collection


def is_not_empty(collection):
    return bool(collection)


def get_tuples_from_the_first_position_of(list_of_tuples: list[tuple]) -> set:
    if list_of_tuples is None:
        return set()
    return {item[0] for item in list_of_tuples}


def repr_in_multi_line(collection):
    if collection is None:
        return 'None'

    if len(collection) == 0:
        return ''

    if isinstance(collection, dict):
        return os.linesep + os.linesep.join(f"{k}: ({v})" for k, v in collection.items())

    return os.linesep + os.linesep.join(map(str, collection))
