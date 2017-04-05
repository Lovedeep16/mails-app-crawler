from __future__ import unicode_literals
from django.db import models
import datetime
from django.core.validators import URLValidator
from mails.models import *

# Create your models here.




class portal(models.Model):
# model to store Portal
	portal_name			= models.CharField(max_length=100)
	portal_link 		= models.TextField(validators=[URLValidator()])
	last_updated		= models.DateTimeField(null=True,auto_now_add=True)

	def __str__(self):
		return self.portal_name

class allUsStates(models.Model):
# model to store all US states
	statename = models.CharField(max_length=500)
	statekey = models.CharField(max_length=400)


sendonSlack =(
				('0','0 '),
				('1','1'),
     		) 

ChannelType = (
				('mail','mail'),
				('job','job'),

	)

class DenywordsList(models.Model):
	denywords 			= models.CharField(max_length=1000,verbose_name='Deny Keywords  (Eg: Contract,W2,Fulltime )')

	def __str__(self):
		return self.denywords

class slack_channel(models.Model):
# model to store various Slack Channels
	slack_name   		= models.CharField(max_length=100,verbose_name = 'Slack Channel Name #')
	channel_ID			= models.CharField(max_length=500,verbose_name = 'Slack Webhooks ID')
	channeltype 		= models.CharField(max_length=50,choices=ChannelType)
	last_updated		= models.DateTimeField(null=True,auto_now_add=True)

 
	def __str__(self):
		return self.slack_name


class keyword_search(models.Model):
	keyword_name		= models.CharField(max_length=50,unique=True)
	last_updated		= models.DateTimeField(null=True,auto_now_add=True)
	slack_channel_con 	= models.ForeignKey(slack_channel)
	deny_filters 		= models.ForeignKey(DenywordsList,default='')


	def __str__(self):
		return self.keyword_name




class job(models.Model):
	job_title 			= models.CharField(max_length=100)
	job_discription     = models.CharField(max_length=4000)
	company_name 		= models.CharField(max_length=50,default='',null=True,blank=True)
	company_email		= models.EmailField(max_length=100,default='',null=True,blank=True)
	portal_id			= models.ForeignKey(portal)
	send_on_slack		= models.CharField(max_length=20,choices=sendonSlack)
	keyword 			= models.ForeignKey(keyword_search)
	last_updated		= models.CharField(max_length=400,default='')
	job_url 			= models.CharField(max_length=1000)
	state 				= models.ForeignKey(allUsStates)

	def __str__(self):
		return self.job_title


