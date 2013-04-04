from django.db import models
from django.contrib import admin
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.safestring import mark_safe

import os, subprocess

# This stuff needs to be configured for your server!!!
WEBAPP_DIR = '/Users/ryan/homebrew/Cellar/tomcat/7.0.39/libexec/webapps'
TOMCAT_MANAGER_PATH = 'localhost:8080/manager/text'
TOMCAT_MANAGER = "tomcat" # must have role "manager-text"
TOMCAT_MANAGER_PASSWORD = "secret"

# Don't change this one though
GEOSERVER_WAR_PATH = os.path.join(os.path.dirname(__file__), "geoserver", "geoserver.war")

# ...or these
TOMCAT_DEPLOY_URL = "http://%s:%s@%s/deploy" % (TOMCAT_MANAGER, TOMCAT_MANAGER_PASSWORD, TOMCAT_MANAGER_PATH)
TOMCAT_UNDEPLOY_URL = "http://%s:%s@%s/undeploy" % (TOMCAT_MANAGER, TOMCAT_MANAGER_PASSWORD, TOMCAT_MANAGER_PATH)

class GeoserverInstance(models.Model):
    class Meta:
        ordering = [ "name" ]
        
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return slugify(self.name)
    
    def war_name(self):
        return "%s.war" % self.__unicode__()
    
    def instance_admin_url(self):
        return "http://geoserver.azgs.az.gov/%s/web/" % self.__unicode__()
    
    def instance_admin(self):
        return mark_safe("<a href='%s'>%s</a>" % (self.instance_admin_url(), self.instance_admin_url()))
    
    def pretty_instance_url(self):
        return mark_safe("<a href='%s'>%s</a>" % (self.instance_admin_url(), self.__unicode__()))
    
    def war_destination(self):
        return os.path.join(WEBAPP_DIR, self.war_name())
    
    def copy_war(self):
        """Copy a war file to the WEBAPP_DIR"""
        params = [ "cp", GEOSERVER_WAR_PATH, self.war_destination() ]
        return subprocess.call(params)
    
    def delete_war(self):
        """Remove a war file from the WEBAPP_DIR"""
        params = [ "rm", self.war_destination() ]
        return subprocess.call(params)
    
    def deploy_war(self):
        """POST a war file to Tomcat"""
        params = [
            "curl",
            "--upload-file",
            GEOSERVER_WAR_PATH,
            "%s?path=/%s&update=true" % (TOMCAT_DEPLOY_URL, self.__unicode__()) 
        ]
        return subprocess.call(params)
    
    def undeploy_war(self):
        """Undeploy a WAR file from Tomcat"""
        params = [
            "curl",
            "%s?path=/%s" %(TOMCAT_UNDEPLOY_URL, self.__unicode__())
        ]
        return subprocess.call(params)
    
@receiver(post_save, sender=GeoserverInstance)
def instance_instantiator(sender, instance, created, **kwargs):
    if created:
        out = instance.deploy_war()
        
@receiver(post_delete, sender=GeoserverInstance)
def instance_deinstantiator(sender, instance, **kwargs):
    out = instance.undeploy_war()
    
class GeoserverInstanceAdmin(admin.ModelAdmin):
    list_display = [ '__unicode__', 'instance_admin' ]

admin.site.register(GeoserverInstance, GeoserverInstanceAdmin)

