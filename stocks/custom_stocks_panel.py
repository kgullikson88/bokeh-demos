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

THEME = "default"

def style_axis(plot, theme):
    plot.axis.minor_tick_in=None
    plot.axis.minor_tick_out=None
    plot.axis.major_tick_in=None
    plot.axis.major_label_text_font_size="10pt"
    plot.axis.major_label_text_font_style="normal"
    plot.axis.axis_label_text_font_size="10pt"

    plot.axis.axis_line_width=1
    plot.axis.major_tick_line_width=1


    plot.axis.major_tick_line_cap="round"
    plot.axis.axis_line_cap="round"

    if theme == 'default':
        plot.axis.axis_line_color='#AAAAAA'
        plot.axis.major_tick_line_color='#AAAAAA'
        plot.axis.major_label_text_color='#666666'

    elif theme == 'dark':
        plot.axis.axis_line_color='#808080'
        plot.axis.major_tick_line_color='#808080'
        plot.axis.major_label_text_color='#666666'
        plot.outline_line_color = "#E6E6E6"
        plot.outline_line_alpha = 0


def style_selection_plot(selection_plot, theme='default'):
    style_axis(selection_plot, theme)
    selection_plot.min_border_bottom = selection_plot.min_border_top = 0
    selection_plot.ygrid.grid_line_color = None


    if theme == 'default':
        selection_plot.background_fill = "white"
        selection_plot.border_fill = "white"
        selection_plot.yaxis.major_label_text_color = "white"
        selection_plot.yaxis.minor_tick_line_color="white"
        selection_plot.yaxis.major_tick_line_color=None

    elif theme == 'dark':
        selection_plot.background_fill = "#333333"
        selection_plot.border_fill = "#191919"
        selection_plot.yaxis.major_label_text_color = "#191919"
        selection_plot.yaxis.minor_tick_line_color="#191919"
        selection_plot.yaxis.major_tick_line_color=None


def style_main_plot(p, theme='default'):
    style_axis(p, theme)

    if theme == 'default':
        p.background_fill = "white"
        p.border_fill = "white"

    elif theme == 'dark':
        p.background_fill = "#333333"
        p.border_fill = "#191919"
        p.grid.grid_line_color = "#4D4D4D"


source = AjaxDataSource(data_url='http://localhost:5000/data', polling_interval=1000)

# Get the data for the entire time period (so that we can use on th upper plot)
url = "http://127.0.0.1:5000/alldata"
res = requests.get(url, timeout=20)
data = res.json()

def create_main_plot(theme):
    p = figure(x_axis_type = "datetime", tools="pan,wheel_zoom,box_zoom,reset,hover,previewsave",
               height=500, toolbar_location='right')
    p.line('Date', 'Price', color='#A6CEE3', source=source)
    style_main_plot(p, theme)

    hover = p.select(dict(type=HoverTool))
    hover.mode='vline'
    hover.tooltips = OrderedDict([
     ("Date", "@Date"),
     ("Price", "$ @Price"),
     ("Date", "@DateFmt"),
    ])
    return p

def create_selection_plot(main_plot, theme):

    static_source = ColumnDataSource(data)
    selection_plot = figure(
        height=100, tools="box_select", x_axis_location="above",
        x_axis_type="datetime", toolbar_location=None,
        outline_line_color=None, name="small_plot"
    )
    selection_source = ColumnDataSource()
    for k in ['end', 'values', 'start', 'bottom']:
        selection_source.add([], k)

    if theme == 'default':
        selection_color = '#c6dbef'
    elif theme == 'dark':
        selection_color = "#FFAD5C"

    selection_plot.quad(top='values', bottom='bottom', left='start', right='end',
          source=selection_source, color=selection_color, fill_alpha=0.5)

    selection_plot.line('Date', 'Price', color='#A6CEE3', source=static_source)
    selection_plot.circle('Date', 'Price', color='#A6CEE3', source=static_source, size=1)

    style_selection_plot(selection_plot, theme)

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

        if (sel.length==0){
            $("#details_panel").addClass("hidden");
            $("#details_panel").html("");
        }else{

            var url = "http://127.0.0.1:5000/details";
            xhr = $.ajax({
                type: 'GET',
                url: url,
                contentType: "application/json",
                // data: jsondata,
                header: {
                  client: "javascript"
                }
            });

            xhr.done(function(details) {
                $("#details_panel").removeClass("hidden");
                $("#details_panel").html("<h3>Selected Region Report</h3>");
                $("#details_panel").append("<div>From " + details.start + " to " + details.end + "</div>");
                $("#details_panel").append("<div>Number of original samples " + details.original_samples_no + "</div>");
                $("#details_panel").append("<div>Number of samples " + details.samples_no + "</div>");
                $("#details_panel").append("<div>Factor " + details.factor + "</div>");
            });
        }

    """

    callback = Callback(
           args={'source': static_source,
                 'selection_source': selection_source,
                 'main_plot': main_plot},
           code=code)
    static_source.callback = callback

    return selection_plot


# Create the flask app to serve the customized panel
from flask import Flask, render_template, jsonify, request
from bokeh.embed import components
from bokeh.resources import Resources
from bokeh.templates import RESOURCES

application = Flask('Stocks_Demo')

@application.route("/")
def newapplet():
    theme = request.args.get('theme', 'default')
    INLINE = Resources(mode="inline", minified=False,)
    templname = "stocks_custom.html"

    plot_resources = RESOURCES.render(
        js_raw=INLINE.js_raw,
        css_raw=INLINE.css_raw,
        js_files=INLINE.js_files,
        css_files=INLINE.css_files,
    )

    p = create_main_plot(theme)
    plot_script, extra_divs = components(
        {
            "main_plot": p,
            "selection_plot": create_selection_plot(p, theme),
        },
        INLINE
    )
    themes = ["default", "dark"]
    options = { k: 'selected="selected"' if theme == k else "" for k in themes}

    return render_template(
        templname,
        theme = theme,
        extra_divs = extra_divs,
        plot_script = plot_script,
        plot_resources=plot_resources,
        theme_options=options,
    )

gen_config = dict(
    applet_url="http://127.0.0.1:5050",
    host='0.0.0.0',
    port=5050,
    debug=True,
)
if __name__ == "__main__":
    print("\nView this example at: %s\n" % gen_config['applet_url'])
    application.debug = gen_config['debug']
    application.run(host=gen_config['host'], port=gen_config['port'])


