from rest_framework.response import Response

def success_response(message="", data=None, status=200):
    payload = {
        "success": True,
        "message": message,
        "data": data,
        "errors": None
    }
    return Response(payload, status=status)

def error_response(message="", errors=None, status=400):
    payload = {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors
    }
    return Response(payload, status=status)

# alias in case other code uses api_response(...)
api_response = success_response
