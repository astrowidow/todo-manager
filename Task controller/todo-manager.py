import time

import schedule
import Notifier


def set_notify_schedule():
    # tag
    # daily_tag = "daily_update"

    # set
    config_parser = Notifier.ConfigParser()
    # morning
    morning_time = config_parser.get_option_str("TIME", "morning_notification")
    Notifier.debug_print("[setting] morning notification time: ", morning_time)
    schedule.every().day.at(morning_time).do(
        Notifier.notify_morning_todo
    )
    # daytime
    day_time = config_parser.get_option_str("TIME", "daytime_notification")
    Notifier.debug_print("[setting] daytime notification time: ", day_time)
    schedule.every().day.at(day_time).do(
        Notifier.notify_daytime_todo
    )
    # evening
    evening_time = config_parser.get_option_str("TIME", "evening_notification")
    Notifier.debug_print("[setting] evening notification time: ", evening_time)
    schedule.every().day.at(evening_time).do(
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
