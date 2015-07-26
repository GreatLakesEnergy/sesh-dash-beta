from django.contrib import admin

from .models import Sesh_Site
# Register your models here.

class Sesh_SiteAdmin(admin.ModelAdmin):
    list_display = ('site_name','location_city')

admin.site.register(Sesh_Site,Sesh_SiteAdmin)
