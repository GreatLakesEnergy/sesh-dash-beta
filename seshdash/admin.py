from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import *
# Register your models here.

@admin.register(Sesh_Site)
class Sesh_SiteAdmin(GuardedModelAdmin):
    list_display = ('site_name','location_city','installed_kw','battery_bank_capacity','comission_date')
    list_filter = ('installed_kw','location_city', 'installed_kw')

@admin.register(BoM_Data_Point)
class BoM_Data_PointAdmin(GuardedModelAdmin):
    list_display= ('site','time','soc','battery_voltage','AC_input', 'AC_output', 'AC_Load_in', 'AC_Load_out', 'pv_production', 'inverter_state', 'genset_state', 'relay_state','trans',)

@admin.register(Alert_Rule)
class Alert_RuleAdmin(GuardedModelAdmin):
    list_display = ('site','check_field','operator','value')
    list_filter = ('site','operator')

@admin.register(Sesh_Alert)
class Sesh_AlertAdmin(GuardedModelAdmin):
    list_display = ('site','alert','date','isSilence')
    list_filter = ('site','isSilence', 'date')

@admin.register(Daily_Data_Point)
class Daily_Data_PointAdmin(GuardedModelAdmin):
    list_display = ('site','date','daily_pv_yield','daily_power_consumption_total','daily_battery_charge')

@admin.register(VRM_Account)
class VRM_AccountAdmin(GuardedModelAdmin):
    pass

@admin.register(Sesh_RMC_Account)
class RMC_AccountAdmin(GuardedModelAdmin):
    list_display = ('site','api_key','api_key_numeric')
    pass

@admin.register(Sesh_Organisation)
class Organisation(GuardedModelAdmin):
    list_display = ('group', 'slack_token')
    pass

@admin.register(Sesh_User)
class SeshUser(GuardedModelAdmin):
    list_display = ('user','phone_number','on_call')
    list_filter = ('on_call',)
    pass

@admin.register(Slack_Channel)
class SlackAlertChannel(GuardedModelAdmin):
    list_display = ('name','organisation')
    pass


@admin.register(RMC_status)
class RMCStatus(GuardedModelAdmin):
    list_display = ('site','ip_address','time','minutes_last_contact')
    list_filter = ('site',)
    pass


