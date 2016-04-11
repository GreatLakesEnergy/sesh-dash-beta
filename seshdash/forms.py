from django.forms import ModelForm
from django import forms
from seshdash.models import Sesh_Site,VRM_Account,Sesh_RMC_Account

class SiteForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = Sesh_Site
        exclude = ('Delete','vrm_account','vrm_site_id','rmc_account')
        #DateSelectorWidget
        widgets = {'comission_date':forms.DateInput()}

class SiteRMCForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"


    class Meta:
        model = Sesh_Site
        exclude = ('Delete','vrm_account','vrm_site_id','rmc_account','import_data')
        #DateSelectorWidget
        widgets = {'comission_date':forms.DateInput()}


class RMCForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = Sesh_RMC_Account
        exclude = ('Delete',)


class VRMForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = VRM_Account
        exclude = ('number_of_sites',)
        widgets = {
                  'vrm_password': forms.PasswordInput(),
                   }

