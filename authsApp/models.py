from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class UserProfile(models.Model):
# model to store Users
	user 				= models.OneToOneField(User)
	

	def __str__(self):
		return self.user.username
