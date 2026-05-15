from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    data = response.data
    if isinstance(data, dict) and list(data.keys()) == ["detail"]:
        message = str(data["detail"])
        error = {"message": message}
    else:
        error = {"message": "Request failed.", "detail": data}

    response.data = {"success": False, "error": error}
    return response
