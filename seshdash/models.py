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
    longtude = models.FloatField()
    installed_kw = models.IntegerField()
    number_of_pv_strings = models.IntegerField()
    Number_of_panels = models.IntegerField()
    enphase_ID = models.CharField( max_length = 100)
    vrm_ID = models.CharField(max_length = 100)
    battery_bank_capactiy = models.IntegerField()
    has_genset = models.BooleanField()
    has_grid = models.BooleanField()
"""
Data point for PV production at a site
"""
class PV_Production_Point(models.Model):
    site = models.ForeignKey(Sesh_Site)
    time = models.DateTimeField()
    w_production = models.IntegerField()

"""
weather data to overlay with each stite

"""
class Site_Weather_Data(models.Model):
    site = models.ForeignKey(Sesh_Site)
    date = models.DateTimeField('date')
    temp = models.IntegerField()
    uv_index = models.IntegerField()
    condition = models.CharField(max_length=20)



