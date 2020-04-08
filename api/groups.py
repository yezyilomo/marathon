from django.contrib.auth.models import Group


def create_groups():
    Group.objects.get_or_create(name='admin')
    Group.objects.get_or_create(name='organizer')
    Group.objects.get_or_create(name='client')