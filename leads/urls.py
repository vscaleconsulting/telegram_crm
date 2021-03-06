from django.urls import path
from . import views
from .views import leads_list, LeadsListView, update_db, repopulate


urlpatterns = [
    path('', LeadsListView.as_view(), name='lead-list'),
    path('update/<int:msg_id>', update_db, name='update-db'),
    path('repopulate', repopulate, name='repopulate-list')
]