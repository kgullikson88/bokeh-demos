from __future__ import print_function
from threading import Thread
import requests
from requests.exceptions import ConnectionError

import utils
import ui
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models.sources import ColumnDataSource, AjaxDataSource

from bokeh.embed import components
from bokeh.resources import Resources
from bokeh.templates import RESOURCES

from flask import render_template, request
from flask_app import app


POLL_TIME = 1000

output_file('airports.html')

# Create DataSources
ap_routes_source = AjaxDataSource(data_url='http://localhost:5050/data/ap_routes',
                                  polling_interval=POLL_TIME)
all_airports = AjaxDataSource(data_url='http://127.0.0.1:5050/data/all_aps',
                             polling_interval=POLL_TIME)

# create plot object and add all it's objects
plot = figure(title="Flights", plot_width=1000, plot_height=500,
              tools="pan,box_zoom,box_select,tap,resize,reset")
ui.create_airport_map(plot, ap_routes_source, all_airports)

# Let' add a new view to the airport dashboard so we can serve a customized
# dashboard page and integrate some Frontend functionality
@app.route("/dashboard")
def newapplet():
    theme = request.args.get('theme', 'default')
    # preare all resources
    INLINE = Resources(mode="inline", minified=False,)
    templname = "dashboard.html"
    plot_resources = RESOURCES.render(
        js_raw=INLINE.js_raw,
        css_raw=INLINE.css_raw,
        js_files=INLINE.js_files,
        css_files=INLINE.css_files,
    )

    # get the js script and html divs for the bokeh objects to place on the
    # html page
    plot_script, extra_divs = components({"main_plot": plot}, INLINE)
    themes = ["default", "dark"]
    options = {k: 'selected="selected"' if theme == k else "" for k in themes}

    return render_template(
        templname,
        theme = theme,
        extra_divs = extra_divs,
        plot_script = plot_script,
        plot_resources=plot_resources,
        theme_options=options,
    )

if __name__ == "__main__":
    print("To see the example go to: http://127.0.0.1:5050/dashboard")
    print()
    print()
    app.run(port=5050, debug=True)

