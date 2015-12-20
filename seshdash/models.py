from django.contrib.auth.models import User
from django.db import models
from datetime import timedelta
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
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
    #enphase_ID = models.CharField( max_length = 100)
    #TODO need to figure a way to show this in admin to automatically populate
    #enphase_site_id = models.IntegerField()
    vrm_user_id = models.CharField(max_length=100)
    vrm_password = models.CharField(max_length=100)
    vrm_site_id = models.CharField(max_length=20)
    battery_bank_capacity = models.IntegerField()
    has_genset = models.BooleanField()
    has_grid = models.BooleanField()

    def __str__(self):
        return self.site_name

    #Row based permissioning using django guardian not every user should be able to see all sites
    class Meta:
        permissions = (
            ('view_Sesh_Site', 'View Sesh Site'),
        )


class Sesh_User(models.Model):
    #TODO each user will have his her own settings / alarms this needs
    #to be added
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    def __str__(self):
        return self.user.username


class Alert_Rule(models.Model):
    OPERATOR_CHOICES = (
        ("eq" , "equals"),
        ("lt" , "less than"),
        ("gt" , "greater than"),
        )
    FIELD_CHOICES = (('battery_voltage','battery voltage'),
                     ('soc','System State of Charge'),
                     ('AC_output','AC Loads'),
                     ('pv_production','Solar Energy Produced'),
                     ('main_on','Grid Availible'),
                     ('genset_state','Generator on'),
                )

    site = models.ForeignKey(Sesh_Site)
    check_field = models.CharField(choices=FIELD_CHOICES,max_length=100)
    value = models.FloatField()
    operator = models.CharField(max_length=2,
                                      choices=OPERATOR_CHOICES,
                                      default="lt")
    send_mail = models.BooleanField(default=True)
    #TODO a slug field with the field operator and value info can be added
    #TODO this is vastly incomplete!! fields need to be mapable and chooices need to exist
    def __str__(self):
        return "site:%s rule:[%s '%s' %s]" %(self.site.site_name,self.check_field,self.operator,self.value)

#TODO Add alert Object to save alerts
class Sesh_Alert(models.Model):
    site = models.ForeignKey(Sesh_Site)
    alert = models.ForeignKey(Alert_Rule)
    date = models.DateTimeField()
    isSilence = models.BooleanField()
    alertSent = models.BooleanField()


"""
Data point for PV production at a site from pv panels.
Currently comes form enphase

REMMOVING because enphase API SUCS and  victron now provides us with this data
"""
# class PV_Production_Point(models.Model):
    # site = models.ForeignKey(Sesh_Site)
    # time = models.DateTimeField()
    # w_production = models.IntegerField()
    # wh_production = models.IntegerField()
    # data_duration = models.DurationField(default=timedelta())

    # class Meta:
     #    unique_together = ('site','time')

"""
BoM data Soc,, battery voltage system voltage etc
Currently comes from Victron
"""
class BoM_Data_Point(models.Model):
    #TODO unique together contraing on time and site
    site = models.ForeignKey(Sesh_Site)
    time = models.DateTimeField()
    soc = models.FloatField()
    battery_voltage = models.FloatField()
    AC_Voltage_in = models.FloatField(default=-0)
    AC_Voltage_out = models.FloatField(default=0)
    AC_input = models.FloatField()
    AC_output = models.FloatField()
    AC_Load_in = models.FloatField()
    AC_Load_out = models.FloatField()
    #NEW  victron now tells us pv production
    pv_production = models.FloatField(default=0)
    inverter_state = models.CharField(max_length = 100)
    main_on = models.BooleanField(default=False)
    genset_state = models.CharField(max_length = 100)
#TODO relay will likely need to be it's own model
    relay_state = models.CharField(max_length = 100)
    trans = models.IntegerField(default=0)

    def __str__(self):
        return " %s : %s : %s" %(self.time,self.site,self.soc)

    class Meta:
          unique_together = ('site','time')
"""
TODO removing for now as it's breaking celery object creation
    owner = models.ForeignKey('auth.User', related_name='snippets')
    highlighted = models.TextField()

    def save(self, *args, **kwargs):
        site = self.site
        time = self.time
        soc = self.soc
        battery_voltage = self.battery_voltage
        AC_input = self.AC_input
        AC_output = self.AC_output
        AC_Load_in = self.AC_Load_in
        AC_Load_out = self.AC_Load_out
        inverter_state = self.inverter_state
        genset_state = self.genset_state
        relay_state = self.relay_state
        owner = self.owner
        super(BoM_Data_Point, self).save(*args, **kwargs)

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)
"""

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

    class Meta:
        unique_together = ('site','date')
