from django.db import models
from django.forms import ValidationError

# Create your models here.
class Password(models.Model):
    service_name = models.CharField(max_length=255, unique=True, null=False)
    password = models.CharField(max_length=255, null=False)

    def clean(self):
        # Проверка, что пароль не пустой
        if not self.password.strip():
            raise ValidationError("Password cannot be empty.")

    def save(self, *args, **kwargs):
        # Вызов clean для валидации перед сохранением
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.service_name