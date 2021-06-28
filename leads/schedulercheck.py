from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from leads.functions import check_grps

def start():
    scheduler = BackgroundScheduler()

    # Starts background process for updating the database every 1800 secs.
    scheduler.add_job(check_grps, 'interval', seconds=1800)
    scheduler.start()