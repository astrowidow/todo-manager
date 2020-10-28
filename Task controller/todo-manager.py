import time

import schedule
import Notifier


def set_notify_schedule():
    # tag
    # daily_tag = "daily_update"

    # set
    config_parser = Notifier.ConfigParser()
    # morning
    schedule.every().day.at(config_parser.get_option_str("TIME", "morning_notification")).do(
        Notifier.notify_morning_todo
    )
    # daytime
    schedule.every().day.at(config_parser.get_option_str("TIME", "daytime_notification")).do(
        Notifier.notify_daytime_todo
    )
    # evening
    schedule.every().day.at(config_parser.get_option_str("TIME", "evening_notification")).do(
        Notifier.notify_evening_todo
    )


# set daily schedule
parser = Notifier.ConfigParser()
schedule.every().day.at("01:00").do(set_notify_schedule)
set_notify_schedule()

# process starting up
if Notifier.Datetime.is_before_working_time():
    Notifier.process_start_up()

while True:
    schedule.run_pending()
    time.sleep(900)
