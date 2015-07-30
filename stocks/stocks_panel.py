# The plot server must be running
# Go to http://localhost:5006/bokeh to view this plot
from collections import OrderedDict
import os.path
from bokeh.plotting import figure, show, output_server, output_file, vplot
from bokeh.models.sources import ColumnDataSource, AjaxDataSource
from bokeh.models import BoxSelectTool, HoverTool
from blaze.server.client import Client
from blaze import Data
from bokeh.models.actions import Callback

import requests

output_file("remotedata.html")


def style_axis(plot):
    plot.axis.minor_tick_in=None
    plot.axis.minor_tick_out=None
    plot.axis.major_tick_in=None
    plot.axis.major_label_text_font_size="10pt"
    plot.axis.major_label_text_font_style="normal"
    plot.axis.axis_label_text_font_size="10pt"

    plot.axis.axis_line_color='#AAAAAA'
    plot.axis.major_tick_line_color='#AAAAAA'
    plot.axis.major_label_text_color='#666666'

    plot.axis.major_tick_line_cap="round"
    plot.axis.axis_line_cap="round"
    plot.axis.axis_line_width=1
    plot.axis.major_tick_line_width=1


def style_selection_plot(selection_plot):
    style_axis(selection_plot)
    selection_plot.min_border_bottom = selection_plot.min_border_top = 0
    selection_plot.background_fill = "white"
    selection_plot.border_fill = "white"
    selection_plot.ygrid.grid_line_color = None


source = AjaxDataSource(data_url='http://localhost:5000/data', polling_interval=1000)
p = figure(x_axis_type = "datetime", tools="pan,wheel_zoom,box_zoom,reset,hover,previewsave",
           height=500, toolbar_location='right')
p.line('Date', 'Price', color='#A6CEE3', source=source, legend='AAPL')
style_axis(p)

hover =p.select(dict(type=HoverTool))
hover.mode='vline'
hover.tooltips = OrderedDict([
    ("Date", "@Date"),
    ("Price", "$ @Price"),
    ("Date", "@DateFmt"),
])

url = "http://127.0.0.1:5000/alldata"
res = requests.get(url, timeout=20)
data = res.json()
static_source = ColumnDataSource(data)
selection_plot = figure(
    height=100, tools="box_select",
    x_axis_location="above",
    x_axis_type="datetime", toolbar_location=None,
    outline_line_color=None,
    name="small_plot"
)
selection_source = ColumnDataSource()
for k in ['end', 'values', 'start', 'bottom']:
       selection_source.add([], k)
       selection_plot.quad(top='values', bottom='bottom', left='start', right='end',
              source=selection_source, color='#c6dbef', fill_alpha=0.5)

selection_plot.line('Date', 'Price', color='#A6CEE3', source=static_source)
selection_plot.circle('Date', 'Price', color='#A6CEE3', source=static_source, size=1)

style_selection_plot(selection_plot)

# Customize select tool behaviour
select_tool = selection_plot.select(dict(type=BoxSelectTool))
select_tool.dimensions = ['width']

code = """
    if (window.xrange_base_start == undefined){
        window.xrange_base_start = main_plot.get('x_range').get('start');
    }
    if (window.xrange_base_end == undefined){
        window.xrange_base_end = main_plot.get('x_range').get('end');
    }

    data = source.get('data');
    sel = source.get('selected')['1d']['indices'];
    var mi = 1000000000;
    var ma = -100000;
    if (sel.length == 0){
       var url = "http://127.0.0.1:5000/alldata";
       source_data = selection_source.get('data');
       source_data.bottom = []
       source_data.values = [];
       source_data.start = [];
       source_data.end = [];

        // reset main plot ranges
        main_range.set('start', window.xrange_base_start);
        main_range.set('end', window.xrange_base_end);
    }else{
       for (i=0; i<sel.length; i++){
        if (mi>sel[i]){
            mi = sel[i];
        }
        if (ma<sel[i]){
            ma = sel[i];
        }
       }
       var url = "http://127.0.0.1:5000/subsample/"+data.Date[mi]+"/"+data.Date[ma];
       source_data = selection_source.get('data');
       source_data.bottom = [0]
       source_data.values = [700];
       source_data.start = [data.Date[mi]];
       source_data.end = [data.Date[ma]];

       main_range = main_plot.get('x_range');
       main_range.set('start', data.Date[mi]);
       main_range.set('end', data.Date[ma]);
    }

    xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", url, true);
    xmlhttp.send();

    selection_source.trigger('change');

"""

callback = Callback(
    args={'source': static_source,
          'selection_source': selection_source,
          'main_plot': p},
    code=code
)
static_source.callback = callback
layout = vplot(selection_plot, p)

show(layout)
