from django.db import models

# Create your models here.

"""
Model for each PV SESH installed site
"""
class Sesh_Site(models.Model):

    site_name = models.CharField(max_length=100)
    comission_date = models.DateTimeField('date comissioned')
    location_city = models.CharField(max_length = 100)
    location_country = models.CharField(max_length = 100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    installed_kw = models.FloatField()
    number_of_pv_strings = models.IntegerField()
    Number_of_panels = models.IntegerField()
    enphase_ID = models.CharField( max_length = 100)
    vrm_user_id = models.CharField(max_length=100)
    vrm_password = models.CharField(max_length=100)
    battery_bank_capacity = models.IntegerField()
    has_genset = models.BooleanField()
    has_grid = models.BooleanField()

    class Meta:
        permissions = (
            ('view_Sesh_Site', 'View Sesh Site'),
        )

"""
Data point for PV production at a site
"""
class PV_Production_Point(models.Model):
    site = models.ForeignKey(Sesh_Site)
    time = models.DateTimeField()
    w_production = models.IntegerField()

"""
BoM data Soc,, battery voltage system voltage etc
"""
class BoM_Data_Point(models.Model):
    site = models.ForeignKey(Sesh_Site)
    time = models.DateTimeField()
    soc = models.FloatField()
    battery_voltage = models.FloatField()
    AC_input = models.FloatField()
    AC_output = models.FloatField()
    AC_Load_in = models.FloatField()
    AC_Load_out = models.FloatField()
    inverter_state = models.CharField(max_length = 100)
    genset_state = models.CharField(max_length = 100)
#TODO relay will likely need to be it's own model
    relay_state = models.CharField(max_length = 100)

"""
weather data to overlay with each stite

"""
class Site_Weather_Data(models.Model):
    site = models.ForeignKey(Sesh_Site)
    date = models.DateTimeField('date',unique_for_date=True)
    temp = models.IntegerField()
    condition = models.CharField(max_length=20)
    cloud_cover = models.FloatField()
    sunrise = models.TimeField()
    sunset = models.TimeField()



