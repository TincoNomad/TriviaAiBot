import uuid
from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    ROLES = [
        ('user', _('Regular User')),
        ('admin', _('Administrator'))
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_verified = models.BooleanField(_('Email Verified'), default=False)
    login_attempts = models.IntegerField(_('Login Attempts'), default=0)
    role = models.CharField(_('Role'), max_length=20, choices=ROLES, default='user')
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='created_users', verbose_name=_('Created By'))

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
