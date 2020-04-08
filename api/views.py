from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import ProtectedError
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django_restql.mixins import EagerLoadingMixin
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated
)
from drf_guard.operators import And, Or, Not
from drf_guard.permissions import HasRequiredGroups, HasRequiredPermissions

from .permissions import (
    IsAllowedUser, IsCategoryOwner, IsSponsorOwner, IsMarathonOwner,
    IsPaymentOwner, IsAdminUser
)
from .models import (
    User, Category, Sponsor, Marathon, Payment
)
from .serializers import (
    UserSerializer, CategorySerializer, SponsorSerializer, 
    MarathonSerializer, PaymentSerializer
)


def fields(*args):
    """ 
    Specify the field lookup that should be performed in a filter call.
    Default lookup is exact.
    """
    lookup_fields = {}
    for field in args:
        if isinstance(field, str):
            lookup_fields.update({field: ['exact']})
        elif isinstance(field, dict):
            lookup_fields.update(field)
        else:
            raise Exception("Invalid formating of lookup field")

    return lookup_fields


class HandleProtectedErrorMixin():
    def error_response(self, error):
        error_args = map(lambda arg: str(arg), error.args)
        msg = ", ".join(error_args)
        data = {'detail': msg}
        return_status = status.HTTP_403_FORBIDDEN
        return Response(data=data, status=return_status)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ProtectedError as e:
            return self.error_response(e)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ProtectedError as e:
            return self.error_response(e)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as e:
            return self.error_response(e)


class LoginUser(ObtainAuthToken):
    """API endpoint that allows users to login and obtain auth token."""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, context={'request': request})
        data = {
            'token': token.key,
            **user_serializer.data
        }
        return Response(data)


class RegisterUser(ObtainAuthToken):
    """API endpoint that allows users to register and obtain auth token."""
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        username = data.pop("username")
        email = data.pop("email", "")
        password = data.pop("password")
        role = data.pop("role")
        user = User.objects.create_user(username, email, password)
        user.save()
        user.groups.add(Group.objects.get(name=role))
        token, created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, context={'request': request})
        data = {
            'token': token.key,
            **user_serializer.data
        }
        return Response(data)


class UserViewSet(HandleProtectedErrorMixin, viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited."""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (HasRequiredGroups, HasRequiredPermissions)
    http_method_names = ['get', 'put', 'patch', 'delete']
    groups_and_permissions = {
         'GET': {
             'list': {
                 'groups': ['admin'],
                 'permissions': [IsAuthenticated]
             },
             'retrieve': {
                 'groups': ['__all__'],
                 'permissions': [IsAuthenticated, IsAllowedUser, Or, IsAdminUser]
             },
         },
         'PUT': {
             'groups': ['__all__'],
             'permissions': [IsAuthenticated, IsAllowedUser, Or, IsAdminUser]
         },
         'PATCH': {
             'groups': ['__all__'],
             'permissions': [IsAuthenticated, IsAllowedUser, Or, IsAdminUser]
         },
         'DELETE': {
             'groups': ['__all__'],
             'permissions': [IsAuthenticated, IsAllowedUser, Or, IsAdminUser]
         }
    }

    filter_fields = fields(
        'id', {'email': ['exact', 'icontains']}, 
        {'username': ['exact', 'icontains']}
    )


class CategoryViewSet(HandleProtectedErrorMixin, viewsets.ModelViewSet):
    """API endpoint that allows categories to be viewed or edited."""
    queryset = Category.objects.all().order_by('-id')
    serializer_class = CategorySerializer
    permission_classes = (HasRequiredGroups, HasRequiredPermissions)
    groups_and_permissions = {
         'GET': {
             'list': {
                 'groups': ['admin'],
                 'permissions': [IsAuthenticated]
             },
             'retrieve': {
                 'groups': ['admin', Or, 'organizer'],
                 'permissions': [IsAuthenticated, IsCategoryOwner, Or, IsAdminUser],
             },
         },
         'POST': {
             'groups': ['admin', Or, 'organizer'],
             'permissions': [IsAuthenticated]
         },
         'PUT': {
             'groups': ['admin', Or, 'organizer'],
             'permissions': [IsAuthenticated, IsCategoryOwner, Or, IsAdminUser]
         },
         'PATCH': {
             'groups': ['admin', Or, 'organizer'],
             'permissions': [IsAuthenticated, IsCategoryOwner, Or, IsAdminUser]
         },
         'DELETE': {
             'groups': ['admin', Or, 'organizer'],
             'permissions': [IsAuthenticated, IsCategoryOwner, Or, IsAdminUser]
         }
    }

    filter_fields = fields(
        'id', 
    )


class SponsorViewSet(HandleProtectedErrorMixin, viewsets.ModelViewSet):
    """API endpoint that allows sponsors to be viewed or edited."""
    queryset = Sponsor.objects.all().order_by('-id')
    serializer_class = SponsorSerializer
    permission_classes = (HasRequiredGroups, HasRequiredPermissions)
    groups_and_permissions = {
         'GET': {
             'list': {
                 'groups': ['admin'],
                 'permissions': [IsAuthenticated]
             },
             'retrieve': {
                 'groups': ['admin', Or, 'organizer'],
                 'permissions': [IsAuthenticated, IsSponsorOwner, Or, IsAdminUser]
             },
         },
         'POST': {
             'groups': ['admin', Or, 'organizer'],
             'permissions': [IsAuthenticated]
         },
         'PUT': {
             'groups': ['admin', Or, 'organizer'],
             'permissions': [IsAuthenticated, IsSponsorOwner, Or, IsAdminUser]
         },
         'PATCH': {
             'groups': ['admin', Or, 'organizer'],
             'permissions': [IsAuthenticated, IsSponsorOwner, Or, IsAdminUser]
         },
         'DELETE': {
             'groups': ['admin', Or, 'organizer'],
             'permissions': [IsAuthenticated, IsSponsorOwner, Or, IsAdminUser]
         }
    }

    filter_fields = fields(
        'id', 
    )


class MarathonViewSet(HandleProtectedErrorMixin, EagerLoadingMixin, viewsets.ModelViewSet):
    """API endpoint that allows marathons to be viewed or edited."""
    queryset = Marathon.objects.all().order_by('-id')
    serializer_class = MarathonSerializer
    permission_classes = (HasRequiredGroups, HasRequiredPermissions)
    groups_and_permissions = {
         'GET': {
             'list': {
                 'groups': ['admin', Or, 'organizer', Or, 'client'],
                 'permissions': [IsAuthenticated]
             },
             'retrieve': {
                 'groups': ['admin', Or, 'organizer', Or, 'client'],
                 'permissions': [IsAuthenticated]
             },
         },
         'POST': {
             'groups': ['admin', Or, 'organizer'],
             'permissions': [IsAuthenticated]
         },
         'PUT': {
             'groups': ['admin', Or, 'organizer'],
             'permissions': [IsAuthenticated, IsMarathonOwner, Or, IsAdminUser]
         },
         'PATCH': {
             'groups': ['admin', Or, 'organizer'],
             'permissions': [IsAuthenticated, IsMarathonOwner, Or, IsAdminUser]
         },
         'DELETE': {
             'groups': ['admin', Or, 'organizer'],
             'permissions': [IsAuthenticated, IsMarathonOwner, Or, IsAdminUser]
         }
    }

    select_related = {'organizer': 'organizer'}
    prefetch_related = {'sponsors': 'sponsors', 'categories': 'categories'}

    filter_fields = fields(
        'id'
    )


class PaymentViewSet(HandleProtectedErrorMixin, viewsets.ModelViewSet):
    """API endpoint that allows payments to be viewed or edited."""
    queryset = Payment.objects.all().order_by('-id')
    serializer_class = PaymentSerializer
    permission_classes = (HasRequiredGroups, HasRequiredPermissions)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_admin:
            return queryset
        elif user.is_organizer:
            return queryset.filter(marathon__organizer=user)
        return queryset.filter(user=user)

    groups_and_permissions = {
         'GET': {
             'list': {
                 'groups': ['admin', Or, 'organizer', Or, 'client'],
                 'permissions': [IsAuthenticated]
             },
             'retrieve': {
                 'groups': ['admin', Or, 'organizer', Or, 'client'],
                 'permissions': [IsAuthenticated, IsPaymentOwner, Or, IsAdminUser]
             },
         },
         'POST': {
             'groups': ['admin', Or, 'client'],
             'permissions': [IsAuthenticated]
         },
         'PUT': {
             'groups': ['admin'],
             'permissions': [IsAuthenticated]
         },
         'PATCH': {
             'groups': ['admin'],
             'permissions': [IsAuthenticated]
         },
         'DELETE': {
             'groups': ['admin', Or, 'client'],
             'permissions': [IsAuthenticated, IsPaymentOwner, Or, IsAdminUser]
         }
    }

    filter_fields = fields(
        'id', 
    )