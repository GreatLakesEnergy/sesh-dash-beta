from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import *
# Register your models here.

class Sesh_SiteAdmin(GuardedModelAdmin):
    list_display = ('site_name','location_city','installed_kw','battery_bank_capacity','comission_date')
    list_filter = ('installed_kw','location_city', 'installed_kw')

class BoM_Data_PointAdmin(GuardedModelAdmin):
    list_display= ('site','time','soc','battery_voltage','AC_input', 'AC_output', 'AC_Load_in', 'AC_Load_out', 'pv_production', 'inverter_state', 'genset_state', 'relay_state','trans',)

class Alert_RuleAdmin(GuardedModelAdmin):
    list_display = ('site','check_field','operator','value')
    list_filter = ('site','operator')

class Sesh_AlertAdmin(GuardedModelAdmin):
    list_display = ('site','alert','date','isSilence')
    list_filter = ('site','isSilence', 'date')

class Sesh_AlertAdmin(GuardedModelAdmin):
    list_display = ('site','alert','date','isSilence')
    list_filter = ('site','isSilence', 'date')

class Daily_Data_PointAdmin(GuardedModelAdmin):
    list_display = ('site','date','daily_pv_yield','daily_power_consumption','daily_battery_charge')


admin.site.register(Sesh_Site,Sesh_SiteAdmin)
admin.site.register(BoM_Data_Point,BoM_Data_PointAdmin)
admin.site.register(Alert_Rule,Alert_RuleAdmin)
#admin.site.register(Sesh_User)
admin.site.register(Sesh_Alert,Sesh_AlertAdmin)
admin.site.register(Daily_Data_Point,Daily_Data_PointAdmin)
