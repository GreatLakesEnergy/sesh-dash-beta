from django.conf.urls import url
from rest_framework.authtoken import views as authtokenviews
from . import views

urlpatterns = [
            url(r'^$', views.index, name='index'),
            url(r'^dash/([0-9]{1,5})$', views.index, name='index'),
            url(r'^pie/$', views.pie, name='pie'),
            url(r'^linebar/$', views.linebar, name='pie'),
            url(r'^login/$', views.login_user, name='login_user'),
            url(r'^logout/$', views.logout_user, name='logout_user'),
            url(r'^bom-data-points/$', views.BoM_Data_Stream.as_view()),
            url(r'^bom-data-points/(?P<pk>[0-9]+)/$', views.BoM_Data_Detail.as_view()),
            url(r'^api-token-auth/', authtokenviews.obtain_auth_token),
            ]

