from django.forms import ModelForm
from django import forms
from seshdash.models import Sesh_Site,VRM_Account,Sesh_RMC_Account, Sensor_EmonTh, \
                            Sensor_EmonTx, Sensor_BMV, Sensor_EmonPi, Alert_Rule, Sesh_User
from seshdash.utils.time_utils import get_timezone_from_geo, localize

class SiteForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = Sesh_Site
        exclude = ('Delete','vrm_site_id','rmc_account','time_zone','status_card','site_measurements')
        #DateSelectorWidget
        widgets = {'comission_date':forms.DateInput()}


#    def clean(self,**kwargs):
#        """
#        add timezone based on location
#        """
#       # super(SiteForm, self).save(**kwargs)
#        cleaned_data = super(SiteForm, self).clean()
#        pos =self.cleaned_data.get('position')
#        timezone = get_timezone_from_geo(pos[0], pos[1])
#        self.instance.time_zone = timezone
#        self.instance.comission_date = localize(self.instance.comission_date, timezone)
#
#        #super(SiteForm, self).save(**kwargs)
#        return cleaned_data

class EditSiteForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model= Sesh_Site
        exclude = ('Delete','vrm_site_id','rmc_account','time_zone','status_card','site_measurements','vrm_account',)


class SiteRMCForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"


    class Meta:
        model = Sesh_Site
        exclude = ('vrm_account','vrm_site_id','import_data', 'status_card', 'site_measurements')
        #DateSelectorWidget
        widgets = {'comission_date':forms.DateInput()}


class SiteVRMForm(ModelForm):
    """ 
    Form for a vrm site 
    """
    class Meta:
        model = Sesh_Site
        exclude = ('vrm_account', 'vrm_site_id', 'status_card', 'site_measurements')



class RMCForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = Sesh_RMC_Account
        exclude = ('Delete','site',)


class VRMForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = VRM_Account
        exclude = ('number_of_sites',)
        widgets = {
                  'vrm_password': forms.PasswordInput(),
                   }


class SensorEmonThForm(ModelForm):
     """
     Emonth form
     """
     class Meta:
         model = Sensor_EmonTh
         exclude = ('site',)

class SensorEmonTxForm(ModelForm):
    """
    Emontx form
    """
    class Meta:
        model = Sensor_EmonTx
        exclude = ('site',)


class SensorBMVForm(ModelForm):
    """
    Bmv form
    """
    class Meta:
        model = Sensor_BMV
        exclude = ('site',)


class SensorEmonPiForm(ModelForm):
    """
    Form for the emon pi senosr
    """
    class Meta:
        model = Sensor_EmonPi
        exclude = ('site',)


class AlertRuleForm(ModelForm):
    """
    Form for the Alert Rule 
    Model
    """
    class Meta:
        model = Alert_Rule
        fields = ('check_field', 'operator', 'value',)

class SeshUserForm(ModelForm):
    """
    Form for the Sesh User
    """
    class Meta:
        model = Sesh_User
        fields = ("username", "is_org_admin", "email", "password",  "phone_number", "on_call", "send_mail", "send_sms")
