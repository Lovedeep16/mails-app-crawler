from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'keywords/',views.home,name='home'),
	url(r'keyword/$',views.add_key,name='keyword'),
	url(r'all/$',views.jobs,name='jobs'),
	# url(r'jobFilter/(?P<idd>\w+)/$', views.jobFilter, name='jobFilter'),
	url(r'jobFilter/$', views.jobFilter, name='jobFilter'),
	

	url(r'crawl-jobs/$',views.crawl_jobs,name='crawl_jobs'),
	url(r'sync-jobs/$',views.sync_jobs_indeed,name='sync_jobs_indeed'),
	url(r'slack-channels/$',views.slackchaneels,name='slackchaneels'),
	

    ]
