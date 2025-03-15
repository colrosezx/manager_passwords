from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import Password
from .serializers import PasswordSerializer
from manager_passwords.utils import password_manager



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
            password_instance = Password.objects.get(service_name=service_name)
            encrypted_password = password_instance.password

            decrypted_password = password_manager.decrypt_password(encrypted_password)
            serializer = PasswordSerializer(password_instance)
            response_data = serializer.data
            response_data['password'] = decrypted_password

            return Response(response_data, status=status.HTTP_200_OK)
        except Password.DoesNotExist:  
            return Response({"detail": "Пароль не найден"}, status=status.HTTP_404_NOT_FOUND)

    
    elif request.method == 'POST':
        try:
            password_data = request.data.get('password')
            if not password_data:
                return Response({"detail": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)

            encrypted_password = password_manager.encrypt_password(password_data)
            password_instance, created = Password.objects.get_or_create(service_name=service_name)
            password_instance.password = encrypted_password.decode('utf-8')
            password_instance.save()

            decrypted_password = password_manager.decrypt_password(encrypted_password)
            serializer = PasswordSerializer(password_instance)
            response_data = serializer.data
            response_data['password'] = decrypted_password  # Добавляем расшифрованный пароль в ответ

            return Response(response_data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
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

    decrypted_passwords = []
    for password_instance in passwords:
        decrypted_password = password_manager.decrypt_password(password_instance.password)
        if decrypted_password is not None:
            decrypted_passwords.append({
                'service_name': password_instance.service_name,
                'password': decrypted_password
            })
        else:
            return Response(
                {"detail": "Ошибка расшифровки одного или нескольких паролей."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return Response(decrypted_passwords, status=status.HTTP_200_OK)