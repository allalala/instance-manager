from django.shortcuts import render
from models import GeoserverInstance

def home(request):
    return render(request, "instances/home.html", {"intances": GeoserverInstance.objects.all() })
    
    