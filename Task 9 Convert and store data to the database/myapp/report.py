import datetime
import pathlib


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
START_DATA_FILE = BASE_DIR / 'data' / 'start.log'
FINISH_DATA_FILE = BASE_DIR / 'data' / 'end.log'
ABBREVIATIONS_FILE = BASE_DIR / 'data' / 'abbreviations.txt'


def read_data_from_file(file):
    with open(file, "r") as f:
        content = f.read().splitlines()
    return content


def abbreviation_file_list(content):
    abbreviations = []
    for line in content:
        sep_data = line.split("_")
        abbreviations.append(sep_data)
    return abbreviations


def time_file_list(content):
    formatted_lines = []
    for line in content:
        sep_data = line.split("_")
        abb = sep_data[0][:3]
        start_date = sep_data[0][3:]
        start_time = sep_data[1]
        obj = [abb, start_date, start_time]
        formatted_lines.append(obj)
    return formatted_lines


def count_time(starts, finishes):
    delta_times = []
    for start_line in starts:
        for finish_line in finishes:
            if finish_line[0] == start_line[0]:
                format = "%I:%M:%S.%f"
                t1 = datetime.datetime.strptime(start_line[2], format)
                t2 = datetime.datetime.strptime(finish_line[2], format)
                time = t2 - t1
                line = [start_line[0], start_line[2], finish_line[2], time]
                delta_times.append(line)
                break
    return delta_times


def built_report(delta_times, racers, order, driver_id):
    for time in delta_times:
        for racer in racers:
            if racer[0] == time[0]:
                racer.extend(time[1:4])
                break

    racers_sorted = []

    if driver_id != "":
        for racer in racers:
            if racer[0] == driver_id:
                return [racer]
    elif order == "desc":
        racers_sorted = sorted(racers, key=lambda x: - x[5])
    else:
        racers_sorted = sorted(racers, key=lambda x: x[5])

    return racers_sorted


def drivers_statistic(racers_sorted):
    statistic = []
    for driver in racers_sorted:
        info_dict = dict(id=driver[0], name=driver[1], car=driver[2], start_time=driver[3], end_time=driver[4],
                 delta_time=driver[5])
        statistic.append(info_dict)
    return statistic


def ordering(order, driver_id):
    start_data = read_data_from_file(START_DATA_FILE)
    start_data_parsed = time_file_list(start_data)

    finish_data = read_data_from_file(FINISH_DATA_FILE)
    finish_data_parsed = time_file_list(finish_data)

    time_parsed = count_time(start_data_parsed, finish_data_parsed)

    abbreviations = read_data_from_file(ABBREVIATIONS_FILE)
    abbreviations_parsed = abbreviation_file_list(abbreviations)

    report = built_report(time_parsed, abbreviations_parsed, order, driver_id)
    final_statistic = drivers_statistic(report)

    return final_statistic



