from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Sesh_Site
# Register your models here.

class Sesh_SiteAdmin(GuardedModelAdmin):
    list_display = ('site_name','location_city','installed_kw','battery_bank_capacity','comission_date')

admin.site.register(Sesh_Site,Sesh_SiteAdmin)
