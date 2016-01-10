from django.forms import ModelForm
from seshdash.models import Sesh_Site,VRM_Account

class SiteForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = Sesh_Site
        exclude = ('Delete',)


class VRMForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = VRM_Account
        exclude = ('number_of_sites',)


