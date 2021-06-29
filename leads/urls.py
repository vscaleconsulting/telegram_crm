from django.urls import path
from . import views
from .views import ConversationView, leads_list, LeadsListView, update_db, repopulate, category_update


urlpatterns = [
    path('', leads_list, name='lead-list'),
    path('update/<int:msg_id>', update_db, name='update-db'),
    path('repopulate', repopulate, name='repopulate-list'),
    path('category/<lead_id>', category_update, name='category-update'),
    path('conversation/<int:messagecampaign_id>/<int:peer_id>', ConversationView.as_view(), name='conversation')

]