from django.forms import ModelForm
from seshdash.models import Sesh_Site

class SiteForm(ModelForm):
    class Meta:
        model = Sesh_Site
        exclude = ()


