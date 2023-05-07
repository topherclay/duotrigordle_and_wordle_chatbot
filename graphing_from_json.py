
import json

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
    fig = figure(title="Scores",
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





def make_many_wordle_bar_graph(all_the_shit):

    # todo: handle failed games
    # first i have to get the failed games from sql.
    for key in all_the_shit.keys():
        full_data = all_the_shit[key]
        scores = [item[1] for item in full_data]
        fig = figure(title=f"{key}",
                     x_axis_label="score",
                     y_axis_label="amount",
                     sizing_mode="stretch_both")


        x_slots = list(range(1,7))
        y_values = []
        for index in x_slots:
            y_values.append(scores.count(index))






        print(f"{key} == {color_dict[key]}")

        fig.vbar(x=x_slots, top=y_values, color=color_dict[key])





        fig.yaxis.ticker.max_interval = 1
        fig.yaxis.ticker.min_interval = 1
        fig.xaxis.ticker.max_interval = 10
        fig.xaxis.ticker.min_interval = 1


        fig.x_range.start = 1
        fig.x_range.end = 7
        fig.y_range.end = 85
        fig.y_range.start = 1


        show(fig)
        time.sleep(2)




with open("data_for_graph.json", "r") as file:
    data = json.load(file)

colors = (color for color in ["green", "red", "magenta", "blue", "purple"])
color_dict = {}
for key, value in data.items():
    data[key] = ast.literal_eval(value)
    color_dict[key] = next(colors)




make_many_wordle_bar_graph(data)


