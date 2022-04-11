from datetime import datetime
import json
import numpy as np
from hashlib import md5

timeline_t = [('beginTime', datetime), ("endTime", datetime), ("event", dict)]

message = {
	"progressing": [
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


def rand16(n):
	return (md5(str(datetime.now().timestamp()).encode()).digest()[6] << 8
		  | md5(str(datetime.now().timestamp()).encode()).digest()[9]) % n

if __name__ == '__main__':
	try:
		with open("timeline.json", "r", encoding="utf8") as f:
			time_schedule = json.load(f)
		assert type(time_schedule) == dict
	except:
		time_schedule = {}

	if "week" in time_schedule:
		week_schedule = time_schedule["week"]
		assert type(week_schedule) == list
	else:
		week_schedule = []
	if "day" in time_schedule:
		day_schedule = time_schedule["day"]
		assert type(day_schedule) == dict
	else:
		day_schedule = {}

	now = datetime.now()
	print(now.strftime("%Y-%m-%d %H:%M:%S"), end='\n\n')

	today_schedule = []

	weekday = now.weekday()
	if weekday < len(week_schedule):
		today_schedule.extend(week_schedule[weekday])

	todayYmd = now.strftime("%Y-%m-%d")
	if todayYmd in day_schedule:
		assert type(day_schedule[todayYmd]) == list 
		today_schedule.extend(day_schedule[todayYmd])

	waiting_events = []
	progressing_events = []

	progressing_events_count = 0
	waiting_events_count = 0

	for item in today_schedule:
		beginTime = datetime.strptime(item["beginTime"], "%H:%M")
		beginTime = now.replace(hour=beginTime.hour, minute=beginTime.minute, second=0)

		endTime = datetime.strptime(item["endTime"], "%H:%M")
		endTime = now.replace(hour=endTime.hour, minute=endTime.minute, second=0)

		if item["event"]:
			if beginTime <= now and now <= endTime:
				progressing_events_count += 1
				progressing_events.append((beginTime, endTime, item["event"]))
			elif now < beginTime:
				waiting_events_count += 1
				waiting_events.append((beginTime, endTime, item["event"]))

	waiting_events_array = np.array(waiting_events, dtype=timeline_t)
	waiting_events_array.sort(axis=0, order=('beginTime', 'endTime', 'event'))
	# print(waiting_events)
	# print(waiting_events_array)
	progressing_events_array = np.array(progressing_events, dtype=timeline_t)
	progressing_events_array.sort(axis=0, order=('beginTime', 'endTime', 'event'))
	# print(progressing_events)
	# print(progressing_events_array)

	if progressing_events_count:
		print(message["progressing"][rand16(len(message["progressing"]))], end='\n\n')
		for item in progressing_events_array:
			print(f"now event: {item['event']}, {item['beginTime'].strftime('%H:%M')} - {item['endTime'].strftime('%H:%M')}")
			print("Countdown:", item["endTime"] - now)
		print()
		if waiting_events_count:
			for item in waiting_events_array:
				print(f"next event: {item['event']}, {item['beginTime'].strftime('%H:%M')} - {item['endTime'].strftime('%H:%M')}")
				print("Countdown:", item["beginTime"] - now)
	elif waiting_events_count:
		print(message["waiting"][rand16(len(message["waiting"]))], end='\n\n')
		for item in waiting_events_array:
			print(f"next event: {item['event']}, {item['beginTime'].strftime('%H:%M')} - {item['endTime'].strftime('%H:%M')}")
			print("Countdown:", item["beginTime"] - now)
	else:
		print(message["finish"][rand16(len(message["finish"]))], end='\n\n')
