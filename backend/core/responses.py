from rest_framework import status
from rest_framework.response import Response


def success_response(data, status=status.HTTP_200_OK) -> Response:
    return Response({"success": True, "data": data}, status=status)


def error_response(message: str, detail=None, status=status.HTTP_400_BAD_REQUEST) -> Response:
    error = {"message": message}
    if detail is not None:
        error["detail"] = detail
    return Response({"success": False, "error": error}, status=status)
