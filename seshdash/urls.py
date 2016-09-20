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
            url(r'^create-site/$', views.handle_create_site, name='create_site'),
            url(r'^bom-data-points/$', views.BoM_Data_Stream.as_view()),
            url(r'^bom-data-points/(?P<pk>[0-9]+)/$', views.BoM_Data_Detail.as_view()),
            url(r'^api-token-auth/', authtokenviews.obtain_auth_token),
            #url(r'^users/$', views.UserList.as_view()),
            #url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
            url(r'^silence-alert', views.silence_alert),
            url(r'^get-alerts', views.get_alerts),
            url(r'^get-alert-data', views.display_alert_data),
            url(r'^notifications',views.get_notifications_alerts),
            url(r'^get-latest-bom-data', views.get_latest_bom_data),
            url(r'^search', views.search),
            url(r'^historical_data', views.historical_data),
            url(r'^graphs', views.graphs),
            url(r'^edit_site$',views.edit_site, name='edit_site'),
            url(r'^edit_site/([0-9]{1,5})$',views.edit_site),
            url(r'^manage_sites$', views.site_add_edit, name='manage_sites'),
            url(r'^alert_rules$', views.settings_alert_rules, name='manage_alert_rules'),
            url(r'^site_alert_rules/([0-9]{1,7})$', views.site_alert_rules, name='site_alert_rules'),
            url(r'^edit_alert_rule/([0-9]{1,7})$', views.edit_alert_rule, name='edit_alert_rule'),
            url(r'^delete_alert_rule/([0-9]{1,7})$', views.delete_alert_rule, name='delete_alert_rule'),
            url(r'^add_rmc_site$',views.add_rmc_site, name='add_rmc_site'),
            url(r'^add_rmc_account/([0-9]{1,5})$', views.add_rmc_account, name='add_rmc_account'),
            url(r'^get_rmc_config$', views.get_rmc_config, name='get_rmc_config'),
            url(r'^user_notifications$', views.user_notifications, name='user_notifications'),
            ]

