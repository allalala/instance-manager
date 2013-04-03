from django.db import models
from django.contrib import admin
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.safestring import mark_safe

import os, subprocess

# This needs to be configured for your server!!!
WEBAPP_DIR = '/Users/ryan/homebrew/Cellar/tomcat/7.0.39/libexec/webapps'

# Don't change this one
GEOSERVER_WAR_PATH = os.path.join(os.path.dirname(__file__), "geoserver", "geoserver.war")
 
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
    
@receiver(post_save, sender=GeoserverInstance)
def instace_instantiator(sender, instance, created, **kwargs):
    if created:
        instance.copy_war()
        
@receiver(post_delete, sender=GeoserverInstance)
def instance_deinstantiator(sender, instance, **kwargs):
    instance.delete_war()
    
class GeoserverInstanceAdmin(admin.ModelAdmin):
    list_display = [ '__unicode__', 'instance_admin' ]

admin.site.register(GeoserverInstance, GeoserverInstanceAdmin)

