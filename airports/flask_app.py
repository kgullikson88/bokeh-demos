import pandas as pd

from flask import Flask, jsonify, request
from bokeh.server.crossdomain import crossdomain

import utils
from utils import create_output


# Prepare data
airport = utils.get_airport_data('3682', utils.airports)
ap_routes = utils.get_routes(airport)
_source_aps = create_output(airport['destinations'])
_all_aps = create_output(utils.airports)

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

    ap = airport['airport']
    ind = ap.index.values[0]
    dd = {k: v[ind] for k, v in dict(ap).items()}

    return jsonify(
        {
         'connections': len(airport['destinations']),
         'airport': dd
        }
    )


if __name__ == "__main__":
    app.run(port=5050, debug=True)


