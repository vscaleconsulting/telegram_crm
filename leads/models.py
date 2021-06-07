from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.utils import timezone

class User(AbstractUser):
    pass


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username


class Lead(models.Model):

    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    username = models.CharField(max_length=20, primary_key=True)
    # agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20)
    grp_username = models.CharField(max_length=255)
    admin = models.IntegerField(default=0)

    # class Meta:
    #     unique_together=(('agent', 'target_grp'),)
    
    def __str__(self):
        return f'{self.username}'


# class InstantMessageCampaign(models.Model):
#     __tablename__ = 'campaign_instant'

#     # id = Column(Integer, index=True)
#     user_id = Column(Integer, primary_key=True)
#     admin_contact_url = Column(String)
#     message = Column(Text)
#     delivered = Column(Boolean, default=False)
#     replied = Column(Boolean, default=False)
#     session_str = Column(Text)
#     reply = Column(Text)


class MessageCampaign(models.Model):
    
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE)
    agent = models.ForeignKey('Agent', on_delete=models.SET_NULL, null=True, blank=True)
    target_grp = models.CharField(max_length=255)
    contacted = models.BooleanField(default=False)
    joined = models.BooleanField(default=False)
    session_used = models.ForeignKey('TGSession', on_delete=models.SET_NULL, null=True, default=None, blank=True)

    class Meta:
        unique_together=(('lead', 'target_grp'),)

    def __str__(self):
        return f'Username: {self.lead.username}, Target grp: {self.target_grp}, Agent: {self.agent}, Contacted: {self.contacted}'

class TGSession(models.Model):

    phone_num = models.CharField(max_length=15)
    session_str = models.TextField(primary_key=True)
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    last_used_on = models.DateField(default=timezone.now)

    class Meta:
        verbose_name_plural = 'TGSessions'
    
    
class TGBot(models.Model):

    bot_token = models.TextField(primary_key=True)
    usage_count = models.IntegerField(default=0)
    last_used_on = models.DateField(default=timezone.now)
    
    
    class Meta:
        verbose_name_plural = 'TGBots'
