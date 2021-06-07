from leads.models import User
from leads import functions

# print(User.objects.all())
phone_num = '+79058127836'
session_str = '1ApWapzMBuyhm1ynxKkQ4qL58doxHa27-g-aeN80l6kxSLbsPtaD5me6vNwXEXL5oZGBSVBSDap5R0ART95CtPnmVI55mmQGvC9FFyBe4K4YgrFdRLOOmIWRSz3vBXXTgh8XevtEti1COGlTeP600EL257_ni8Ikh7Ns20DoPYchm9rd61zk6HmLwAzHCQ7t0FiyrDPp3TCCkp6lA-VUYZpZ2fORpy_FlR4szTFVfd-XTcROZYtsm_UetS77alp0dQbWHzjTbb1xW0hBPIpE6kPZVHtr9yHK5MDrB2IfCtxw_fhQRAJWEaO3C9ZPRd1KoXjXQJq-9XB2gUzamQ04ddHXtI4fm1z8='

# functions.add_user_session(phone_num, session_str)
# print(functions.get_session_str())
# functions.update_usage_session_str(session_str)
functions.add_session_str(phone_num, session_str)
# print(functions.add_all_users('XfceDevelopment'))
# functions.generate_message_campaign('cryptoinsiderslimited')
# print(functions.get_leads_to_msg(2, 'cryptoinsiderslimited'))

# functions.check_grps()
