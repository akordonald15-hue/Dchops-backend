# core/utils/response.py
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response as DRFResponse

def api_response(success: bool, message: str = "", data=None, errors=None, status=200):
    payload = {
        "success": bool(success),
        "message": message or "",
        "data": data if data is not None else None,
        "errors": errors if errors is not None else None
    }
    return DRFResponse(payload, status=status)

class StandardJSONRenderer(JSONRenderer):
    """
    Forces all responses to use the standard API shape when the view returns
    a dict / list / etc. If a view already returns a Response with 'success'
    key, we leave it alone.
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # If view returned an already-wrapped response, pass through
        response = renderer_context.get('response', None)
        request = renderer_context.get('request', None)
        # If data already has success key, assume wrapped
        if isinstance(data, dict) and 'success' in data:
            return super().render(data, accepted_media_type, renderer_context)

        # For non-error responses (200-299), wrap as success
        status_code = getattr(response, "status_code", 200)
        if 200 <= status_code < 300:
            payload = {"success": True, "message": "", "data": data, "errors": None}
            return super().render(payload, accepted_media_type, renderer_context)

        # For error responses, if DRF produced detail or errors, normalize
        # data may be a dict with 'detail' or validation error format
        errors = data
        message = ""
        payload = {"success": False, "message": message, "data": None, "errors": errors}
        return super().render(payload, accepted_media_type, renderer_context)
