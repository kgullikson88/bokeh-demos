import logging
import os
import warnings
from collections import defaultdict

import h5py
import numpy as np
import pandas as pd

import Analyze_CCF
from GenericSmooth import roundodd
from HelperFunctions import mad, integral
import CCF_Systematics
import Fitters



class Full_CCF_Interface(object):
    """
    Interface to all of my cross-correlation functions in one class!
    """

    def __init__(self):
        # Instance variables to hold the ccf interfaces
        self._ccf_files = {'TS23': '{}/School/Research/McDonaldData/Cross_correlations/CCF.hdf5'.format(home),
                           'HET': '{}/School/Research/HET_data/Cross_correlations/CCF.hdf5'.format(home),
                           'CHIRON': '{}/School/Research/CHIRON_data/Cross_correlations/CCF.hdf5'.format(home),
                           'IGRINS': '{}/School/Research/IGRINS_data/Cross_correlations/CCF.hdf5'.format(home)}
        self._interfaces = {inst: Analyze_CCF.CCF_Interface(self._ccf_files[inst]) for inst in self._ccf_files.keys()}
        return

    def list_stars(self, print2screen=False):
        """
        List all of the stars in all of the CCF interfaces
        """
        stars = []
        for inst in self._interfaces.keys():
            if print2screen:
                print('Stars observed with {}: \n============================\n\n'.format(inst))
            stars.extend(self._interfaces[inst].list_stars(print2screen=print2screen))

        return list(pd.unique(stars))



    def get_observations(self, starname, print2screen=False):
        """
        Return a list of all observations of the given star
        :param starname:
        :return:
        """
        observations = []
        for instrument in self._interfaces.keys():
            interface = self._interfaces[instrument]
            if starname in interface.list_stars():
                for date in interface.list_dates(starname):
                    observations.append((instrument, date))
                    if print2screen:
                        print('{}   /   {}'.format(instrument, date))
        return observations


    def make_summary_df(self, instrument, starname, date, addmode='simple', read_ccf=False):
        interface = self._interfaces[instrument]
        data = interface._compile_data(starname, date, addmode=addmode, read_ccf=read_ccf)
        data['Instrument'] = instrument
        return data


    def load_ccf(self, instrument, name=None, star=None, date=None, T=None, feh=None, logg=None, vsini=None):
        """ Load the ccf from the appropriate interface. Must give either name or every other parameter

        name: The full path in the HDF5 file to the dataset. This is given in the 'name' column of the DataFrame
              returned by make_summary_df or get_ccfs
        """
        interface = self._interfaces[instrument]
        if name is not None:
            ds = interface[name]
            vel, corr = ds.value
            return vel, corr
        elif all([a is not None for a in [star, date, T, feh, logg, vsini]]):
            raise NotImplementedError
        else:
            raise ValueError('Must give either the full HDF5 path to the dataset in the name keyword, or every other parameter')

