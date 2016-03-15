from django.conf.urls import url
from rest_framework.authtoken import views as authtokenviews
from . import views

urlpatterns = [
            url(r'^$', views.index, name='index'),
            url(r'^dash/([0-9]{1,5})$', views.index, name='index'),
            url(r'^linebar/$', views.linebar, name='linebar'),
            url(r'^login/$', views.login_user, name='login_user'),
            #url(r'^login\?next=/$', views.login_user, name='login_user_2'),
            url(r'^logout/$', views.logout_user, name='logout_user'),
            url(r'^import-site/$', views.import_site, name='import_site'),
            url(r'^create-site/$', views.create_site, name='create_site'),
            url(r'^bom-data-points/$', views.BoM_Data_Stream.as_view()),
            url(r'^bom-data-points/(?P<pk>[0-9]+)/$', views.BoM_Data_Detail.as_view()),
            url(r'^api-token-auth/', authtokenviews.obtain_auth_token),
            url(r'^users/$', views.UserList.as_view()),
            url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
            url(r'^get-alert-data', views.display_alert_data),
            url(r'^silence-alert', views.silence_alert),
            ]

