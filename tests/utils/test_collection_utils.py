import os

import pytest

from utils.collection_utils import (is_valid_collection,
                                    is_collection_empty,
                                    is_collection_not_empty,
                                    get_tuples_from_the_first_position_of,
                                    repr_in_multi_line)

NL = os.linesep


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (None, True),
        (set(), True),
        ([1, 2], False)
    ]
)
def test_is_empty(test_input, expected):
    assert is_collection_empty(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (None, False),
        (set(), False),
        ([1, 2], True)
    ]
)
def test_is_not_empty(test_input, expected):
    assert is_collection_not_empty(test_input) == expected


def test_get_tuples_from_the_first_position_of__with_none():
    tuple_to_test = None

    # noinspection PyTypeChecker
    actual = get_tuples_from_the_first_position_of(tuple_to_test)

    assert len(actual) == 0


def test_get_tuples_from_the_first_position_of__with_an_empty_list_input():
    tuple_to_test = []

    actual = get_tuples_from_the_first_position_of(tuple_to_test)

    assert len(actual) == 0


def test_get_tuples_from_the_first_position_of__with_1_tuple_and_string_in_the_first_position__type_is_set():
    test_input = [('first tuple 1st', 'first tuple 2nd', 'first tuple 3rd')]

    actual = get_tuples_from_the_first_position_of(test_input)

    assert isinstance(actual, set)


def test_get_tuples_from_the_first_position_of__with_1_tuple_and_string_in_the_first_position():
    test_input = [('first tuple 1st', 'first tuple 2nd', 'first tuple 3rd')]
    expected = {'first tuple 1st'}

    actual = get_tuples_from_the_first_position_of(test_input)

    assert actual == expected


def test_get_tuples_from_the_first_position_of__with_1_tuple_and_int_in_the_first_position():
    test_input = [(1, 'first tuple 2nd', 'first tuple 3rd')]
    expected = {1}

    actual = get_tuples_from_the_first_position_of(test_input)

    assert actual == expected


def test_get_tuples_from_the_first_position_of__with_2_tuples_and_string_in_the_first_position():
    test_input = [
        ('first tuple 1st', 'first tuple 2nd', 'first tuple 3rd'),
        ('second tuple 1st', 'second tuple 2nd', 'second tuple 3rd'),
    ]
    expected = {
        'first tuple 1st',
        'second tuple 1st',
    }

    actual = get_tuples_from_the_first_position_of(test_input)

    assert actual == expected


def test_get_tuples_from_the_first_position_of__with_2_tuples_and_int_in_the_first_position():
    test_input = [
        (1, 'first tuple 2nd', 'first tuple 3rd'),
        (2, 'second tuple 2nd', 'second tuple 3rd'),
    ]
    expected = {1, 2}

    actual = get_tuples_from_the_first_position_of(test_input)

    assert actual == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (None, 'None'),
        ({}, ''),
        ({}, ''),

        (['line1'], NL + 'line1'),
        (['line1', 'line2'], NL + 'line1' + NL + 'line2'),
        (['line1', 'line2', 'line3'], NL + 'line1' + NL + 'line2' + NL + 'line3'),

        (
                {'key1': {'key1-item1': 'key1-item1-value1', 'key1-item2': 'key1-item2-value1'}},
                NL + "key1: ({'key1-item1': 'key1-item1-value1', 'key1-item2': 'key1-item2-value1'})"
        ),
        (
                {
                    'key1': {'key1-item1': 'key1-item1-value1', 'key1-item2': 'key1-item2-value1'},
                    'key2': {'key2-item1': 'key2-item1-value1', 'key2-item2': 'key2-item2-value1'},
                },
                NL + "key1: ({'key1-item1': 'key1-item1-value1', 'key1-item2': 'key1-item2-value1'})" +
                NL + "key2: ({'key2-item1': 'key2-item1-value1', 'key2-item2': 'key2-item2-value1'})"
        )
    ]
)
def test_repr_in_multi_line(test_input, expected):
    actual = repr_in_multi_line(test_input)
    assert actual == expected


def test_repr_in_multi_line_none():
    assert repr_in_multi_line(None) == 'None'


def test_repr_in_multi_line_empty_list():
    assert repr_in_multi_line([]) == ''


def test_repr_in_multi_line_empty_dict():
    assert repr_in_multi_line({}) == ''


def test_repr_in_multi_line_empty_set():
    assert repr_in_multi_line(set()) == ''


def test_repr_in_multi_line_list():
    collection = [1, 2, 3]
    expected_output = f"{NL}1{NL}2{NL}3"
    assert repr_in_multi_line(collection) == expected_output


def test_repr_in_multi_line_dict():
    collection = {'key1': 'value1', 'key2': 'value2'}
    expected_output = f"{NL}key1: (value1){NL}key2: (value2)"
    assert repr_in_multi_line(collection) == expected_output


def test_repr_in_multi_line_tuple():
    collection = (10, 20, 30)
    expected_output = f"{NL}10{NL}20{NL}30"
    assert repr_in_multi_line(collection) == expected_output


def test_repr_in_multi_line_set():
    collection = {5, 10, 15}
    expected_output = NL + NL.join(map(str, collection))
    assert repr_in_multi_line(collection) == expected_output


def test_repr_in_multi_line_invalid_input():
    with pytest.raises(ValueError, match="Input must be a collection or None"):
        repr_in_multi_line(42)


def test_repr_in_multi_line_string():
    with pytest.raises(ValueError, match="Input must be a collection or None"):
        repr_in_multi_line("string")


def test_is_valid_collection_with_list():
    assert is_valid_collection([1, 2, 3]) is True


def test_is_valid_collection_with_dict():
    assert is_valid_collection({"key": "value"}) is True


def test_is_valid_collection_with_tuple():
    assert is_valid_collection((1, 2, 3)) is True


def test_is_valid_collection_with_set():
    assert is_valid_collection({1, 2, 3}) is True


def test_is_valid_collection_with_none():
    assert is_valid_collection(None) is True


def test_is_valid_collection_with_string():
    assert is_valid_collection("not a collection") is False


def test_is_valid_collection_with_int():
    assert is_valid_collection(42) is False


def test_is_valid_collection_with_float():
    assert is_valid_collection(3.14) is False


def test_is_valid_collection_with_boolean():
    assert is_valid_collection(True) is False
