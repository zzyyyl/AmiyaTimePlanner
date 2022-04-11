from datetime import datetime, timedelta
import json
import numpy as np
from hashlib import md5

timeline_t = [('beginTime', datetime), ("endTime", datetime), ("event", dict)]

WEEK = ["Mon", "Tue", "Wed", "Thr", "Fri", "Sat", "Sun"]
lower_week = [x.lower() for x in WEEK]

DAY = ["Today", "Tomorrow"]
lower_day = [x.lower() for x in DAY]

def rand16(n):
	return (md5(str(datetime.now().timestamp()).encode()).digest()[6] << 8
		  | md5(str(datetime.now().timestamp()).encode()).digest()[9]) % n

def DumpConfig():
	with open("timeline.json", "w", encoding="utf8") as f:
		json.dump(time_schedule, f, indent=2)

# Week Mon 13:30-15:30 doSomething
def append_week_event(s: str):
	assert type(s) == str
	s = s.split(' ')
	if s[0].lower() in lower_week:
		week_index = lower_week.index(s[0].lower())
	else:
		week_index = int(s[0])
	if '-' in s[1]:
		s[1] = s[1].split('-')
		beginTime = s[1][0]
		endTime = s[1][-1]
	else:
		beginTime = s[1]
		endTime = s[2]
	event = s[-1]
	print(WEEK[week_index], f"{beginTime}-{endTime}, {event}")
	choice = 'n'
	while True:
		choice = input("(y/n)").lower()
		if choice in ['y', 'n']: break
	if choice == 'y':
		week_schedule[week_index].append({
			"beginTime": beginTime,
			"endTime": endTime,
			"event": event
		})
		DumpConfig()
		print("Append success.")

# Day today 13:30-15:30 doSomething
# Day 0 13:30-15:30 doSomething
# Day 2022-4-13 13:30-15:30 doSomething
# Day thisweek Mon 13:30-15:30 doSomething
# Day nextweek Mon 13:30-15:30 doSomething
# Day next1week Mon 13:30-15:30 doSomething
def append_day_event(s: str):
	assert type(s) == str
	s = s.split(' ', 1)
	param = s[0].lower()
	if param in lower_day:
		day_index = lower_day.index(param)
		day_formatted = datetime.now() + timedelta(days=day_index)
	elif param.isdecimal():
		day_index = int(param)
		day_formatted = datetime.now() + timedelta(days=day_index)
	elif param[:4] == "next" and param[-4:] == "week":
		if param[4:-4] == '':
			week_count = 1
		else:
			week_count = int(param[4:-4])
		s = s[1].split(' ', 1)
		param = s[0].lower()
		if param in lower_week:
			weekday_index = lower_week.index(param)
		else:
			weekday_index = int(param)
		day_index = week_count * 7 - datetime.now().weekday() + weekday_index
		day_formatted = datetime.now() + timedelta(days=day_index)
	elif param == "thisweek":
		s = s[1].split(' ', 1)
		param = s[0].lower()
		if param in lower_week:
			weekday_index = lower_week.index(param)
		else:
			weekday_index = int(param)
		day_index = weekday_index - datetime.now().weekday()
		day_formatted = datetime.now() + timedelta(days=day_index)
	else:
		while True:
			try: day_formatted = datetime.strptime(param, "%Y-%m-%d")
			except: pass
			else: break
			try: day_formatted = datetime.strptime(param, "%y-%m-%d")
			except: pass
			else: break
			try:
				day_formatted = datetime.strptime(param, "%m-%d")
				day_formatted = day_formatted.replace(year=datetime.now().year)
			except: pass
			else: break
			raise ValueError("Unrecognized time data " + param)
	s = s[1].split(' ')
	if '-' in s[0]:
		s[0] = s[0].split('-')
		beginTime = s[0][0]
		endTime = s[0][-1]
	else:
		beginTime = s[0]
		endTime = s[1]
	event = s[-1]
	dateYmd = day_formatted.strftime("%Y-%m-%d")
	print(dateYmd, f"{beginTime}-{endTime}, {event}")
	choice = 'n'
	while True:
		choice = input("(y/n)").lower()
		if choice in ['y', 'n']: break
	if choice == 'y':
		if dateYmd not in day_schedule:
			day_schedule[dateYmd] = []
		day_schedule[dateYmd].append({
			"beginTime": beginTime,
			"endTime": endTime,
			"event": event
		})
		DumpConfig()
		print("Append success.")

if __name__ == '__main__':
	try:
		with open("timeline.json", "r", encoding="utf8") as f:
			time_schedule = json.load(f)
		assert type(time_schedule) == dict
	except:
		time_schedule = {}

	if "week" not in time_schedule:
		time_schedule["week"] = [[] for x in range(7)]
	week_schedule = time_schedule["week"]

	if "day" not in time_schedule:
		time_schedule["day"] = {}
	day_schedule = time_schedule["day"]

	while True:
		s = input("Append event:")
		s = s.split(' ', 1)

		if s[0].lower() == 'week':
			append_week_event(s[1])
		elif s[0].lower() == 'day':
			append_day_event(s[1])

	s = json.dumps(time_schedule, indent=4)
	print(s)
