import json
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Password
from .serializers import PasswordSerializer, ServicesAndPasswordsSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse



# @extend_schema(
#     request=PasswordSerializer,
#     responses={201: str, 400: str},
#     description=""
# )
# @api_view(['POST'])
# def create_or_update_password(request, service_name):
#     """
#     Сохраняет или обновляет пароль для указанного сервиса.

#     Параметры:
#     - service_name (str): Название сервиса (передается в URL).
#     - password (str): Пароль (передается в теле запроса).

#     Пример тела запроса:
#     {
#         "password": "very_secret_pass"
#     }
#     """
#     if request.method == 'POST':
#         password = request.data.get('password')
        
#         if password is None:
#             return Response({'error': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         password_obj, created  = Password.objects.update_or_create(
#             service_name=service_name,
#             defaults={'password': password}
#         )
        
#         return Response({
#             'password': password_obj.password
#         }, status=status.HTTP_200_OK)
    


# @api_view(['GET'])
# def get_password(request, service_name):
#     try:
#         password = Password.objects.get(service_name=service_name)
#         serializer = PasswordSerializer(password)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     except Password.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

# @api_view(['GET'])
# def search_passwords(request):
#     part_of_service_name = request.query_params.get('service_name', None)
#     if part_of_service_name:
#         passwords = Password.objects.filter(service_name__icontains=part_of_service_name)
#         serializer = PasswordSerializer(passwords, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=PasswordSerializer,
    responses={
        201: PasswordSerializer,  # Успешное создание
        200: PasswordSerializer,  # Успешное обновление
        400: "Неверные данные",
        404: "Пароль не найден",
        500: "Ошибка сервера"
    },
    description="""
    Создание или обновление пароля для указанного сервиса.
    - Для создания используйте POST.
    - Для обновления используйте PUT.
    """
)
@api_view(['GET', 'POST'])
def password_handler(request, service_name):
    if request.method == 'GET':
        # Логика для GET-запроса (получение пароля)
        try:
            password = Password.objects.get(service_name=service_name)
            serializer = PasswordSerializer(password)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Password.DoesNotExist:
            return Response({"detail": "Password not found"}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'POST':
        # Логика для POST
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
            description="Часть имени сервиса для поиска (например, 'yun').",
            required=True,
            examples=[
                OpenApiExample(
                    'Пример 1',
                    value='yun',
                    description="Поиск паролей для сервисов, содержащих 'yun'."
                ),
                OpenApiExample(
                    'Пример 2',
                    value='google',
                    description="Поиск паролей для сервисов, содержащих 'google'."
                ),
            ],
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
    # Получаем параметр `service_name` из запроса
    service_name_part = request.query_params.get('service_name', None)

    # Проверяем, что параметр `service_name` передан
    if not service_name_part:
        return Response(
            {"detail": "Parameter 'service_name' is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Ищем пароли, которые содержат часть имени сервиса
    passwords = Password.objects.filter(service_name__icontains=service_name_part)

    # Если пароли не найдены, возвращаем 404
    if not passwords.exists():
        return Response(
            {"detail": "No passwords found for the given service name."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Сериализуем найденные пароли
    serializer = ServicesAndPasswordsSerializer(passwords, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)