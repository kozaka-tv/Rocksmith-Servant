# File: tests/test_exceptions.py

import pytest

from utils.exceptions import CheckedException, ConfigError


def test_checked_exception_message_formatting():
    error_msg = "Error occurred: {reason}"
    details = {"reason": "Invalid operation"}
    exception = CheckedException(error_msg, **details)
    assert str(exception) == "Error occurred: Invalid operation"


def test_checked_exception_details():
    error_msg = "Error occurred: {reason}"
    details = {"reason": "File not found"}
    exception = CheckedException(error_msg, **details)
    assert str(exception) == "Error occurred: File not found"
    assert exception.details == details


def test_checked_exception_with_missing_kwarg():
    error_msg = "Error occurred: {reason}, code: {code}"
    details = {"reason": "Timeout"}
    with pytest.raises(KeyError):
        CheckedException(error_msg, **details)


def test_checked_exception_with_empty_details():
    error_msg = "A generic error occurred without additional details."
    exception = CheckedException(error_msg)
    assert str(exception) == error_msg
    assert exception.details == {}


def test_config_error_message_formatting():
    error_msg = "Configuration error: {name}"
    details = {"name": "missing_key"}
    exception = ConfigError(error_msg, **details)
    assert str(exception) == "Configuration error: missing_key"


def test_checked_exception_partial_message_formatting():
    error_msg = "Partial error: {missing} information."
    details = {"missing": "Configuration"}
    exception = CheckedException(error_msg, **details)
    assert str(exception) == "Partial error: Configuration information."
    assert exception.details == details


def test_config_error_details():
    error_msg = "Configuration error: {field}"
    details = {"field": "path"}
    exception = ConfigError(error_msg, **details)


def test_config_error_with_missing_kwarg():
    error_msg = "Configuration error in {field}: {detail}"
    details = {"field": "port"}
    with pytest.raises(KeyError):
        ConfigError(error_msg, **details)


def test_config_error_with_empty_details():
    error_msg = "A generic error occurred without additional details"
    exception = ConfigError(error_msg)
    assert str(exception) == error_msg
    assert exception.details == {}


def test_config_error():
    try:
        raise ConfigError("Invalid configuration parameter", param="example")
    except ConfigError as e:
        assert str(e) == "Invalid configuration parameter"
        assert e.details == {"param": "example"}
