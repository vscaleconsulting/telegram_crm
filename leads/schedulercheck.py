from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from leads.functions import check_grps

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_grps, 'interval', seconds=60)
    scheduler.start()