import pytest
import requests
from requests.models import Response
from unittest.mock import patch

@pytest.mark.django_db
def test_paystack_verify_mock(monkeypatch):
    """
    Example: patch requests.get/post used inside your payments verification
    function to simulate Paystack API.
    Adjust path to requests call used in your code.
    """

    class DummyResp:
        status_code = 200
        def json(self):
            return {"status": True, "data": {"reference": "abc", "amount": 2000}}

    monkeypatch.setattr("requests.get", lambda *args, **kwargs: DummyResp())

    # call your verify function (example)
    # from payments.utils import verify_paystack
    # result = verify_paystack("abc")
    # assert result["status"] is True

    # Because project specifics vary, this test shows the mock pattern.
    assert requests.get("https://api.paystack.co/transaction/verify/abc").json()["status"] is True
