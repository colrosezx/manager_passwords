from django.db import models
from django.forms import ValidationError

class Password(models.Model):
    service_name = models.CharField(max_length=255, unique=True, null=False)
    password = models.CharField(max_length=255, null=False)

    def clean(self):
        if not self.password.strip():
            raise ValidationError({"password": "Password cannot be empty."})
