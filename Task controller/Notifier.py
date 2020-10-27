import json
import datetime
import locale
import shutil
import os
import pathlib
from enum import Enum, auto

import configparser
import jpholiday


class NotifyType(Enum):
    MONTHLY = auto()
    WEEKLY = auto()
    DAILY = auto()
    DATE = auto()


class NotifyFix:
    def __init__(self, prefix, suffix, infix=None):
        self.prefix = prefix
        self.suffix = suffix
        self.infix = infix


class NotifyTiming(Enum):
    MORNING = "朝"
    DAYTIME = "昼"
    EVENING = "夕"
    NIGHT = "夜"
    NONE = ""
    ALL = auto


class Datetime:
    def __init__(self, date_obj=datetime.date.today()):
        # locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
        locale.setlocale(locale.LC_TIME, 'ja_JP')
        self.date_obj = date_obj

    def get_month_str(self):
        return self.date_obj.strftime('%m')

    def get_date_str(self):
        return self.date_obj.strftime('%d')

    def get_weekday_str(self):
        return self.date_obj.strftime('%a')

    @staticmethod
    def get_prev_date(date):
        td = datetime.timedelta(days=-1)
        return date + td

    @staticmethod
    def is_holiday(date):
        if date.weekday() >= 5 or jpholiday.is_holiday(date):
            return True
        else:
            return False

    def generate_holiday_until_today(self):
        date = self.get_prev_date(datetime.date.today())
        while self.is_holiday(date):
            yield date
            date = self.get_prev_date(date)


class Prefix:
    def __init__(self, date_obj, notify_timing):
        self.terminator = "_"
        self.notify_fix_dict = {
            NotifyType.MONTHLY: NotifyFix("★毎月", "日"),
            NotifyType.WEEKLY:  NotifyFix("★毎週", "曜"),
            NotifyType.DAILY:   NotifyFix("★毎日", ""),
            NotifyType.DATE:    NotifyFix("★", "")
        }
        self.timing_list = []
        self.set_timing_list(notify_timing)
        self.set_infix_list(date_obj)

    def set_infix_list(self, date_obj):
        datetime_manager = Datetime(date_obj)
        month = datetime_manager.get_month_str()
        date = datetime_manager.get_date_str()
        weekday = datetime_manager.get_weekday_str()
        # set
        self.notify_fix_dict[NotifyType.MONTHLY].infix = date
        self.notify_fix_dict[NotifyType.WEEKLY].infix = weekday
        self.notify_fix_dict[NotifyType.DAILY].infix = ""
        self.notify_fix_dict[NotifyType.DATE].infix = month + date

    def set_timing_list(self, notify_timing):
        timing_list = []
        if notify_timing != NotifyTiming.ALL:
            timing_list.append(notify_timing)
        else:
            for timing in NotifyTiming:
                if timing is not NotifyTiming.ALL:
                    timing_list.append(timing)
        self.timing_list = timing_list

    def get_prefix_list(self):
        pref_list = []
        pref_type_list = []
        for notify_type, notify_fix in self.notify_fix_dict.items():
            prefix = notify_fix.prefix
            infix = notify_fix.infix
            suffix = notify_fix.suffix
            for timing in self.timing_list:
                pref_list.append(prefix + infix + suffix + timing.value + self.terminator)
                pref_type_list.append(notify_type)
        return pref_list, pref_type_list


class ConfigParser:
    def __init__(self):
        self.config_ini = configparser.ConfigParser()
        self.config_ini.read("config.ini", encoding='utf-8')

    @staticmethod
    def trim_path_str(path_str):
        return path_str.replace('\n', '').replace('\\', '/')

    def get_path_str(self, section, option):
        return self.trim_path_str(self.config_ini.get(section, option))

    def get_path_list(self, section, option):
        tmp_path_str = self.get_path_str(section, option)
        tmp_path_str = json.loads(tmp_path_str)
        if not isinstance(tmp_path_str, list):
            tmp_path_str = [tmp_path_str]
        return [pathlib.Path(path_str) for path_str in tmp_path_str]


class Notifier:
    def __init__(self, src_path_list, dst_path_list, date_obj=datetime.date.today(), notify_timing=NotifyTiming.ALL):
        self.src_list = src_path_list
        if len(self.src_list) == 0:
            self.src_list = list(self.src_list)

        self.dst_list = dst_path_list
        if len(self.dst_list) == 0:
            self.dst_list = list(self.dst_list)

        self.notify_timing = notify_timing
        self.date = date_obj

    def set_notify_timing(self, notify_timing):
        self.notify_timing = notify_timing

    def set_date(self, date_obj):
        self.date = date_obj

    def notify_todo(self):
        prefix = Prefix(self.date, self.notify_timing)
        prefix_list, prefix_type = prefix.get_prefix_list()
        for src_path in self.src_list:
            for dst_path in self.dst_list:
                for prefix, pre_type in zip(prefix_list, prefix_type):
                    for src_file in src_path.glob('**/' + prefix + '*.*'):
                        shutil.copy(src_file, dst_path)
                        if pre_type is NotifyType.DATE:
                            os.remove(src_file)



def get_notifier_from_config():
    parser = ConfigParser()
    # get src path
    src = parser.get_path_list("SRC", "routine")
    src = src + parser.get_path_list("SRC", "user")

    # get dst path
    dst = parser.get_path_list("DST", "next")
    return Notifier(src, dst)


notifier = get_notifier_from_config()
notifier.notify_todo()
