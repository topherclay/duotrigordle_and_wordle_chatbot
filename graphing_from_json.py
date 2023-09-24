
import json
from pprint import pprint


import bokeh.models
from bokeh.plotting import figure, show
from bokeh.models import DatetimeTickFormatter, DatePicker

import ast

import time


def make_a_graph(all_the_shit):
    # this was for duotrigordle
    fig = figure(title="Time Scores",
                 x_axis_label="day",
                 sizing_mode="stretch_both")





    for key in all_the_shit.keys():
        # print(all_the_shit[key])
        full_data = all_the_shit[key]
        days_with_data = [item[0] for item in full_data]
        first_day = min(days_with_data)
        last_day = max(days_with_data)
        times = [item[1] for item in full_data]
        print(times)
        times = [time/60 for time in times]
        print(times)

        times_for_specific_days = {day: time for day, time in zip(days_with_data, times)}
        all_days = [day for day in range(first_day, last_day + 1)]
        all_times = [times_for_specific_days[day] if (day in days_with_data) else float("nan") for day in range(first_day, last_day + 1)]


        print(f"{key} == {color_dict[key]}")

        fig.scatter(x=all_days, y=all_times, color=color_dict[key], size=10, legend_label=key.split("#")[0])
        fig.line(x=all_days, y=all_times, color=color_dict[key])

    fig.legend.location = "top_left"
    fig.legend.title = "players"

    fig.yaxis.ticker.max_interval = 2
    fig.yaxis.ticker.min_interval = 1
    fig.xaxis.ticker.max_interval = 10
    fig.xaxis.ticker.min_interval = 1


    fig.x_range.start = 190
    fig.x_range.end = 275
    fig.y_range.end = 20
    fig.y_range.start = 0

    show(fig)


def make_a_wordle_graph(all_the_shit):
    # unused
    fig = figure(title="dwd",
                 x_axis_label="day",
                 sizing_mode="stretch_both")


    for key in all_the_shit.keys():
        # print(all_the_shit[key])
        full_data = all_the_shit[key]
        days_with_data = [item[0] for item in full_data]
        first_day = min(days_with_data)
        last_day = max(days_with_data)
        scores = [item[1] for item in full_data]






        print(f"{key} == {color_dict[key]}")

        fig.scatter(x=days_with_data, y=scores, color=color_dict[key], size=10, legend_label=key.split("#")[0])
        # fig.line(x=days_with_data, y=scores, color=color_dict[key])

    fig.legend.location = "top_left"
    fig.legend.title = "players"

    fig.yaxis.ticker.max_interval = 1
    fig.yaxis.ticker.min_interval = 1
    fig.xaxis.ticker.max_interval = 10
    fig.xaxis.ticker.min_interval = 1


    # fig.x_range.start = 190
    # fig.x_range.end = 275
    fig.y_range.end = 6.5
    fig.y_range.start = 0.5

    show(fig)


def make_many_wordle_graph(all_the_shit):


    for key in all_the_shit.keys():
        # print(all_the_shit[key])
        full_data = all_the_shit[key]
        days_with_data = [item[0] for item in full_data]
        first_day = min(days_with_data)
        last_day = max(days_with_data)
        scores = [item[1] for item in full_data]

        fig = figure(title=f"{key}",
                     x_axis_label="day",
                     sizing_mode="stretch_both")



        print(f"{key} == {color_dict[key]}")

        fig.scatter(x=days_with_data, y=scores, color=color_dict[key], size=10, legend_label=key.split("#")[0])
        # fig.line(x=days_with_data, y=scores, color=color_dict[key])


        for index in range(1, 7):
            amount = scores.count(index)
            label = bokeh.models.Label(x=690, y=index, text=f"\n {amount} \n",
                                       border_line_color="black", border_line_alpha=0.5)
            fig.add_layout(label)

        fig.yaxis.ticker.max_interval = 1
        fig.yaxis.ticker.min_interval = 1
        fig.xaxis.ticker.max_interval = 10
        fig.xaxis.ticker.min_interval = 1


        fig.x_range.start = 440
        fig.x_range.end = 700
        fig.y_range.end = 6.5
        fig.y_range.start = 0.5

        fig.legend.location = "top_left"

        show(fig)
        time.sleep(2)



def make_time_line_graph(all_the_shit):

    def turn_days_into_intervals(all_days):
        intervals = []
        interval_min = -1
        interval_max = -2
        for index in range(len(all_days)):
            number = all_days[index]
            if interval_min == -1:
                interval_min = number
                interval_max = number + 1

            try:
                next_number = all_days[index+1]
            except IndexError:
                intervals.append((interval_min, interval_max))
                break

            if next_number == number + 1:
                interval_max = next_number
            else:
                intervals.append((interval_min, interval_max))
                interval_min = -1

        return intervals




    # todo: handle failed games
    # first i have to get the failed games from sql.
    for _key in all_the_shit.keys():
        full_data = all_the_shit[_key]

        days_played = [item[0] for item in full_data]



        intervs = turn_days_into_intervals(days_played)




        fig = figure(title=f"All {len(days_played)} submissions of {_key}",
                     x_axis_label=f"{_key}",
                     y_axis_label="board numbers played",
                     width=400,
                     height=800)

        # print(f"{key} == {color_dict[key]}")

        for item in intervs:
            fig.vbar(x=1, bottom=item[0], top=item[1], color="blue")

        fig.yaxis.ticker.max_interval = 10
        fig.yaxis.ticker.min_interval = 2
        fig.xaxis.ticker.max_interval = 1
        fig.xaxis.ticker.min_interval = 1

        fig.x_range.start = 0.5
        fig.x_range.end = 1.5
        fig.y_range.end = max(days_played)
        fig.y_range.start = min(days_played)

        show(fig)
        time.sleep(2)


def make_many_wordle_bar_graph(all_the_shit):


    for _key in all_the_shit.keys():
        full_data = all_the_shit[_key]
        scores = [item[1] for item in full_data if item[2] is True]

        failed_game_count = [item[2] for item in full_data if item[2] is False]
        failed_game_count = len(failed_game_count)




        total_games = 0


        x_slots = list(range(0,7))
        y_values = []
        for index in x_slots:

            if index == 0:
                print(f"{_key} scored {index} {failed_game_count} times")
                y_values.append(failed_game_count)
                total_games += failed_game_count
                continue

            print(f"{_key} scored {index} {scores.count(index)} times")
            y_values.append(scores.count(index))
            total_games += scores.count(index)

        # pprint(full_data)
        print(f"total adds up to {total_games}")
        print(f"length of data is {len(full_data)}")


        fig = figure(title=f"{_key.split('#')[0]}'s {total_games} games.",
                     x_axis_label="score",
                     y_axis_label="amount",
                     width=400,
                     height=800)



        # print(f"{key} == {color_dict[key]}")

        # fig.vbar(x=x_slots, top=y_values, color=color_dict[key])
        fig.vbar(x=x_slots, top=y_values, color="blue")



        fig.yaxis.ticker.max_interval = 10
        fig.yaxis.ticker.min_interval = 5
        fig.xaxis.ticker.max_interval = 10
        fig.xaxis.ticker.min_interval = 1


        fig.x_range.start = 0
        fig.x_range.end = 7
        fig.y_range.end = 120
        fig.y_range.start = 0


        show(fig)
        time.sleep(2)




with open("data_for_graph.json", "r") as file:
    data = json.load(file)







new_data = {}
for key in data.keys():
    if key.split("#")[1] in ["0", "9686", "4960"]:
        new_data[key] = data[key]

data = new_data








colors = (color for color in ["green", "red", "magenta", "blue", "purple", "pink", "red", "red", "red","red","red","red","red","red","red"])
color_dict = {}
for key, value in data.items():
    data[key] = ast.literal_eval(value)
    color_dict[key] = next(colors)







# make_many_wordle_bar_graph(data)
make_time_line_graph(data)

