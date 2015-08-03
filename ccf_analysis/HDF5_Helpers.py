import os
from collections import defaultdict
import logging
from scipy.interpolate import InterpolatedUnivariateSpline as spline

import h5py
import numpy as np
import pandas as pd


HOME = os.environ['HOME']

class CCF_Interface(object):
    """ Interface for an HDF5 file with my cross-correlation data in it.
    """
    def __init__(self, filename, vel=np.arange(-900, 900, 1)):
        """ Initialize the interface with the given filename. All ccfs will be
        interpolated onto the velocity grid given in the 'vel' keyword.
        """
        self.hdf5 = h5py.File(filename, 'r')
        self.velocities = vel

    def __getitem__(self, path):
        return self.hdf5[path]

    def list_stars(self, print2screen=False):
        """
        List the stars available in the HDF5 file, and the dates available for each
        :return: A list of the stars
        """
        if print2screen:
            for star in sorted(self.hdf5.keys()):
                print(star)
                for date in sorted(self.hdf5[star].keys()):
                    print('\t{}'.format(date))
        return sorted(self.hdf5.keys())


    def list_dates(self, star, print2screen=False):
        """
        List the dates available for the given star
        :param star: The name of the star
        :return: A list of dates the star was observed
        """
        if print2screen:
            for date in sorted(self.hdf5[star].keys()):
                print(date)
        return sorted(self.hdf5[star].keys())


    def _compile_data(self, starname=None, date=None, addmode='simple', read_ccf=True):
        """
        This reads in all the datasets for the given star and date.

        :param starname: the name of the star. Must be in self.hdf5
        :param date: The date to search. Must be in self.hdf5[star]
        :keyword addmode: The way the individual CCFs were added. Options are:
                          - 'simple'
                          - 'ml'
                          - 'all'  (saves all addmodes)
        :keyword read_ccf: Whether or not to read in the actual ccf, or just the metadata in 
                           the dataset attributes.

        :return: a pandas DataFrame with the columns:
                  - star
                  - date
                  - temperature
                  - log(g)
                  - [Fe/H]
                  - vsini
                  - addmode
                  - ccf_max
                  - vel_max
                  - ccf (if read_ccf == True)
        """
        if starname is None:
            df_list = []
            star_list = self.list_stars()
            for star in star_list:
                date_list = self.list_dates(star)
                for date in date_list:
                    df_list.append(self._compile_data(star, date, addmode=addmode, read_ccf=read_ccf))
            return pd.concat(df_list, ignore_index=True)
            
        elif starname is not None and date is None:
            df_list = []
            date_list = self.list_dates(starname)
            for date in date_list:
                df_list.append(self._compile_data(starname, date, addmode=addmode, read_ccf=read_ccf))
            return pd.concat(df_list, ignore_index=True)
            
        else:
            datasets = self.hdf5[starname][date].keys()
            data = defaultdict(list)
            for ds_name, ds in self.hdf5[starname][date].iteritems():  # in datasets:
                am = ds.attrs['addmode']
                if addmode == 'all' or addmode == am:
                    data['T'].append(ds.attrs['T'])
                    data['logg'].append(ds.attrs['logg'])
                    data['[Fe/H]'].append(ds.attrs['[Fe/H]'])
                    data['vsini'].append(ds.attrs['vsini'])
                    data['addmode'].append(am)
                    data['name'].append(ds.name)
                    try:
                        data['ccf_max'].append(ds.attrs['ccf_max'])
                        data['vel_max'].append(ds.attrs['vel_max'])
                    except KeyError:
                        vel, corr = ds.value
                        idx = np.argmax(corr)
                        data['ccf_max'].append(corr[idx])
                        data['vel_max'].append(vel[idx])
                        
                    if read_ccf:
                        v = ds.value
                        vel, corr = v[0], v[1]
                        fcn = spline(vel, corr)
                        data['ccf'].append(fcn(self.velocities))

            data['Star'] = [starname] * len(data['T'])
            data['Date'] = [date] * len(data['T'])
            df = pd.DataFrame(data=data)
            return df







class Full_CCF_Interface(object):
    """
    Interface to all of my cross-correlation functions in one class!
    """

    def __init__(self):
        # Instance variables to hold the ccf interfaces
        #self._ccf_files = {'TS23': '{}/School/Research/McDonaldData/Cross_correlations/CCF.hdf5'.format(HOME),
        #                   'HET': '{}/School/Research/HET_data/Cross_correlations/CCF.hdf5'.format(HOME),
        #                   'CHIRON': '{}/School/Research/CHIRON_data/Cross_correlations/CCF.hdf5'.format(HOME),
        #                   'IGRINS': '{}/School/Research/IGRINS_data/Cross_correlations/CCF.hdf5'.format(HOME)}
        self._ccf_files = {'TS23': 'data/TS23_data.h5',
                           'HET': 'data/HRS_data.h5',
                           'CHIRON', 'data/CHIRON_data.h5',
                           'IGRINS': 'data/IGRINS_data.h5'}
        self._interfaces = {inst: CCF_Interface(self._ccf_files[inst]) for inst in self._ccf_files.keys()}
        self._make_cache()
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

    def _make_cache(self, addmode='simple'):
        """ Read through all the datasets in each CCF interface, pulling the metadata.
        """
        logging.info('Reading HDF5 metadata for faster access later')
        dataframes = []
        for inst in self._interfaces.keys():
            interface = self._interfaces[inst]
            data = interface._compile_data(starname=None, date=None, addmode=addmode, read_ccf=False)
            data['Instrument'] = inst
            dataframes.append(data)

        self._cache = pd.concat(dataframes)



    def make_summary_df(self, instrument, starname, date, addmode='simple', read_ccf=False):
        cache = self._cache
        data = cache.loc[(cache.Instrument == instrument) & (cache.Star == starname) & (cache.Date == date)]
        return data 

        #interface = self._interfaces[instrument]
        #data = interface._compile_data(starname, date, addmode=addmode, read_ccf=read_ccf)
        #data['Instrument'] = instrument
        #return data


    def load_ccf(self, instrument, name=None, star=None, date=None, T=None, feh=None, logg=None, vsini=None):
        """ Load the ccf from the appropriate interface. Must give either name or every other parameter

        name: The full path in the HDF5 file to the dataset. This is given in the 'name' column of the DataFrame
              returned by make_summary_df
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

