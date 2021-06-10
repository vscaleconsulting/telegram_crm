import re
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
# from TelegramBot import models
from telethon.tl.types import ChannelParticipantsAdmins
from random import randint
from .config import *
import asyncio
from .models import TGSession, TGBot, Lead, MessageCampaign, Agent
from django.utils import timezone


def get_session():
    session = TGSession.objects.order_by('last_used_on', 'usage_count').first()
    session.last_used_on = timezone.now()
    session.save()
    return session


def get_session_str():
    return TGSession.objects.order_by('last_used_on', 'usage_count').first().session_str


def get_bot_token():
    return TGBot.objects.order_by('last_used_on', 'usage_count').first().bot_token


def add_session_str(phone_num, session_str):
    TGSession.objects.create(
        phone_num='+' + phone_num.replace(' ', '').lstrip('+'), session_str=session_str)


def add_bot_token(bot_token):
    TGBot.objects.create(bot_token=bot_token)


def update_usage_session_str(session_str):
    session = TGSession.objects.get(session_str=session_str)
    session.usage_count += 1
    session.last_used_on = timezone.now()
    session.save()


def update_usage_bot_token(bot_token):
    session = TGBot.objects.get(bot_token=bot_token)
    session.usage_count += 1
    session.last_used_on = timezone.now()
    session.save()


def add_all_users(group):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # client = TelegramClient(StringSession(
    #     '1ApWapzMBuyhm1ynxKkQ4qL58doxHa27-g-aeN80l6kxSLbsPtaD5me6vNwXEXL5oZGBSVBSDap5R0ART95CtPnmVI55mmQGvC9FFyBe4K4YgrFdRLOOmIWRSz3vBXXTgh8XevtEti1COGlTeP600EL257_ni8Ikh7Ns20DoPYchm9rd61zk6HmLwAzHCQ7t0FiyrDPp3TCCkp6lA-VUYZpZ2fORpy_FlR4szTFVfd-XTcROZYtsm_UetS77alp0dQbWHzjTbb1xW0hBPIpE6kPZVHtr9yHK5MDrB2IfCtxw_fhQRAJWEaO3C9ZPRd1KoXjXQJq-9XB2gUzamQ04ddHXtI4fm1z8='),
    #     api_id, api_hash, loop=loop)
    client = TelegramClient(StringSession(get_session_str()), api_id, api_hash, loop=loop)
    client.connect()
    # print(StringSession.save(client.session))
    users = client.get_participants(group)
    admins = client.get_participants(group, filter=ChannelParticipantsAdmins)
    client.disconnect()

    db_leads_list = [u.username for u in Lead.objects.filter(grp_username=group).all()]
    leads = []
    for user in users:
        if user.username in db_leads_list or user.bot or user.status is None or user.username is None:
            continue
        leads.append(Lead(username=user.username,
                          first_name=user.first_name,
                          last_name=user.last_name,
                          status=str(type(user.status)).split(
                              '.')[-1][10:-2],
                          grp_username=group,
                          admin=0))

    Lead.objects.bulk_create(leads, ignore_conflicts=True)

    i = 1
    for admin in admins:
        if admin.bot or admin.status is None or admin.username is None:
            continue
        req_admin = Lead.objects.filter(
            username=admin.username, grp_username=group).first()
        if req_admin is None:
            continue
        req_admin.admin = i
        req_admin.save()
        i += 1

    return len(users)


def generate_message_campaign(target_grp, source_grp=None):
    if source_grp is None:
        leads = Lead.objects.all()
    else:
        leads = Lead.objects.filter(grp_username=source_grp).all()
    campaign = []
    for lead in leads:
        campaign.append(MessageCampaign(lead=lead, target_grp=target_grp))

    MessageCampaign.objects.bulk_create(campaign, ignore_conflicts=True)


def get_leads_to_msg(agent_id, target_grp=None, entries=10):
    print(agent_id)
    agent = Agent.objects.get(user_id = agent_id)
    print(agent)
    if target_grp is None:
        not_contacted = MessageCampaign.objects.filter(agent=agent, contacted=False).all()
    else:
        not_contacted = MessageCampaign.objects.filter(agent=agent, contacted=False, target_grp=target_grp).all()

    print(not_contacted)
    entries -= len(not_contacted)
    if entries <= 0:
        return not_contacted

    if target_grp is None:
        campaigns = MessageCampaign.objects.filter(agent=None).all()[:entries]
    else:
        campaigns = MessageCampaign.objects.filter(agent=None, target_grp=target_grp).all()[:entries]

    if len(campaigns) < entries and target_grp is not None:
        print('here')
        generate_message_campaign(target_grp)
        campaigns = MessageCampaign.objects.filter(agent=None, target_grp=target_grp).all()[:entries]

    for campaign in campaigns:
        campaign.agent = agent
        campaign.save()

    return list(not_contacted) + list(campaigns)


def mark_contacted(id):
    entry = MessageCampaign.objects.get(id=id)
    entry.contacted = True
    entry.session_used = entry.agent.session
    entry.save()


def check_grps():
    print('Updating Database...')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient(StringSession(
        '1ApWapzMBuyhm1ynxKkQ4qL58doxHa27-g-aeN80l6kxSLbsPtaD5me6vNwXEXL5oZGBSVBSDap5R0ART95CtPnmVI55mmQGvC9FFyBe4K4YgrFdRLOOmIWRSz3vBXXTgh8XevtEti1COGlTeP600EL257_ni8Ikh7Ns20DoPYchm9rd61zk6HmLwAzHCQ7t0FiyrDPp3TCCkp6lA-VUYZpZ2fORpy_FlR4szTFVfd-XTcROZYtsm_UetS77alp0dQbWHzjTbb1xW0hBPIpE6kPZVHtr9yHK5MDrB2IfCtxw_fhQRAJWEaO3C9ZPRd1KoXjXQJq-9XB2gUzamQ04ddHXtI4fm1z8='),
        api_id, api_hash, loop=loop)
    # client = TelegramClient(StringSession(get_session_str()), api_id, api_hash, loop=loop)
    client.connect()
    
    grps = MessageCampaign.objects.order_by().values('target_grp').distinct()
    members = {}
    
    for grp in grps:
        users = client.get_participants(grp['target_grp'])
        members[grp['target_grp']] = users
    
    client.disconnect()
    
    leads = MessageCampaign.objects.filter(contacted=True)
    for lead in leads:
        if lead.lead_id in members[lead.target_grp]:
            lead.joined = True
            lead.save()
    
