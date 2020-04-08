from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views as auth_view

from api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'sponsors', views.SponsorViewSet)
router.register(r'marathons', views.MarathonViewSet)
router.register(r'payments', views.PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', views.LoginUser.as_view()),
    path('register/', views.RegisterUser.as_view())
]