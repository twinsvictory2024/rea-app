import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from rea_common.models import TimeStampedModel, UUIDModel

class CustomUser(AbstractUser, TimeStampedModel, UUIDModel):
    username = None

    ROLE_CUSTOMER = 'customer'
    ROLE_VENDOR = 'vendor'

    ROLE_CHOICES = [
        (ROLE_CUSTOMER, 'Покупатель'),
        (ROLE_VENDOR, 'Продавец')
    ]

    role = models.CharField(
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER,
        verbose_name="Роль"
    )

    email = models.EmailField(
        max_length=200,
        unique=True,
        null=False,
        blank=False,
    )

    first_name = models.CharField(
        max_length=50
    )

    last_name = models.CharField(
        max_length=50
    )

    patronymic = models.CharField(
        max_length=50
    )

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name[0]}. {self.patronymic[0]}. ({self.email})"

    def __str__(self):
        return self.full_name

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Contact(TimeStampedModel, UUIDModel):
    user = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name='Пользователь'
    )

    city = models.CharField(
        max_length=50,
        verbose_name='Город'
    )

    street = models.CharField(
        max_length=100,
        verbose_name='Улица'
    )

    house = models.CharField(
        max_length=15,
        verbose_name='Дом',
        blank=True
    )

    structure = models.CharField(
        max_length=15,
        verbose_name='Корпус',
        blank=True
    )

    building = models.CharField(
        max_length=15,
        verbose_name='Строение',
        blank=True
    )

    apartment = models.CharField(
        max_length=15,
        verbose_name='Квартира',
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон'
    )

    class Meta:
        verbose_name = 'Контакты пользователя'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'