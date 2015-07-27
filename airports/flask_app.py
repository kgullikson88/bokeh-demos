from threading import Thread
import requests
from requests.exceptions import ConnectionError

import pandas as pd
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models.sources import ColumnDataSource, AjaxDataSource

from flask import Flask, jsonify, request
from bokeh.server.crossdomain import crossdomain

import utils
import ui
from utils import routes, airports, create_output


# Prepare data
airport = utils.get_airport_data('3682', utils.airports)
ap_routes = utils.get_routes(airport)
_source_aps = create_output(airport['destinations'])
_all_aps = create_output(utils.airports)

df_isolated_ap = utils.airports[~utils.airports.id.isin(airport['destinations'].id.values)]
_isolated_aps = create_output(df_isolated_ap)
_active_aps = create_output(utils.active_airports)


app = Flask(__name__)

@app.route('/data/ap_routes', methods=['GET', 'OPTIONS'])
@crossdomain(origin="*", methods=['GET', 'POST'], headers=None)
def ap_routes_view():
    return jsonify(ap_routes)

@app.route('/data/source_aps', methods=['GET', 'OPTIONS'])
@crossdomain(origin="*", methods=['GET', 'POST'], headers=None)
def source_aps_view():
    return jsonify(_source_aps)

@app.route('/data/isolated_aps', methods=['GET', 'OPTIONS'])
@crossdomain(origin="*", methods=['GET', 'POST'], headers=None)
def isolated_aps_view():
    return jsonify(_isolated_aps)

@app.route('/data/all_aps', methods=['GET', 'OPTIONS'])
@crossdomain(origin="*", methods=['GET', 'POST'], headers=None)
def all_aps_view():
    return jsonify(_all_aps)

@app.route('/data/update/<newid>', methods=['GET', 'OPTIONS'])
@crossdomain(origin="*", methods=['GET', 'POST'], headers=None)
def update(newid):
    global airport
    global ap_routes
    global _source_aps
    global _isolated_aps
    global _all_aps

    airport = utils.get_airport_data(str(newid), utils.airports)
    ap_routes = utils.get_routes(airport)

    _all_aps = create_output(utils.airports)

    df_source_ap = utils.airports[utils.airports.id.isin(airport['destinations'].id)]
    _source_aps = create_output(df_source_ap)

    # df_isolated_ap = airports[~airports.id.isin(airport['connections'].dest_ap_id.values)]
    df_isolated_ap = utils.airports[~utils.airports.id.isin(airport['destinations'].id.values)]
    _isolated_aps = create_output(df_isolated_ap)

    return jsonify({"msg": "OK", 'connections': len(airport['destinations'])})


if __name__ == "__main__":
    app.run(port=5050, debug=True)


