from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from leads.functions import check_grps, receive_msgs

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(receive_msgs)
    scheduler.add_job(check_grps, 'interval', seconds=1800)
    scheduler.start()