import os.path
from bokeh.plotting import figure, show, output_server, output_file
from bokeh.models.sources import ColumnDataSource, AjaxDataSource
from blaze.server.client import Client
from blaze import Data

output_file("localdata.html")

source = AjaxDataSource(data_url='http://localhost:5000/data', polling_interval=1000)

p = figure(x_axis_type = "datetime", tools="pan,wheel_zoom,box_zoom,reset,previewsave")
p.line('Date', 'Price', color='#A6CEE3', source=source, legend='AAPL')
show(p)

