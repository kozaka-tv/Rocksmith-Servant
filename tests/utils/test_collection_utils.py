import os

import pytest

from utils import collection_utils

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
    assert collection_utils.is_empty(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (None, False),
        (set(), False),
        ([1, 2], True)
    ]
)
def test_is_not_empty(test_input, expected):
    assert collection_utils.is_not_empty(test_input) == expected


def test_set_of_the_tuples_from_the_first_position__with_none():
    tuple_to_test = None

    actual = collection_utils.set_of_the_tuples_from_the_first_position(tuple_to_test)

    assert actual is None


def test_set_of_the_tuples_from_the_first_position__with_an_empty_list_input():
    tuple_to_test = []

    actual = collection_utils.set_of_the_tuples_from_the_first_position(tuple_to_test)

    assert len(actual) == 0


def test_set_of_the_tuples_from_the_first_position__with_1_tuple_and_string_in_the_first_position():
    test_input = [('first tuple 1st', 'first tuple 2nd', 'first tuple 3rd')]
    expected = {'first tuple 1st'}

    actual = collection_utils.set_of_the_tuples_from_the_first_position(test_input)

    assert actual == expected


def test_set_of_the_tuples_from_the_first_position__with_1_tuple_and_int_in_the_first_position():
    test_input = [(1, 'first tuple 2nd', 'first tuple 3rd')]
    expected = {1}

    actual = collection_utils.set_of_the_tuples_from_the_first_position(test_input)

    assert actual == expected


def test_set_of_the_tuples_from_the_first_position__with_2_tuples_and_string_in_the_first_position():
    test_input = [
        ('first tuple 1st', 'first tuple 2nd', 'first tuple 3rd'),
        ('second tuple 1st', 'second tuple 2nd', 'second tuple 3rd'),
    ]
    expected = {
        'first tuple 1st',
        'second tuple 1st',
    }

    actual = collection_utils.set_of_the_tuples_from_the_first_position(test_input)

    assert actual == expected


def test_set_of_the_tuples_from_the_first_position__with_2_tuples_and_int_in_the_first_position():
    test_input = [
        (1, 'first tuple 2nd', 'first tuple 3rd'),
        (2, 'second tuple 2nd', 'second tuple 3rd'),
    ]
    expected = {1, 2}

    actual = collection_utils.set_of_the_tuples_from_the_first_position(test_input)

    assert actual == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (None, 'None'),
        (set(), ''),
        (dict(), ''),

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
    actual = collection_utils.repr_in_multi_line(test_input)
    assert actual == expected
