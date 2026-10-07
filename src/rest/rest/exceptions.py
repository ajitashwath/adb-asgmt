from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    """Report DRF-raised errors (e.g. malformed JSON) as {"error": "<message>"}."""
    response = exception_handler(exc, context)
    if response is not None and isinstance(response.data, dict) and 'detail' in response.data:
        response.data = {'error': str(response.data['detail'])}
    return response
