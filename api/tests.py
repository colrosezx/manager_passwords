from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Password


class PasswordHandlerTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.service_name = "example_service"
        self.password_data = {"password": "secure_password"}
        self.password = Password.objects.create(service_name=self.service_name, password="old_password")

    def test_get_password_success(self):
        url = reverse('password_handler', args=[self.service_name])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['password'], self.password.password)

    def test_get_password_not_found(self):
        url = reverse('password_handler', args=["nonexistent_service"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_password_success(self):
        url = reverse('password_handler', args=["new_service"])
        response = self.client.post(url, self.password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Password.objects.count(), 2)

    def test_update_password_success(self):
        url = reverse('password_handler', args=[self.service_name])
        response = self.client.post(url, self.password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.password.refresh_from_db()
        self.assertEqual(self.password.password, self.password_data['password'])

    def test_create_password_invalid_data(self):
        url = reverse('password_handler', args=["new_service"])
        response = self.client.post(url, {"password": ""}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordSearchTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.service_name = "yandex"
        self.unknown_service_name = "chocho"
        self.password = Password.objects.create(service_name=self.service_name, password="secure_password")

    def test_search_password_success(self):
        url = reverse('password-search')
        response = self.client.get(url, {'service_name': self.service_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['service_name'], self.service_name)

    def test_search_password_not_found(self):
        url = reverse('password-search')
        response = self.client.get(url, {'service_name': self.unknown_service_name})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_password_missing_parameter(self):
        url = reverse('password-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)