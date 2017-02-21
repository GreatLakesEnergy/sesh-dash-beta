from django.forms import ModelForm
from django import forms
from seshdash.models import Sesh_Site,VRM_Account,Sesh_RMC_Account, Sensor_Node, Alert_Rule, Sesh_User, Status_Card
from seshdash.utils.time_utils import get_timezone_from_geo, localize
from seshdash.utils.model_tools import get_site_sensor_fields_choices

class SiteForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = Sesh_Site
        exclude = ('Delete','vrm_site_id','organisation', 'rmc_account','time_zone','status_card','site_measurements')
        #DateSelectorWidget
        widgets = {'comission_date':forms.DateInput(attrs={'type':'date'})}


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
        exclude = ('Delete','organisation', 'vrm_site_id','rmc_account','time_zone','status_card','site_measurements','vrm_account',)


class SiteRMCForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"


    class Meta:
        model = Sesh_Site
        exclude = ('vrm_account','vrm_site_id', 'organisation', 'import_data', 'status_card', 'site_measurements')
        #DateSelectorWidget
        widgets = {'comission_date':forms.DateInput(attrs={'type': 'date'})}


class SiteVRMForm(ModelForm):
    """
    Form for a vrm site
    """
    class Meta:
        model = Sesh_Site
        exclude = ('vrm_account', 'organisation', 'vrm_site_id', 'status_card', 'site_measurements')



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

class SensorNodeForm(ModelForm):
    """
    Generic Sensor Node Form
    """
    class Meta:
        model = Sensor_Node
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


class StatusCardForm(ModelForm):
    """
    Form to edit the status card of sites
    """
    class Meta:
        model = Status_Card
        exclude = ("site",)
