"""
Bokeh widget for analyzing CCF data.
"""

import os
from collections import OrderedDict
import sys
import time

from bokeh.models import ColumnDataSource, Plot, HoverTool
from bokeh.plotting import figure, curdoc
from bokeh.properties import String, Instance
from bokeh.server.app import bokeh_app
from bokeh.server.utils.plugins import object_page
from bokeh.models.widgets import HBox, VBox, VBoxForm, Select

from Analyze_CCF import CCF_Interface
from HDF5_Helpers import Full_CCF_Interface

# Parse command-line arguments 
ADDMODE = 'simple'

class BokehApp(VBox):
    extra_generated_classes = [["BokehApp", "BokehApp", "VBox"]]
    jsmodel = "VBox"

    # data sources
    main_source = Instance(ColumnDataSource)
    ccf_source = Instance(ColumnDataSource)

    # layout boxes
    mainrow = Instance(HBox)
    ccfrow = Instance(HBox)

    # plots
    mainplot = Instance(Plot)
    ccf_plot = Instance(Plot)

    # inputs
    star = String(default=u"HIP 92855")
    inst_date = String(default=u"CHIRON/20141015")
    star_select = Instance(Select)
    inst_date_select = Instance(Select)
    input_box = Instance(VBoxForm)


    def __init__(self, *args, **kwargs):
        super(BokehApp, self).__init__(*args, **kwargs)


    @classmethod
    def create(cls):
        """
        This function is called once, and is responsible for
        creating all objects (plots, datasources, etc)
        """
        # create layout widgets
        obj = cls()
        cls._ccf_interface = Full_CCF_Interface()
        obj.mainrow = HBox()
        obj.ccfrow = HBox()
        obj.input_box = VBoxForm()

        # create input widgets
        obj.set_defaults()
        obj.make_star_input()
        obj.make_inst_date_input()

        # outputs
        # obj.pretext = PreText(text="", width=500)
        obj.make_source()
        obj.make_plots()

        # layout
        obj.set_children()
        return obj

    def set_defaults(self):
        starnames = sorted(self._ccf_interface.list_stars())
        observations = self._ccf_interface.get_observations(starnames[0])
        observations = ['/'.join(obs) for obs in observations]
        self.star = starnames[0]
        self.inst_date = observations[0]


    def make_star_input(self):
        starnames = sorted(self._ccf_interface.list_stars())
        self.star_select = Select(
            name='Star',
            value=starnames[0],
            options=starnames,
        )

    def make_inst_date_input(self):
        observations = self._ccf_interface.get_observations(self.star)
        observations = ['/'.join(obs) for obs in observations]
        self.inst_date = observations[0]
        if isinstance(self.inst_date_select, Select):
            self.inst_date_select.update(value=observations[0], options=observations)
        else:
            self.inst_date_select = Select.create(
                name='Instrument/Date',
                value=observations[0],
                options=observations,
            )

    def make_source(self):
        # Get the CCF summary
        data = self.df

        # Pull out the best CCFS for each temperature
        idx = data.groupby(['T']).apply(lambda x: x['ccf_max'].idxmax())
        highest = data.iloc[idx].copy()

        # make dictionaries to turn into ColumnDataSource objects
        highest_dict = {'T': highest['T'].values,
                        'feh': highest['[Fe/H]'].values,
                        'logg': highest.logg.values,
                        'vsini': highest.vsini.values,
                        'ccf_max': highest.ccf_max.values,
                        'vel_max': highest.vel_max.values}
        ccf_dict = {'ccf': highest.ccf.values,
                    'vel': highest.vel.values,
                    'T': highest['T'].values}


        self.main_source = ColumnDataSource(data=highest_dict)
        self.ccf_source = ColumnDataSource(data=ccf_dict)


    def plot_ccf(self, T, x_range=None):
        # First, find the best values where temperature = T
        ccf_data = self.ccf_source.to_df()
        good = ccf_data.loc[ccf_data['T'] == T]
        vel, corr = good.vel.item(), good.ccf.item()

        # Now, plot
        p = figure(
            title='{} K'.format(T),
            x_range=x_range,
            plot_width=1000, plot_height=500,
            title_text_font_size="10pt",
            tools="pan,wheel_zoom,box_select,reset,save"
        )
        p.line(vel, corr, size=2,
               xlabel='Velocity', ylabel='CCF')
        p.xaxis[0].axis_label = 'Velocity (km/s)'
        p.yaxis[0].axis_label = 'CCF Power'

        return p

    def make_plots(self):
        star = self.star
        inst_date = self.inst_date
        T_run = self.main_source.to_df()
        p = figure(
            title="{} - {}".format(star, inst_date),
            plot_width=1000, plot_height=400,
            tools="pan,wheel_zoom,tap,hover,reset",
            title_text_font_size="20pt",
        )
        p.circle("T", "ccf_max",
                 size=8,
                 nonselection_alpha=1.0,
                 source=self.main_source
        )
        p.xaxis[0].axis_label = 'Temperature (K)'
        p.yaxis[0].axis_label = 'CCF Peak Value'

        hover = p.select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ("Temperature", "@T"),
            ("vsini", "@vsini"),
            ("[Fe/H]", "@feh"),
            ("log(g)", "@logg"),
            ("Radial Velocity (km/s)", "@vel_max"),
            ("ccf peak height", "@ccf_max"),
        ])
        self.mainplot = p

        T = T_run.iloc[T_run['ccf_max'].idxmax()]['T'].item()
        self.ccf_plot = self.plot_ccf(T)


    def set_children(self):
        self.children = [self.mainrow, self.ccfrow]
        # self.mainrow.children = [self.input_box, self._plot]
        self.mainrow.children = [self.input_box, self.mainplot]
        self.input_box.children = [self.star_select, self.inst_date_select]
        # self.ccfrow.children = [self._ccf_plot]
        self.ccfrow.children = [self.ccf_plot]

    def star_change(self, obj, attrname, old, new):
        print 'Star change!'
        self.star = new
        self.make_inst_date_input()
        self.make_source()
        self.make_plots()
        self.set_children()
        curdoc().add(self)

    def inst_date_change(self, obj, attrname, old, new):
        print 'Date change!'
        self.inst_date = new
        self.make_source()
        self.make_plots()
        self.set_children()
        curdoc().add(self)

    def setup_events(self):
        super(BokehApp, self).setup_events()
        # if self.source:
        #    self.source.on_change('selected', self, 'selection_change')
        if self.main_source:
            self.main_source.on_change('selected', self, 'Trun_change')
        if self.star_select:
            self.star_select.on_change('value', self, 'star_change')
        if self.inst_date_select:
            self.inst_date_select.on_change('value', self, 'inst_date_change')


    def Trun_change(self, obj, attrname, old, new):
        t1 = time.time()
        T = self.main_source.to_df().ix[new['1d']['indices']]['T'].item()
        t2 = time.time()
        logging.debug('Time to convert T_run to dataframe: {}'.format(t2 - t1))
        t1 = time.time()
        self.ccf_plot = self.plot_ccf(T)
        t2 = time.time()
        logging.debug('Time to make ccf plot: {}'.format(t2 - t1))
        self.set_children()
        curdoc().add(self)


    @property
    def df(self):
        # Parse the observation into an instrument and date
        observation = self.inst_date
        i = observation.find('/')
        instrument = observation[:i]
        date = observation[i+1:]

        # Get the CCF summary
        starname = self.star 
        return self._ccf_interface.get_ccfs(instrument, starname, date, addmode=ADDMODE)


# The following code adds a "/bokeh/stocks/" url to the bokeh-server. This URL
# will render this StockApp. If you don't want serve this applet from a Bokeh
# server (for instance if you are embedding in a separate Flask application),
# then just remove this block of code.
@bokeh_app.route("/bokeh/ccf/")
@object_page("ccf")
def make_ccf_app():
    app = BokehApp.create()
    return app
