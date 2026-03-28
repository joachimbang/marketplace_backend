from rest_framework.response import Response
from rest_framework import status


def success_response(message, body=None, code=status.HTTP_200_OK):
    return Response(
        {
            "status": "success",
            "message": message,
            "body": body
        },
        status=code
    )


def error_response(message, code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {
            "status": "error",
            "message": message
        },
        status=code
    )


def get_serializer_error(serializer):
    errors = serializer.errors

    if isinstance(errors, dict):
        field = list(errors.keys())[0]
        message = errors[field][0]
        return message

    return "Erreur de validation"