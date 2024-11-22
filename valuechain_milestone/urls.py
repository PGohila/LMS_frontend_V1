from django.urls import path
from .views import *

urlpatterns = [
    path('valuechain_setups',valuechain_setups,name='valuechain_setups'),
    
]