from django.db import models
from django.conf import settings
from django.db.models import ProtectedError
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female')
)

MARATHON_CATEGORY_NAME_CHOICES = (
    ('FULL', 'Full'),
    ('HALF', 'Half')
)

CURRENCY_CHOICES = (
    ('USD', 'USD'),
    ('TZS', 'TZS')
)

PAYMENT_STATUS_CHOICES = (
    ('PAID', 'Paid'),
    ('UNPAID', 'Unpaid'),
    ('CANCELLED', 'Cancelled')
)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class User(AbstractUser):
    full_name = models.CharField(max_length=256, blank=True)
    phone = models.CharField(max_length=256, blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, choices=GENDER_CHOICES)

    @property
    def is_admin(self):
        return super().is_staff or self.groups.filter(name='admin').exists()

    @property
    def is_organizer(self):
        return self.groups.filter(name='organizer').exists()

    @property
    def is_client(self):
        return self.groups.filter(name='client').exists()


class Marathon(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    theme = models.TextField(blank=True, null=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marathons')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, choices=MARATHON_CATEGORY_NAME_CHOICES)
    price = models.FloatField()
    currency = models.CharField(max_length=256, choices=CURRENCY_CHOICES)
    marathon = models.ForeignKey(Marathon, on_delete=models.CASCADE, related_name='categories')


class Sponsor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)
    marathon = models.ForeignKey(Marathon, on_delete=models.CASCADE, related_name='sponsors')


class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    marathon = models.ForeignKey(Marathon, on_delete=models.CASCADE, related_name='payments')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    status = models.CharField(max_length=256, choices=PAYMENT_STATUS_CHOICES)
    validation_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, using=None, keep_parents=False):
        if self.status != 'PAID':
            return super().delete(using=using, keep_parents=keep_parents)
        raise ProtectedError("Can't delete paid payment", self)