import utils
import ui
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models import ColumnDataSource

output_file('airports.html')

routes = ColumnDataSource()
all_airports = ColumnDataSource(utils.airports)

plot = figure(title="Flights", plot_width=1000, plot_height=500,
              tools="pan,box_zoom,box_select,tap,hover,resize,reset")
ui.create_airport_map(plot, routes, all_airports)

show(plot)
