from django.contrib import admin
from .models import *
# Register your models here.

# admin.site.register(portal)
admin.site.register(job)
admin.site.register(slack_channel)
admin.site.register(keyword_search)
admin.site.register(DenywordsList)

admin.site.register(allUsStates)