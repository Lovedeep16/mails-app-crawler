from django.shortcuts import render, redirect, render_to_response
from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404,redirect
from mails.models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from JobSearch import getAllJobsFromIndeed
from threading import Thread

# @login_required
def home(request):
# Function to handle home page view
	keyword_list = keyword_search.objects.all()
	page = request.GET.get('page', 1)
	paginator = Paginator(keyword_list, 10)
	try:
		keywords = paginator.page(page)
	except PageNotAnInteger:
		keywords = paginator.page(1)
	except EmptyPage:
		keywords = paginator.page(paginator.num_pages)
	return render(request, 'home.html', { 'keywords': keywords })
	
# @login_required
def add_key(request):
# Function to handle adding keywords for search.
  keyword_list = keyword_search.objects.all()
  form=add_keyword(request.POST or None)
  page = request.GET.get('page', 1)
  paginator = Paginator(keyword_list, 10)
  try:
	keywords = paginator.page(page)
  except PageNotAnInteger:
		keywords = paginator.page(1)
  except EmptyPage:
		keywords = paginator.page(paginator.num_pages)
  if form.is_valid():
	# keyword_search.added_by=request.user
	data=form.cleaned_data
	form.save()
	return HttpResponseRedirect('/jobs/keywords/')
  
# @login_required
def jobs(request):
# Function to show all jobs available
	keywords=keyword_search.objects.all()
	jobs_list=job.objects.all()
	page = request.GET.get('page', 1)
	paginator = Paginator(jobs_list, 20)
	try:
		jobs = paginator.page(page)
	except PageNotAnInteger:
		jobs = paginator.page(1)
	except EmptyPage:
		jobs = paginator.page(paginator.num_pages)
	return render(request,"jobs.html",{'jobs':jobs,'keywords':keywords})



# def jobFilter(request,idd):
# 	data = job.objects.filter(keyword=idd)
# 	return render(request,"test.html",{'data':data})
def jobFilter(request):
# Function to filter jobs
	keywords=keyword_search.objects.all()
	jobs=job.objects.all()
	return render(request,"jobs.html",{'jobs':jobs,'keywords':keywords})



class trackThread(Thread):
# Thread created to store keyword, state name , state ID.
	def __init__(self,keyname,statename,portalid,keywordid,stateid):
		self.keyname,self.statename,self.portalid,self.keywordid,self.stateid = keyname,statename,portalid,keywordid,stateid
		super(self.__class__, self).__init__()

	def run(self):
		jobsInstance = getAllJobsFromIndeed(self.keyname,self.statename,self.portalid,self.keywordid,self.stateid)
		jobsInstance.getAllJobs()


def sync_jobs_indeed(request):
# Function created to get all jobs from indeed
	if request.method == 'POST':
		keyword = request.POST['keyword']
		portals = request.POST['portal']
		state = request.POST['state']

		keywordinsta = keyword_search.objects.get(pk=int(keyword))
		portalinsta = portal.objects.get(pk=int(portals))
		statesinsta = allUsStates.objects.get(pk=int(state))
		
		t = trackThread(str(keywordinsta.keyword_name),str(statesinsta.statename),portals,keyword,state)
		t.start()

		return HttpResponse('Crawling Started !!! ')
	else:
		return HttpResponse("IT S GET")


def crawl_jobs(request):
# Function crawls jobs on the basis of given keyword and state
	keywords = keyword_search.objects.all()
	postals = portal.objects.all()
	allstates = allUsStates.objects.all()
	return render(request,"crawljobs.html",{'portal':postals,'keywords':keywords,"allstates":allstates})

# @login_required
def slackchaneels(request):
# Function to display all Slack channels
	slackch = slack_channel.objects.all()
	return render(request,"slack_channels.html",{"slack":slackch})






