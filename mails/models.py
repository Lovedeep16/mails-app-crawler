from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
import datetime
# Create your models here.



class mail_id(models.Model):
# model to store Email-ID,Passwords related to mail accounts.
	email_ID			= models.EmailField(max_length=300)
	password			= models.CharField(max_length=300)
	last_updated		= models.DateTimeField(null=True,auto_now_add=True)

	def __str__(self):
		return self.email_ID


class all_mails(models.Model):
# model to store email data under various headers.
	mail_UID			= models.CharField(max_length=50)
	mail_KEY			= models.CharField(max_length=50)
	mail_to             = models.ForeignKey(mail_id)
	mail_from			= models.EmailField(max_length=300)
	mail_title		    = models.CharField(max_length=200)
	mail_discription	= models.CharField(max_length=5000)
	date_recieved       = models.CharField(max_length=200)
	sync_time			= models.CharField(max_length=200)
	last_updated		= models.CharField(max_length=200)
	status 				= models.CharField(max_length=50,default='1')

	def __str__(self):
		return self.mail_from
	



