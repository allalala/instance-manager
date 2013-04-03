from django.shortcuts import render
from models import GeoserverInstance

def home(request):
    return render(request, "instances/home.html", {"instances": GeoserverInstance.objects.all() })
    
    