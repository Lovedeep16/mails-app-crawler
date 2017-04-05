from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',views.login,name='login'),
    url(r'logme/',views.logme,name='logme'),
    url(r'logout/',views.logout,name='logout'),
    ]

