import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Tuple, Union

# TODO. 把 assert 改为自定义错误类型

timeline_t = [('beginTime', datetime), ("endTime", datetime), ("event", dict)]

WEEK = ["Mon", "Tue", "Wed", "Thr", "Fri", "Sat", "Sun"]
lower_week = [x.lower() for x in WEEK]

DAY = ["Today", "Tomorrow"]
lower_day = [x.lower() for x in DAY]

message = {
    "ongoing": [
        "博士，您还有许多事情需要处理。现在还不能休息哦。",
        "ドクター、終わってない仕事がたくさんありますから、まだ休んじゃだめですよ。"
    ],
    "waiting": [
        "咻，应该可以小小休息一下了吧。",
        "ふう、これで少しは休めますね。"
    ],
    "finish": [
        "博士，您工作辛苦了。",
        "ドクター、お仕事お疲れ様です。"
    ]
}


def getTimeFromStr(time_str: str) -> Union[bool, datetime]:
    while True:
        try: time = datetime.strptime(time_str, "%H:%M")
        except: pass
        else: break
        try: time = datetime.strptime(time_str, "%H:%M:%S")
        except: pass
        else: break
        return False
    return time


def loadConfig(config_path="timeline.json", config=None):
    if config:
        if type(config) == str:
            time_schedule = json.loads(config)
            if type(time_schedule) != dict:
                raise RuntimeError(f"type(time_schedule) is `{type(time_schedule)}`, but should be `dict`.")
        elif type(config) == dict:
            time_schedule = config
        else:
            raise RuntimeError(f"type(config) is `{type(config)}`, but should be `str` or `dict`.")
    else:
        try:
            with open(config_path, "r", encoding="utf8") as f:
                time_schedule = json.load(f)
            assert type(time_schedule) == dict
        except:
            time_schedule = {}
    if "week" in time_schedule:
        assert type(time_schedule["week"]) == list
    else:
        time_schedule["week"] = [[] for x in range(7)]
    if "day" in time_schedule:
        assert type(time_schedule["day"]) == dict
    else:
        time_schedule["day"] = {}
    return time_schedule


def dumpConfig(time_schedule, config_path="timeline.json"):
    if config_path:
        with open(config_path, "w", encoding="utf8") as f:
            json.dump(time_schedule, f, indent=2, ensure_ascii=False)


def accept() -> bool:
    choice = 'n'
    while True:
        choice = input("(y/n)").lower()
        if choice in ['y', 'n']: break
    return choice == 'y'


def getDateFromParams(params: str, now=datetime.now()) -> Tuple[datetime, Optional[str]]:
    if not params:
        return (now, None)
    if type(params) != str:
        raise TypeError(f"type(params) is `{type(params)}`, but should be `str`.")
    params = params.split(' ', 1)
    param = params[0].lower()
    if param in lower_day:
        day_index = lower_day.index(param)
        day_formatted = now + timedelta(days=day_index)
    elif param.isdecimal():
        day_index = int(param)
        day_formatted = now + timedelta(days=day_index)
    elif param[:4] == "next" and param[-4:] == "week":
        if param[4:-4] == '':
            week_count = 1
        else:
            week_count = int(param[4:-4])
        params = params[1].split(' ', 1)
        param = params[0].lower()
        if param in lower_week:
            weekday_index = lower_week.index(param)
        else:
            weekday_index = int(param)
        day_index = week_count * 7 - now.weekday() + weekday_index
        day_formatted = now + timedelta(days=day_index)
    elif param == "thisweek":
        params = params[1].split(' ', 1)
        param = params[0].lower()
        if param in lower_week:
            weekday_index = lower_week.index(param)
        else:
            weekday_index = int(param)
        day_index = weekday_index - now.weekday()
        day_formatted = now + timedelta(days=day_index)
    else:
        while True:
            try: day_formatted = datetime.strptime(param, "%Y-%m-%d")
            except: pass
            else: break
            try: day_formatted = datetime.strptime(param, "%y-%m-%d")
            except: pass
            else: break
            try: day_formatted = datetime.strptime(param, "%m-%d").replace(year=now.year)
            except: pass
            else: break
            raise ValueError("Unrecognized time data " + param)
    if len(params) == 1:
        return (day_formatted, None)
    else:
        return (day_formatted, params[1])


def getTimeRangeFromParams(params: str, now=datetime.now()):
    params = params.split(' ', 1)
    if '-' in params[0]:
        assert len(params[0].split('-')) == 2
        beginTime, endTime = params[0].split('-')
    else:
        beginTime = params[0]
        params = params[1].split(' ', 1)
        endTime = params[0]
    assert (getTimeFromStr(beginTime) and getTimeFromStr(endTime))
    if len(params) == 1:
        return ((beginTime, endTime), None)
    else:
        return ((beginTime, endTime), params[1])


def getDayPlan(now, time_schedule):
    today_schedule = []

    weekday = now.weekday()
    week_schedule = time_schedule["week"]
    if weekday < len(week_schedule):
        assert type(week_schedule[weekday]) == list 
        today_schedule.extend(week_schedule[weekday])

    todayYmd = now.strftime("%Y-%m-%d")
    day_schedule = time_schedule["day"]
    if todayYmd in day_schedule:
        assert type(day_schedule[todayYmd]) == list 
        today_schedule.extend(day_schedule[todayYmd])

    return today_schedule


def classify(now, today_schedule):
    ongoing_events = []
    waiting_events = []

    for item in today_schedule:
        beginTime = getTimeFromStr(item["beginTime"])
        if not beginTime:
            raise ValueError("Unrecognized beginTime: " + beginTime)
        beginTime = now.replace(hour=beginTime.hour, minute=beginTime.minute, second=beginTime.second)

        endTime = getTimeFromStr(item["endTime"])
        if not endTime:
            raise ValueError("Unrecognized endTime: " + endTime)
        endTime = now.replace(hour=endTime.hour, minute=endTime.minute, second=endTime.second)

        if item["event"]:
            if beginTime <= now and now <= endTime:
                ongoing_events.append((beginTime, endTime, item["event"]))
            elif now < beginTime:
                waiting_events.append((beginTime, endTime, item["event"]))

    ongoing_events_array = np.array(ongoing_events, dtype=timeline_t)
    ongoing_events_array.sort(axis=0, order=('beginTime', 'endTime', 'event'))

    waiting_events_array = np.array(waiting_events, dtype=timeline_t)
    waiting_events_array.sort(axis=0, order=('beginTime', 'endTime', 'event'))

    return ongoing_events_array, waiting_events_array


# Week 0 13:30-15:30 doSomething
# Week Mon 13:30-15:30 doSomething
def addWeekEvent(params: str, now, time_schedule):
    assert "week" in time_schedule
    week_schedule = time_schedule["week"]
    assert type(week_schedule) == list
    assert type(params) == str
    params = params.split(' ', 1)
    if params[0].lower() in lower_week:
        week_index = lower_week.index(params[0].lower())
    else:
        week_index = int(params[0])
    params = params[1].split(' ', 1)
    if '-' in params[0]:
        assert len(params[0].split('-')) == 2
        beginTime, endTime = params[0].split('-')
    else:
        beginTime = params[0]
        params = params[1].split(' ', 1)
        endTime = params[0]
    event = params[1] #allows space
    assert (getTimeFromStr(beginTime) and getTimeFromStr(endTime))
    print(WEEK[week_index], f"{beginTime}-{endTime}, {event}")
    if accept():
        week_schedule[week_index].append({
            "beginTime": beginTime,
            "endTime": endTime,
            "event": event
        })
        dumpConfig(time_schedule=time_schedule)
        print("Adding success.")


# Day today 13:30-15:30 doSomething
# Day 0 13:30-15:30 doSomething
# Day 2022-4-13 13:30-15:30 doSomething
# Day thisweek Mon 13:30-15:30 doSomething
# Day nextweek Mon 13:30-15:30 doSomething
# Day next1week Mon 13:30-15:30 doSomething
def addDayEvent(params: str, now, time_schedule):
    assert "day" in time_schedule
    day_schedule = time_schedule["day"]
    assert type(day_schedule) == dict

    day_formatted, params = getDateFromParams(params=params, now=now)
    (beginTime, endTime), event = getTimeRangeFromParams(params=params, now=now)

    dateYmd = day_formatted.strftime("%Y-%m-%d")
    print(dateYmd, f"{beginTime}-{endTime}, {event}")
    if accept():
        if dateYmd not in day_schedule:
            day_schedule[dateYmd] = []
        day_schedule[dateYmd].append({
            "beginTime": beginTime,
            "endTime": endTime,
            "event": event
        })
        dumpConfig(time_schedule=time_schedule)
        print("Adding success.")


def addEvent(input_string, now, time_schedule):
    if (not input_string) or input_string == "exit":
        raise EOFError() # TODO: 应改为自定义错误类型
        return

    params = input_string.split(' ', 1)
    if len(params) <= 1:
        raise ValueError("Invalid input.")
        return

    scheduleType = params[0].lower()
    params = params[1]
    if scheduleType == "week":
        addWeekEvent(params=params, now=now, time_schedule=time_schedule)
    elif scheduleType == "day":
        addDayEvent(params=params, now=now, time_schedule=time_schedule)
    else:
        raise ValueError("Invalid input.")


def timeline(now = datetime.now(), config_path="timeline.json", config=None):
    random.seed(now.timestamp())
    time_schedule = loadConfig(config_path=config_path, config=config)
    today_schedule = getDayPlan(now, time_schedule)
    ongoing_events_array, waiting_events_array = classify(now, today_schedule)
    ongoing_events_count = len(ongoing_events_array)
    waiting_events_count = len(waiting_events_array)

    print(now.strftime("%Y-%m-%d %H:%M:%S"), end='\n\n')

    if ongoing_events_count:
        print(message["ongoing"][random.randint(0, len(message["ongoing"])-1)], end='\n\n')
        print("---Ongoing---")
        for item in ongoing_events_array:
            print(f"{item['event']}, {item['beginTime'].strftime('%H:%M')}-{item['endTime'].strftime('%H:%M')}")
            print("Countdown:", item["endTime"] - now)
            print()
        if waiting_events_count:
            print("---Waiting---")
            for item in waiting_events_array:
                print(f"{item['event']}, {item['beginTime'].strftime('%H:%M')}-{item['endTime'].strftime('%H:%M')}")
                print("Countdown:", item["beginTime"] - now)
                print()
    elif waiting_events_count:
        print(message["waiting"][random.randint(0, len(message["waiting"])-1)], end='\n\n')
        print("---Waiting---")
        for item in waiting_events_array:
            print(f"{item['event']}, {item['beginTime'].strftime('%H:%M')}-{item['endTime'].strftime('%H:%M')}")
            print("Countdown:", item["beginTime"] - now)
            print()
    else:
        print(message["finish"][random.randint(0, len(message["finish"])-1)], end='\n\n')
