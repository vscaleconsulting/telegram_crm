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



def get_session(random=False):
    
    """Gets the least used session

    Args:
        random (bool, optional): gives random session if True. Defaults to False
        
    Returns:
        TGSession.object: TGSession queryset
    """
    sessions = TGSession.objects.order_by('last_used_on', 'usage_count')
    if random:
        session = sessions[randint(1, (len(sessions)-1) // 2)]
    else:
        session = sessions.first()
    session.last_used_on = timezone.now()
    session.save()
    return session


def get_session_str():
    """Returns the least used session string

    Returns:
        str: session string
    """

    return TGSession.objects.order_by('last_used_on', 'usage_count').first().session_str1


def get_bot_token():
    """Returns the least used bot token

    Returns:
        str: bot token
    """
    return TGBot.objects.order_by('last_used_on', 'usage_count').first().bot_token


def add_session_str(phone_num, session_str):
    """Adds new session to the database

    Args:
        phone_num (int): phone number of the session
        session_str (str): session string
    """
    try:
        TGSession.objects.create(
            phone_num='+' + phone_num.replace(' ', '').lstrip('+'), session_str=session_str)
    except Exception:
        pass

def assign_new_session(user):
    """Assigns New session to the agent

    Args:
        user (User.object): Agent Model Object
    """
    agent = Agent.objects.get(user=user)
    session = get_session()
    if session == agent.session:
        session = get_session(True)
    agent.session = session
    agent.save()

def get_otp(user):
    """Fetch the otp for the number assigned

    Args:
        user (User.object): User Model Object

    Returns:
        str: OTP for the session if successful else 'Retry'
    """
    agent = Agent.objects.get(user=user)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient(StringSession(agent.session.session_str), api_id, api_hash, loop=loop)
    client.connect()
    messages = client.get_messages(777000, 1)
    client.disconnect()
    if messages:
        return re.findall('[0-9]+', messages[0].message)[0]
    return 'Retry'


# def check(ph_dict, ret):
#     """Helper function for update_active_numbers function
#     Args:
#         ph_dict (dict): dict {<phone>: <session str>}
#         ret (bool): True if phone number is active else False
#     """
#     for ph, sid in ph_dict.items():
#         try:
#             tg_client = TGClient(StringSession(sid), api_id=api_id, api_hash=api_hash)
#             tg_client.connect()
#             ret[ph] = True
#         except:
#             ret[ph] = False
    

def add_bot_token(bot_token):
    """Add bot token to the database

    Args:
        bot_token (str): bot token
    """
    TGBot.objects.create(bot_token=bot_token)


def update_usage_session_str(session_str):
    """Update the usage count of the session

    Args:
        session_str (str): session string
    """
    session = TGSession.objects.get(session_str=session_str)
    session.usage_count += 1
    session.last_used_on = timezone.now()
    session.save()


def update_usage_bot_token(bot_token):
    """Update the usage count of the bot token

    Args:
        bot_token (str): bot token
    """
    session = TGBot.objects.get(bot_token=bot_token)
    session.usage_count += 1
    session.last_used_on = timezone.now()
    session.save()


def add_all_users(group):
    """Adds Leads to the database from a source group

    Args:
        group (str): name of the telegram group

    Returns:
        [int]: Number of leads generated
    """
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
                          telegram_id=user.id,
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
    """Generates campaign messages for the users in source_grp to add them to the target group

    Args:
        target_grp (str): target group username
        source_grp (str, optional): source group username. Defaults to None.
    """
    if source_grp is None:
        leads = Lead.objects.all()
    else:
        leads = Lead.objects.filter(grp_username=source_grp).all()

    campaign = [MessageCampaign(lead=lead, target_grp=target_grp) for lead in leads]

    MessageCampaign.objects.bulk_create(campaign, ignore_conflicts=True)


def get_leads_to_msg(agent_id, target_grp=None, entries=10):
    """returns a list of MessageCampaign.object containing leads to message

    Args:
        agent_id (int): agent id
        target_grp (str, optional): target group username. Defaults to None.
        entries (int, optional): number of leads to get. Defaults to 10.

    Returns:
        list: list of MessageCampaign.object containing leads to message
    """
    agent = Agent.objects.get(user_id = agent_id)
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
    """Mark the Leads as Contacted in the database

    Args:
        id [int]: pk of the lead
    """
    entry = MessageCampaign.objects.get(id=id)
    entry.contacted = True
    entry.session_used = entry.agent.session
    entry.save()


def check_grps():
    """Updates the joined column to True in the database if a contacted user joins the target group
    """
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


def send_message(sender_session, receiver, message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # sess_str = '1ApWapzMBu4bPq_KDVCy4vb0Y0V9IOjCcK3dQkKmIp3CL3adfUpeKznS5mzyYsM8rmwvlrWKAY8XwH1N3WqrHYfMNpXxaKuh-km9NUCwCpU9DeAbr07B3HfkypPzC7RM_mJIQzLB0h4CngnCwNJEFXva-AUlXPhcI2QLWgEaBVfce-Uys9UZ9ETL1QoMbZrkZzHKDa_aB3s2McSkkc9H4wTJHzfHpQYyH79AWABpCGNBtbb3sgrb9Qg5X29pdS41m5XhQWnEllJomISAPs88r2HsWFo_RtBq6_sEbrZ6fqDleE5BIKAaepYPCAY_t1ZFC5qlMXil8x_R6G0rf7aCYL0mrO6stmAQ='

    client = TelegramClient(StringSession(sender_session),
                            1868530, "edf7d1e794e0b4a5596aa27c29d17eba", loop=loop)

    client.connect()
    try:
        client.send_message(receiver, message)
        client.disconnect()
        return True
    except Exception:
        client.disconnect()
        return False


def get_user_id(username):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sess_str = '1ApWapzMBu4bPq_KDVCy4vb0Y0V9IOjCcK3dQkKmIp3CL3adfUpeKznS5mzyYsM8rmwvlrWKAY8XwH1N3WqrHYfMNpXxaKuh-km9NUCwCpU9DeAbr07B3HfkypPzC7RM_mJIQzLB0h4CngnCwNJEFXva-AUlXPhcI2QLWgEaBVfce-Uys9UZ9ETL1QoMbZrkZzHKDa_aB3s2McSkkc9H4wTJHzfHpQYyH79AWABpCGNBtbb3sgrb9Qg5X29pdS41m5XhQWnEllJomISAPs88r2HsWFo_RtBq6_sEbrZ6fqDleE5BIKAaepYPCAY_t1ZFC5qlMXil8x_R6G0rf7aCYL0mrO6stmAQ='

    client = TelegramClient(StringSession(sess_str),
                            1868530, "edf7d1e794e0b4a5596aa27c29d17eba", loop=loop)

    client.connect()
    try:
        entity = client.get_entity('@' + username)
    except ValueError:
        client.disconnect()
        return -1
    except Exception:
        client.disconnect()
        return -2
    client.disconnect()
    return entity.id