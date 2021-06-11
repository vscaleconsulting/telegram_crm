from django.contrib import admin
from .models import Agent, Lead, User, MessageCampaign, TGBot, TGSession, Category


# class TGBotAdmin(admin.ModelAdmin):

admin.site.register(User)
admin.site.register(Agent)
admin.site.register(Lead)
admin.site.register(MessageCampaign)
admin.site.register(TGBot)
admin.site.register(TGSession)
admin.site.register(Category)