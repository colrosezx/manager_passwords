import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import Password
from manager_passwords.utils import password_manager


@pytest.mark.django_db
def test_password_handler_get_success():
    password_instance = Password.objects.create(
        service_name="test_service",
        password= password_manager.encrypt_password("password").decode('utf-8')
    )

    client = APIClient()
    url = reverse('password_handler', args=["test_service"])
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['service_name'] == "test_service"
    assert response.data['password'] == "password"

@pytest.mark.django_db
def test_password_handler_get_not_found():
    client = APIClient()
    url = reverse('password_handler', args=["non_existent_service"])
    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == "Пароль не найден"


@pytest.mark.django_db
def test_password_handler_post_create():
    client = APIClient()
    url = reverse('password_handler', args=["new_service"])
    data = {'password': 'new_password'}

    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['service_name'] == "new_service"
    assert response.data['password'] == "new_password"



@pytest.mark.django_db
def test_password_handler_post_update():
    # Создаем тестовый пароль
    Password.objects.create(
        service_name="existing_service",
        password="old_encrypted_password"
    )

    client = APIClient()
    url = reverse('password_handler', args=["existing_service"])
    data = {'password': 'updated_password'}

    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['service_name'] == "existing_service"
    assert response.data['password'] == "updated_password"

@pytest.mark.django_db
def test_password_search_success():

    encrypted_password_1 = password_manager.encrypt_password("password_1").decode('utf-8')
    encrypted_password_2 = password_manager.encrypt_password("password_2").decode('utf-8')

    Password.objects.create(service_name="yandex", password=encrypted_password_1)
    Password.objects.create(service_name="youtube", password=encrypted_password_2)

    client = APIClient()
    url = reverse('password-search') + "?service_name=yan"
    response = client.get(url)

    print(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['service_name'] == "yandex"
    assert response.data[0]['password'] == "password_1"


@pytest.mark.django_db
def test_password_search_not_found():
    client = APIClient()
    url = reverse('password-search') + "?service_name=non_existent"
    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == "No passwords found for the given service name."


@pytest.mark.django_db
def test_password_search_missing_parameter():
    client = APIClient()
    url = reverse('password-search')
    response = client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "Parameter 'service_name' is required."