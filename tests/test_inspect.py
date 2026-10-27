import pytest
from inspect_site import inspect


def test_rejects_arbitrary_websites(tmp_path):
    with pytest.raises(ValueError):
        inspect('https://example.com/',str(tmp_path))


def test_rejects_insecure_url(tmp_path):
    with pytest.raises(ValueError):
        inspect('http://www.land-savvy.com/',str(tmp_path))
