# inside payments/tests/test_cloudinary_mock.py or menu tests
import pytest
from unittest.mock import patch

@pytest.mark.django_db
def test_cloudinary_upload_mock(monkeypatch):
    class DummyUpload:
        def __call__(*args, **kwargs):
            return {"secure_url": "https://res.cloudinary.com/fake/image/upload/v123/test.jpg"}
    monkeypatch.setattr("cloudinary.uploader.upload", DummyUpload())
    # call your upload function and assert it returns secure_url
    assert "cloudinary"  # pattern demonstration
