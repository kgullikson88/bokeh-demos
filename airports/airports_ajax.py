""" This example provide a basic implementation of the airports_simple
    example using AjaxDataSource instead of ColumnDataSource
"""
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models.sources import ColumnDataSource, AjaxDataSource

from flask import Flask, jsonify
from bokeh.server.crossdomain import crossdomain

import utils
import ui
from utils import routes, airports

POLL_TIME = 1000

output_file('airports_ajax.html')

# Prepare data
airport = utils.get_airport_data('3682', utils.airports)
ap_routes = utils.get_routes(airport)
all_aps = utils.create_output(utils.airports)

# Create DataSources
ap_routes_source = AjaxDataSource(data_url='http://localhost:5050/data/ap_routes',
                                  polling_interval=POLL_TIME)
all_aps_source = AjaxDataSource(data_url='http://localhost:5050/data/all_aps',
                                polling_interval=POLL_TIME)

# Create bokeh objects
plot = figure(title="Flights", plot_width=1000, plot_height=500,
              tools="pan,box_zoom,box_select,tap,resize,reset")
ui.create_airport_map(plot, ap_routes_source, all_aps_source)

##################
# FLASK SERVICE
##################
app = Flask(__name__)

@app.route('/data/ap_routes', methods=['GET', 'OPTIONS'])
@crossdomain(origin="*", methods=['GET', 'POST'], headers=None)
def ap_routes_view():
    return jsonify(ap_routes)

@app.route('/data/all_aps', methods=['GET', 'OPTIONS'])
@crossdomain(origin="*", methods=['GET', 'POST'], headers=None)
def all_aps_view():
    return jsonify(all_aps)

if __name__ == "__main__":
    show(plot)
    app.run(port=5050, debug=True)

