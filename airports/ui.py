from collections import OrderedDict
from bokeh.models.tools import HoverTool, TapTool
from bokeh.models.glyphs import Circle, Patches
from bokeh.models.sources import ColumnDataSource
from bokeh.models.actions import Callback


def get_theme(theme):
    rules = {
        'map_color': "lightblue",
        'map_line_color': "lightblue",
        'connections_color': "lightgrey",
        # 'background': 'white',
        'title_text_font': '"Times New Roman", Times, serif',
        'title_text_font_style': "normal",

    }

    if theme == "creme":
        rules['map_color'] = "#8B8378"
        rules['map_line_color'] = "#8B8378"
        rules['connections_color'] = "black"

        rules['background_fill'] = '#FEFFEF'
        rules['border_fill'] = '#FEFFEF'
        rules['title_text_font'] = '"Times New Roman", Times, serif'
        rules['title_text_font_style'] = "italic"

        rules['outline_line_width'] = 7
        rules['outline_line_alpha'] = 0.3
        rules['outline_line_color'] = "#8B8378"

    return rules

def create_airport_map(plot, ap_routes, isolated_aps, theme='default'):
    import utils

    rules = get_theme(theme)
    worldmap = utils.get_worldmap()
    worldmap_src = ColumnDataSource(worldmap)

    # Using PLOTTING interface
    countries = Patches(xs='lons', ys='lats', fill_color=rules['map_color'],
                        fill_alpha='alpha', line_color=rules['map_line_color'],
                        line_width=0.5)
    countries_renderer = plot.add_glyph(worldmap_src, countries,
                                        selection_glyph=countries,
                                       nonselection_glyph=countries)

    # Using PLOTTING interface
    connections_color = rules.pop('connections_color')
    plot.multi_line('xs', 'ys', color=connections_color, line_width=1,
                    line_alpha=0.4, source=ap_routes)

    # # Using GLYPH interface
    circle = Circle(x='lng', y="lat", fill_color='color', line_color='color',
                    fill_alpha='alpha', line_alpha='alpha', radius='radius')
    isol_aps_renderer = plot.add_glyph(isolated_aps, circle, selection_glyph=circle,
                                       nonselection_glyph=circle)

    # circle = Circle(x='lng', y="lat", fill_color='color', line_color='color',
    #                 fill_alpha='alpha', line_alpha='alpha', radius='radius')
    # aps_renderer = plot.add_glyph(source_aps, circle)

    hover = plot.select(dict(type=HoverTool))
    if hover:
        hover.tooltips = OrderedDict([
            ("Name", "@name"),
        ])
        hover.renderers = [countries_renderer]

    tap = plot.select(dict(type=TapTool))
    tap.renderers = [isol_aps_renderer]

    code = """
        sel = cb_obj.get('selected')['1d'];
        sel = sel.indices;

        if (sel.length>0){
            var data = cb_obj.get('data');
            var url = "http://127.0.0.1:5050/data/update/"+data.id[parseInt(sel[0])];
            xhr = $.ajax({
                type: 'GET',
                url: url,
                contentType: "application/json",
                header: {
                  client: "javascript"
                }
            });

            xhr.done(function(details) {
                if (details.connections == 0){
                    alert("Sorry, the selected airport have no connections!");
                }

                // Fill the airport details div with the new airport info
                $("#info_wrapper").removeClass("hidden");
                $("#details_panel").html("<h3>"+details.airport.name+"</h3>");
                $("#details_panel").append("<div>City: " + details.airport.city + "</div>");
                $("#details_panel").append("<div>Country: " + details.airport.country + "</div>");
                $("#details_panel").append("<div>Number of Connections: " + details.connections + "</div>");
                $("#details_panel").append("<div>IATA: " + details.airport.iata + "</div>");
                $("#details_panel").append("<div>ICAO: " + details.airport.icao + "</div>");
                $("#details_panel").append("<div>Id: " + details.airport.id + "</div>");
                $("#details_panel").append("<div>Geolocation: " + details.airport.lng + "," + details.airport.lat + " </div>");
            });

        }

    """
    objs = {}
    tap.action = Callback(code=code, args=objs)


    plot.axis.minor_tick_in=None
    plot.axis.minor_tick_out=None
    plot.axis.major_tick_in=None
    plot.axis.major_tick_line_color = None#"#8B8378"
    plot.axis.major_label_text_color = "#8B8378"
    plot.axis.axis_line_color = None

    plot.axis.major_label_text_font_style = "italic"


    for k, v in rules.items():
        if k not in ['map_line_color', 'map_color']:
            setattr(plot, k, v)