from leads.models import User
from leads import functions

# print(User.objects.all())
phone_num = '3123123123123'
session_str = 'aweaweqdasczxczbvfghfgh'

# functions.add_user_session(phone_num, session_str)
# print(functions.get_session_str())
# functions.update_usage_session_str(session_str)
# print(functions.add_all_users('XfceDevelopment'))
# functions.generate_message_campaign('cryptoinsiderslimited')
# print(functions.get_leads_to_msg(2, 'cryptoinsiderslimited'))
functions.check_grps()
