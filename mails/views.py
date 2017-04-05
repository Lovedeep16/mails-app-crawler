from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from mails.models import *
from jobs.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mailsObject import getMailsReport
from threading import Thread
from django.contrib.auth.decorators import login_required
class trackThread(Thread):
# Thread created to synchronize th mails
	def __init__(self):
		super(self.__class__, self).__init__()

	def run(self):
		mailsInstance = getMailsReport()
		mailsInstance.get_all()
		print "Syncing MAIL Started"

# @login_required
def home(request):
# Function created to show all mails.
	mailss=all_mails.objects.all()
	page = request.GET.get('page', 1)
	paginator = Paginator(mailss, 20)
	try:
		jobs = paginator.page(page)
	except PageNotAnInteger:
		jobs = paginator.page(1)
	except EmptyPage:
		jobs = paginator.page(paginator.num_pages)
	return render(request,"all_mails.html",{'mails':jobs})

def sync_mail(request):
# Function created to synchronize mails.
	t = trackThread()
	t.start()
	print "IAM IN SYNc MAIL"
	return HttpResponse("Mail Syncing Started !!!")
	
