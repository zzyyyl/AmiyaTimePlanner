import json
import random
import re
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Tuple, Union, List

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


def assertOfType(param, T: type, paramName: str) -> None:
    if type(param) != T:
        raise TypeError(f"`{paramName}` is of type `{type(param)}`, but should be `{T}`.")


def assertOfTypes(param, Ts: List[type], paramName: str) -> None:
    for T in Ts:
        if type(param) == T:
            return
    raise TypeError(f"`{paramName}` is of type `{type(param)}`, but should be `{Ts}`.")


def seParams(params: str) -> Tuple[str, Optional[str]]:
    # separams = separate params
    assertOfType(params, str, "params")
    paramList = params.strip().split(' ', 1)
    if len(paramList) == 1:
        return paramList[0], None
    else:
        return paramList[0], paramList[1]


def getTimeFromStr(time_str: str) -> Union[bool, datetime]:
    assertOfType(time_str, str, "time_str")
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
        assertOfTypes(config, [str, dict], "config")
        if type(config) == str:
            time_schedule = json.loads(config)
            assertOfType(time_schedule, dict, "time_schedule")
        elif type(config) == dict:
            time_schedule = config
        else:
            raise RuntimeError("Unknown Error.")
    else:
        try:
            with open(config_path, "r", encoding="utf8") as f:
                time_schedule = json.load(f)
            assertOfType(time_schedule, dict, "time_schedule")
        except:
            time_schedule = {}
    if "week" in time_schedule:
        assertOfType(time_schedule["week"], list, "time_schedule['week']")
    else:
        time_schedule["week"] = [[] for x in range(7)]
    if "day" in time_schedule:
        assertOfType(time_schedule["day"], dict, "time_schedule['day']")
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
    assertOfType(params, str, "params")
    if not re.match(
        pattern=r"(today|tomorrow)" +\
                r"|((thisweek|nextweek|next-?[0-9]+week) +(mon|tue|wed|thr|fri|sat|sun))" +\
                r"|((thisweek|nextweek|next-?[0-9]+week) +(-?[0-9]+))" +\
                r"|([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})" +\
                r"|([0-9]{2}-[0-9]{1,2}-[0-9]{1,2})|([0-9]{1,2}-[0-9]{1,2})",
        string=params.strip(), flags=re.I):
        raise TypeError(f"Params `{params}` do not match the date rule.")
    param, params = seParams(params)
    param = param.lower()
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
        param, params = seParams(params)
        param = param.lower()
        if param in lower_week:
            weekday_index = lower_week.index(param)
        else:
            weekday_index = int(param)
        day_index = week_count * 7 - now.weekday() + weekday_index
        day_formatted = now + timedelta(days=day_index)
    elif param == "thisweek":
        param, params = seParams(params)
        param = param.lower()
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
            raise TypeError("Unrecognized time data " + param)
    return (day_formatted, params)


def getTimeRangeFromParams(params: str, now=datetime.now()):
    param, params = seParams(params)
    if '-' in param:
        assert len(param.split('-')) == 2
        beginTime, endTime = param.split('-')
    else:
        beginTime = param
        param, params = seParams(params)
        endTime = param
    assert (getTimeFromStr(beginTime) and getTimeFromStr(endTime))
    return ((beginTime, endTime), params)


def getDayPlan(now, time_schedule):
    today_schedule = []

    weekday = now.weekday()
    week_schedule = time_schedule["week"]
    if weekday < len(week_schedule):
        assertOfType(week_schedule[weekday], list, f"week_schedule[{weekday}]")
        today_schedule.extend(week_schedule[weekday])

    todayYmd = now.strftime("%Y-%m-%d")
    day_schedule = time_schedule["day"]
    if todayYmd in day_schedule:
        assertOfType(day_schedule[todayYmd], list, f"day_schedule[{todayYmd}]")
        today_schedule.extend(day_schedule[todayYmd])

    return today_schedule


def classify(now, today_schedule):
    ongoing_events = []
    waiting_events = []

    for item in today_schedule:
        beginTime = getTimeFromStr(item["beginTime"])
        if not beginTime:
            raise TypeError("Unrecognized beginTime: " + beginTime)
        beginTime = now.replace(hour=beginTime.hour, minute=beginTime.minute, second=beginTime.second)

        endTime = getTimeFromStr(item["endTime"])
        if not endTime:
            raise TypeError("Unrecognized endTime: " + endTime)
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
    assertOfType(week_schedule, list, "week_schedule")
    assertOfType(params, str, "params")
    param, params = seParams(params)
    param = param.lower()
    if param in lower_week:
        week_index = lower_week.index(param)
    else:
        week_index = int(param)
    param, params = seParams(params)
    if '-' in param:
        assert len(param.split('-')) == 2
        beginTime, endTime = param.split('-')
    else:
        beginTime = param
        param, params = seParams(params)
        endTime = param
    event = params #allows space
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
    assertOfType(day_schedule, dict, "day_schedule")

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

    param, params = seParams(input_string)
    if not params:
        raise TypeError("Invalid input.")
        return

    scheduleType = param.lower()
    if scheduleType == "week":
        addWeekEvent(params=params, now=now, time_schedule=time_schedule)
    elif scheduleType == "day":
        addDayEvent(params=params, now=now, time_schedule=time_schedule)
    else:
        raise TypeError("Invalid input.")


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
