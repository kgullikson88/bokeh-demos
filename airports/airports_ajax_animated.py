""" This example provide a extends airports_ajax example adding a
simple animation and changes the selected airport every 3 seconds
"""
from __future__ import print_function

import time
from threading import Thread

import utils
import ui
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models.sources import ColumnDataSource, AjaxDataSource

from flask import jsonify
from flask_app import app
import walk_airports

POLL_TIME = 1000

output_file('airports_animated.html')

# Create DataSources
airport = utils.get_airport_data('3682', utils.airports)
ap_routes_source = AjaxDataSource(data_url='http://localhost:5050/data/ap_routes',
                                  polling_interval=POLL_TIME)
all_aps_source = AjaxDataSource(data_url='http://localhost:5050/data/source_aps',
                             polling_interval=POLL_TIME)

plot = figure(title="Flights", plot_width=1000, plot_height=500,
              tools="pan,box_zoom,box_select,tap,resize,reset")
ui.create_airport_map(plot, ap_routes_source, all_aps_source)


def gen_entry(freq=3):
    """ Updates the current selected airport every `freq` seconds"""
    while True:
        new_id = walk_airports.select_new()
        try:
            airport = utils.get_airport_data(str(new_id), utils.airports)
        except ValueError:
            print("ERROR?", new_id)

        time.sleep(freq)


if __name__ == "__main__":
    # start a new thread to update the selected plot and animate the plot
    t = Thread(target=gen_entry)
    t.daemon = True
    t.start()

    # show the plot and start the flask webserver
    show(plot)
    app.run(port=5050, debug=True)
