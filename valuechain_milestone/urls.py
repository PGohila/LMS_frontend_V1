from django.urls import path
from .views import *

urlpatterns = [
    path('valuechain_setups',valuechain_setups,name='valuechain_setups'),
    path('get-valuechain-data/', get_valuechain_data, name='get_valuechain_data'), # js function
    path('valuechainsetup_edit/<pk>',valuechainsetup_edit,name='valuechainsetupedit'),
    path('valuechainsetup_delete/<pk>',valuechainsetup_delete,name='valuechainsetupdelete'),
    path('disply_valuechain',disply_valuechain,name='disply_valuechain'),
    path('create_milestone/<pk>',create_milestone,name='create_milestone'),
    path('milestonesetup_edit/<pk>',milestonesetup_edit,name='milestonesetup_edit'),
    path('milestonesetup_delete/<pk>',milestonesetup_delete,name='milestonesetupdelete'),
    path('add_milestonestages/<pk>',add_milestonestages,name='add_milestonestages'),
    path('activities_edit/<pk>',activities_edit,name='activities_edit'),
    path('activities_delete/<pk>',activities_delete,name='activities_delete'),
    # path('loan_list',loan_list,name='loan_list'),
 
]