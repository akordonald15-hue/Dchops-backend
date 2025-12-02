# core/exceptions.py
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status
from core.utils.response import api_response

def custom_exception_handler(exc, context):
    # Let DRF build the basic response first
    response = drf_exception_handler(exc, context)

    if response is None:
        # Unhandled exception — return 500 with minimal info
        return api_response(False, "Internal server error", data=None, errors={"detail": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # If DRF produced a response (validation errors etc.)
    # Normalize it to our format
    data = response.data
    status_code = response.status_code
    # If DRF already used 'detail' or error dict, pass as errors
    return api_response(False, "", data=None, errors=data, status=status_code)
