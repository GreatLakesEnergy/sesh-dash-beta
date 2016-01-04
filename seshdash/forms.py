from django.forms import ModelForm
from seshdash.models import Sesh_Site,VRM_Account

class SiteForm(ModelForm):
    class Meta:
        model = Sesh_Site
        exclude = ('Delete',)


class VRMForm(ModelForm):
    class Meta:
        model = VRM_Account
        exclude = ('number_of_sites',)


