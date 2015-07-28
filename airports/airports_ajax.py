""" This example provide a basic implementation of the airports_simple
    example using AjaxDataSource instead of ColumnDataSource.

    It also differentiates the airports and shows the airport with more
    destinations routes in red, all it's destinations in green all other
    airports with a smaller circle in light grey color. This airport is
    also connected to all it's destinations using a line glyph.
"""
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models.sources import ColumnDataSource, AjaxDataSource
import utils
import ui
from utils import routes, airports
from flask_app import app

POLL_TIME = 1000

output_file('airports_ajax.html')

# Create DataSources
ap_routes_source = AjaxDataSource(data_url='http://localhost:5050/data/ap_routes',
                                  polling_interval=POLL_TIME)
all_aps_source = AjaxDataSource(data_url='http://localhost:5050/data/all_aps',
                                polling_interval=POLL_TIME)

# Create bokeh objects
plot = figure(title="Flights", plot_width=1000, plot_height=500,
              tools="pan,box_zoom,box_select,tap,resize,reset")
ui.create_airport_map(plot, ap_routes_source, all_aps_source)

if __name__ == "__main__":
    show(plot)
    # serve the flask app
    app.run(port=5050, debug=True)

