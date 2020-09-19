import json
import datetime


class DataIO:
    @staticmethod
    def write_out_today(today, date):
        today_json = []
        for each in today:
            print(each.__dict__)
            all_properties = each.__dict__
            to_save = dict((k, all_properties[k]) for k in ("name", "_task_time", "on", "complete"))
            time = to_save["_task_time"]
            time_list = [time.year, time.month, time.day, time.hour, time.minute, time.second, time.microsecond]
            to_save["_task_time"] = time_list
            today_json.append(to_save)

        log = {"tasks": today_json, "date": [date.year, date.month, date.day]}
        with open("data/log.json", "w") as json_file:
            json.dump(log, json_file)
            print("WRITE log.json", log)

    @staticmethod
    def read_in_today():
        with open("data/log.json", "r") as json_file:
            log_json = json.load(json_file)
            print("READ log.json")
        try:
            return log_json["tasks"], datetime.date(log_json["date"][0], log_json["date"][1], log_json["date"][2])
        except TypeError:
            return None, datetime.datetime.fromtimestamp(0)

    @staticmethod
    def add_local_history(today, date):
        new_log = {"tasks": today, "date": [date.year, date.month, date.day]}
        with open("data/local_history.json", "r") as json_file:
            log_json = json.load(json_file)
            print("READ local_history.json")
        log_json["local_history"].append(new_log)
        with open("data/local_history.json", "w") as json_file:
            json.dump(log_json, json_file)
            print("WRITE local_history.json")
