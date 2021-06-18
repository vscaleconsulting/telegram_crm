from django.contrib import admin, messages
from django.utils.translation import ngettext
from .models import Agent, Lead, User, MessageCampaign, TGBot, TGSession, Category


class MessageCampaignAdmin(admin.ModelAdmin):
    actions = ['mark_replied']

    @admin.action(description='Mark selected leads as replied')
    def mark_replied(self, request, queryset):
        updated = queryset.update(category='Replied')
        self.message_user(request, ngettext(
            '%d lead was successfully marked as replied.',
            '%d leads were successfully marked as replied.',
            updated,
        ) % updated, messages.SUCCESS)
        
        

# class TGBotAdmin(admin.ModelAdmin):


admin.site.register(User)
admin.site.register(Agent)
admin.site.register(Lead)
admin.site.register(MessageCampaign, MessageCampaignAdmin)
admin.site.register(TGBot)
admin.site.register(TGSession)
# admin.site.register(Category)
