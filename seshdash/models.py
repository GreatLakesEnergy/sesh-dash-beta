from django.contrib.auth.models import User
from django.db import models
from datetime import timedelta
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib import admin
from geoposition.fields import GeopositionField

# Create your models here.
class VRM_Account(models.Model):
    """
    seperating VRM account for simplicity
    """
    vrm_user_id = models.CharField(max_length=100,default="",primary_key=True)
    vrm_password = models.CharField(max_length=100,default="")
    number_of_sites = models.IntegerField(default=0)

    def __str__(self):
        return self.vrm_user_id


    class Meta:
        verbose_name = "VRM Account"


class Sesh_RMC_Account(models.Model):
    """
    API key used by SESH EMON node to communicate
    """
    #site = models.ForeignKey(Sesh_Site)
    API_KEY = models.CharField(max_length=130,default="")


    class Meta:
        verbose_name = "RMC API Account"



class Sesh_Site(models.Model):
    """
    Model for each PV SESH installed site
    """
    site_name = models.CharField(max_length=100)
    comission_date = models.DateTimeField('date comissioned')
    location_city = models.CharField(max_length = 100)
    location_country = models.CharField(max_length = 100)
    position = GeopositionField(blank=True)
    installed_kw = models.FloatField()
    system_voltage = models.IntegerField()
    number_of_panels = models.IntegerField()
    #enphase_ID = models.CharField( max_length = 100)
    #TODO need to figure a way to show this in admin to automatically populate
    #enphase_site_id = models.IntegerField()

    battery_bank_capacity = models.IntegerField()
    has_genset = models.BooleanField()
    has_grid = models.BooleanField()
    vrm_account = models.ForeignKey(VRM_Account,default=None,blank=True,null=True)
    vrm_site_id = models.CharField(max_length=20,default="",blank=True, null=True)
    rmc_account = models.ForeignKey(Sesh_RMC_Account,max_length=20,default="",blank=True, null=True)

    def __str__(self):
        return self.site_name

    #Row based permissioning using django guardian not every user should be able to see all sites

    class Meta:
        verbose_name = 'Sesh Site'
        verbose_name_plural = 'Sesh Sites'
        permissions = (
            ('view_Sesh_Site', 'View Sesh Site'),
        )

class RMC_status(models.Model):
    """
    Table containing status information for each RMC unit
    """
    rmc = models.ForeignKey(Sesh_RMC_Account)
    ip_address = models.GenericIPAddressField(default=None)
    last_contact = models.DateTimeField(default=None)
    signal_strength = models.IntegerField(default=None)
    data_sent_24h = models.IntegerField(default=None)



class Sesh_User(models.Model):
    #TODO each user will have his her own settings / alarms this needs
    #to be added
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    def __str__(self):
        return self.user.username

    class Meta:
         verbose_name = 'User'
         verbose_name_plural = 'Users'

class Alert_Rule(models.Model):
    """
    Basic Alert rule model
    TODO think about how to make this more power/generic
    """
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
        return "If %s is %s %s" %(self.get_check_field_display(), self.get_operator_display() ,self.value)

    class Meta:
         verbose_name = 'System Alert Rule'
         verbose_name_plural = 'System Alert Rules'


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

class BoM_Data_Point(models.Model):
    """
    BoM data Soc,, battery voltage system voltage etc
    Currently comes from Victron
    """
    #TODO unique together contraing on time and site
    site = models.ForeignKey(Sesh_Site)
    time = models.DateTimeField()
    soc = models.FloatField(default=0)
    battery_voltage = models.FloatField(default=0)
    AC_Voltage_in = models.FloatField(default=0)
    AC_Voltage_out = models.FloatField(default=0)
    AC_input = models.FloatField(default=0)
    AC_output = models.FloatField(default=0)
    AC_output_absolute = models.FloatField(default=0)
    AC_Load_in = models.FloatField(default=0)
    AC_Load_out = models.FloatField(default=0)
    #NEW  victron now tells us pv production
    pv_production = models.FloatField(default=0)
    inverter_state = models.CharField(max_length = 100)
    main_on = models.BooleanField(default=False)
    genset_state = models.IntegerField(default=0)
    #TODO relay will likely need to be it's own model
    relay_state = models.IntegerField(default=0)
    trans = models.IntegerField(default=0)

    def __str__(self):
        return " %s : %s : %s" %(self.time,self.site,self.soc)

    class Meta:
         verbose_name = 'Data Point'
         unique_together = ('site','time')


#TODO Add alert Object to save alerts
class Sesh_Alert(models.Model):
    site = models.ForeignKey(Sesh_Site)
    alert = models.ForeignKey(Alert_Rule)
    point = models.ForeignKey(BoM_Data_Point)
    date = models.DateTimeField()
    isSilence = models.BooleanField()
    alertSent = models.BooleanField()


    # def __str__(self):
    #     return "Some texting text " #  % (self.alert.check_field, self.alert.operator, self.alert.value )

    def __str__(self):
        return "At %s, %s is %s which is %s %s " % (self.site.site_name, self.alert.get_check_field_display(), \
                                      str(getattr(self.point, self.alert.check_field)), \
                                      self.alert.get_operator_display(), \
                                      self.alert.value)


    class Meta:
        verbose_name = 'System Alert'
        verbose_name_plural = 'System Alerts'




class Daily_Data_Point(models.Model):
    """
    Daily aggregate of data points
    """

    site = models.ForeignKey(Sesh_Site)
    daily_pv_yield = models.FloatField(default=0) # Aggregate pv produced that day Kwh
    daily_power_consumption_total = models.FloatField(default=0) # Aggreagate power used that day Kwh
    daily_power_cons_pv = models.FloatField(default=0)
    daily_battery_charge = models.FloatField(default=0) # Amount of charge put in battery
    daily_grid_outage_t = models.FloatField(default=0) # Amount of time the grid was off
    daily_grid_outage_n = models.FloatField(default=0) # Aggregate amount times  grid was off
    daily_grid_usage = models.FloatField(default=0) # Aggregate amount of grid used
    daily_no_of_alerts = models.FloatField(default=0) # Amount of charge put in battery
    date = models.DateTimeField()


    class Meta:
         verbose_name = 'Daily Aggregate Data Point'
         unique_together = ('site','date')



class Trend_Data_Point(models.Model):
    """
    Data that's calculated from individual data points. Used to display an aggregate view
    Overall aggregates
    """
    site = models.ForeignKey(Sesh_Site)
    pv_yield = models.FloatField(default=0) #
    battery_usage = models.FloatField(default=0)
    system_efficiency  = models.FloatField(default=0)
    system_capacity = models.FloatField(default=0)
    battery_efficieny = models.FloatField(default=0)

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


class Site_Weather_Data(models.Model):
    """

    weather data to overlay with each stite

    """
    site = models.ForeignKey(Sesh_Site)
    date = models.DateTimeField('date',unique_for_date=True)
    temp = models.IntegerField()
    condition = models.CharField(max_length=20)
    cloud_cover = models.FloatField()
    sunrise = models.TimeField()
    sunset = models.TimeField()

    class Meta:
        verbose_name = 'Weather Data'
        unique_together = ('site','date')
