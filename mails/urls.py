from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^all/$',views.home,name='home'),
	url(r'^start-syncing-mails/$',views.sync_mail,name='sync_mail'),
    ]
