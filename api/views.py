import json
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Password
from .serializers import PasswordSerializer, ServicesAndPasswordsSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse



@extend_schema(
    request=PasswordSerializer,
    responses={
        201: PasswordSerializer,
        200: PasswordSerializer,
        400: "Неверные данные",
        404: "Пароль не найден",
        500: "Ошибка сервера"
    },
    description="""
    - Для создания/изменения пароля используйте POST.
    - Для поиска пароля по имени севиса используйте GET
    """
)
@api_view(['GET', 'POST'])
def password_handler(request, service_name):
    if request.method == 'GET':
        try:
            password = Password.objects.get(service_name=service_name)
            serializer = PasswordSerializer(password)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Password.DoesNotExist:
            return Response({"detail": "Password not found"}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'POST':
        try:
            password, created = Password.objects.get_or_create(service_name=service_name)
            serializer = PasswordSerializer(password, data=request.data, partial=not created)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@extend_schema(
    summary="Поиск пароля по части имени сервиса",
    description="Этот эндпоинт позволяет искать пароли по части имени сервиса.",
    parameters=[
        OpenApiParameter(
            name='service_name',
            type=str,
            location=OpenApiParameter.QUERY,
            description="Часть имени сервиса для поиска (например, 'yan').",
            required=True,
        ),
    ],
    responses={
        200: PasswordSerializer(many=True),
        400: OpenApiResponse(description="Ошибка: параметр 'service_name' отсутствует."),
        404: OpenApiResponse(description="Ошибка: пароли не найдены."),
    }
)
@api_view(['GET'])
def password_search(request):
    """
    Поиск пароля по части имени сервиса.

    Параметры:
    - service_name: Часть имени сервиса для поиска (обязательный параметр).

    Пример запроса:
    GET /password/search/?service_name=yun
    """
    service_name_part = request.query_params.get('service_name', None)

    if not service_name_part:
        return Response(
            {"detail": "Parameter 'service_name' is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    passwords = Password.objects.filter(service_name__icontains=service_name_part)

    if not passwords.exists():
        return Response(
            {"detail": "No passwords found for the given service name."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ServicesAndPasswordsSerializer(passwords, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)