
import json

from bokeh.plotting import figure, show
from bokeh.models import DatetimeTickFormatter, DatePicker

import ast



def make_a_graph(all_the_shit):

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



with open("data_for_graph.json", "r") as file:
    data = json.load(file)

colors = (color for color in ["green", "red", "magenta", "blue", "purple"])
color_dict = {}
for key, value in data.items():
    data[key] = ast.literal_eval(value)
    color_dict[key] = next(colors)




make_a_graph(data)


