from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^home/$', 'instances.views.home')
)