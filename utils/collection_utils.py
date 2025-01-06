import os

LINESEP = os.linesep


def is_collection_empty(collection):
    return not collection


def is_collection_not_empty(collection):
    return bool(collection)


def get_tuples_from_the_first_position_of(list_of_tuples: list[tuple]) -> set:
    if list_of_tuples is None:
        return set()
    return {item[0] for item in list_of_tuples}


def repr_in_multi_line(collection):
    """Formats a collection (list, dict, tuple, set) into a multi-line string representation."""
    if not is_valid_collection(collection):
        raise ValueError("Input must be a collection or None")

    if collection is None:
        return 'None'
    if not collection:
        return ''

    if isinstance(collection, dict):
        return LINESEP + LINESEP.join(f"{key}: ({value})" for key, value in collection.items())

    return LINESEP + LINESEP.join(map(str, collection))


def is_valid_collection(value):
    """Checks whether a value is a valid collection or None."""
    return isinstance(value, (list, dict, tuple, set)) or value is None
