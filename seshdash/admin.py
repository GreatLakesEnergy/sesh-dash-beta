from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import Sesh_Site, BoM_Data_Point, Sesh_Alert , Alert_Rule, Sesh_User
# Register your models here.

class Sesh_SiteAdmin(GuardedModelAdmin):
    list_display = ('site_name','location_city','installed_kw','battery_bank_capacity','comission_date')

class BoM_Data_PointAdmin(GuardedModelAdmin):
    list_display= ('site','time','soc','battery_voltage','AC_input', 'AC_output', 'AC_Load_in', 'AC_Load_out', 'pv_production', 'inverter_state', 'genset_state', 'relay_state','trans',)

class Alert_RuleAdmin(GuardedModelAdmin):
    list_display = ('site','check_field','operator','value')

admin.site.register(Sesh_Site,Sesh_SiteAdmin)
admin.site.register(BoM_Data_Point,BoM_Data_PointAdmin)
admin.site.register(Alert_Rule,Alert_RuleAdmin)
#admin.site.register(Sesh_User)
admin.site.register(Sesh_Alert)
