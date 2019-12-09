from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        try:
            email = self.normalize_email(email)
            validate_email(email)
        except ValidationError as e:
            raise ValidationError(e)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password)

        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
