import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.conf import settings


class UserProfileManager(BaseUserManager):
    """ Manager for user profiles """

    def create_user(self, email, name, password=None,mobile=None) -> "UserProfile":
        """Create a new user profile"""
        if not email:
            raise ValueError('Invalid Email')
        # normalize email, convert second half to lowercase
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser):
    """ Database model for users in system """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=13, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self) -> str:
        """
        Retrieve full name of user
        :return: str
        """
        return self.name

    def get_short_name(self) -> str:
        """
        Retrieve full name of user
        :return: str
        """
        return self.name

    def __str__(self) -> str:
        """
        Return String representation of User
        :return: str
        """
        return f"Email: {self.email}, Name:{self.name}"

class Debt(models.Model):
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='to_user')
    amount = models.DecimalField(default=0,max_digits=9,decimal_places=2)

    def __str__(self):
        return f'{self.to_user.name} owes {self.amount} to {self.from_user.name}'


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=255, unique=True)
    debts = models.ManyToManyField(Debt, null=True)
    members = models.ManyToManyField(UserProfile)

    def __str__(self):
        return f'{self.group_name}'


class ExpenseUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    paid_share = models.DecimalField(default=0,max_digits=9,decimal_places=2)
    owed_share = models.DecimalField(default=0,max_digits=9,decimal_places=2)
    net_balance = models.DecimalField(default=0,max_digits=9,decimal_places=2)
    def __str__(self):
        return f'{self.user.name} lent {self.owed_share} net_balance {self.net_balance}'


class Expense(models.Model):
    name = models.CharField(max_length=255, unique=False)
    expense_group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, null=True, db_constraint=False)
    description = models.CharField(max_length=255)
    payment = models.BooleanField(default=False)
    amount = models.DecimalField(default=0,max_digits=9,decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    repayments = models.ManyToManyField(Debt)
    users = models.ManyToManyField(ExpenseUser)
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f'{self.name}'