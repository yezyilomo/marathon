from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import serializers
from django_restql.mixins import DynamicFieldsMixin
from django_restql.serializers import NestedModelSerializer
from django_restql.fields import NestedField

from api import views
from .models import (
    User, Category, Sponsor, Marathon, Payment
)


ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('organizer', 'Organizer'),
    ('client', 'client')
)


class UserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    role = serializers.ChoiceField(ROLE_CHOICES, write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            'id', 'url', 'username', 'email', 'password', 'role', 'phone',
            'date_joined', 'full_name', 'gender', 'is_active', 'payments',
            'is_admin', 'is_organizer', 'is_client'
        )
        read_only_fields = (
            'date_joined', 'payments', 'is_admin', 'is_organizer', 'is_client'
        )

    def validate_role(self, role):
        request = self.context.get('request')
        user = request.user
        if role == 'admin' and not (user.is_authenticated and user.is_admin):
            raise serializers.ValidationError(
                "Can't assign this role to user if you've not logged in as admin.",
                "Value error"
            )
        return role


class CategorySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id', 'url', 'name', 'price', 'currency', 'marathon'
        )

    def validate_marathon(self, marathon):
        request = self.context.get('request')
        user = request.user
        if marathon.organizer != user or not user.is_admin or user.role != 'admin':
            raise serializers.ValidationError(
                {"category": f"Can't use the marathon which you do not organize."},
                "Value error"
            )
        return marathon


class SponsorSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = (
            'id', 'url', 'name', 'marathon'
        )

    def validate_marathon(self, marathon):
        request = self.context.get('request')
        user = request.user
        if marathon.organizer != user or not user.is_admin or user.role != 'admin':
            raise serializers.ValidationError(
                {"category": f"Can't use the marathon which you do not organize."},
                "Value error"
            )
        return marathon


class MarathonSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    organizer = NestedField(UserSerializer, read_only=True, fields=['full_name'])
    sponsors = NestedField(SponsorSerializer, many=True, required=False, fields=['name'],
        create_ops=['create'], update_ops=['create', 'remove', 'update'])
    categories = NestedField(CategorySerializer, required=True, exclude=['marathon'],
        create_ops=['create'], update_ops=['create', 'remove', 'update'])

    class Meta:
        model = Marathon
        fields = (
            'id', 'url', 'name', 'theme', 'organizer', 'sponsors', 
            'categories', 'start_date', 'end_date',
        )

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data.update({'organizer': user})
        return super().create(validated_data)


class PaymentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            'id', 'url', 'marathon', 'category', 'user', 'validation_date', 'status'
        )
        read_only_fields = (
            'user', 'status', 'validation_date'
        )

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data.update({'user': user})
        validated_data.update({'status': 'UNPAID'})
        marathon = validated_data.get('marathon', None)
        category = validated_data.get('category', None)

        if category not in marathon.categories:
            raise serializers.ValidationError(
                {"category": f"Such marathon does not have a category with `id={category.pk}`"},
                "Value error"
            )
        return super().create(validated_data)
