from django.forms import ModelForm
from django import forms
from seshdash.models import Sesh_Site,VRM_Account,Sesh_RMC_Account
from seshdash.utils.time_utils import get_timezone_from_geo, localize

class SiteForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = Sesh_Site
        exclude = ('Delete','vrm_account','vrm_site_id','rmc_account','time_zone','status_card','site_measurements',)
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



class SiteRMCForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"


#    def clean(self):
#        """
#        Add timezone based on location
#        """
#        cleaned_data = super(SiteRMCForm, self).clean()
#        pos = cleaned_data.get('position')
#        timezone = get_timezone_from_geo(pos[0], pos[1])
#        self.cleaned_data['time_zone'] = timezone
#        return cleaned_data


    class Meta:
        model = Sesh_Site
        exclude = ('Delete','vrm_account','vrm_site_id','rmc_account','import_data','time_zone')
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
