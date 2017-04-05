from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse ,HttpResponseRedirect
from django.views.generic import TemplateView ,DetailView
from django.db.models import Q
from myproject import settings
from django.views.generic import FormView, RedirectView
from django.utils.http import is_safe_url
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView


# class LoginView(TemplateView):
# 	template_name = "loginn.html"

def login(request):
# After successful login ,user will be redirect to home page
	return HttpResponseRedirect(reverse('jobs:home'))



def logme(request):
# After method to check valid/registred user
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				auth_login(request,user)
				return HttpResponseRedirect(reverse('jobs:home'))
			else:
				return HttpResponse('You are not Valid')
		else:
			return HttpResponse('Login Again with valid ID and Password')
	return HttpResponse('Login Again with valid ID and Password!!')


def logout(request):
# A method to handle logout
	auth_logout(request)
	return render (request,'loginn.html',{})



# login 					= LoginView.as_view()
	
	
