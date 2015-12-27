from django.forms import ModelForm
from seshdash.models import Sesh_Site,VRM_Account

class SiteForm(ModelForm):
    class Meta:
        model = Sesh_Site
        exclude = ('VRM_Account',)


class VRMForm(ModelForm):
    class Meta:
        model = VRM_Account
        exclude = ('',)

