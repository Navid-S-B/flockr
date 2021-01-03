"""
Example test.
"""
import pytest
import echo
from error import InputError

def test_echo():
    """
    Basic echo tests.
    """
    assert echo.echo("1") == "1", "1 == 1"
    assert echo.echo("abc") == "abc", "abc == abc"
    assert echo.echo("trump") == "trump", "trump == trump"

def test_echo_except():
    """
    Trigger exception.
    """
    with pytest.raises(InputError):
        assert echo.echo("echo")
