import tables
import numpy as np
import mdtraj as md
import pandas as pd

from IPython.utils.traitlets import Unicode, Int, Enum, Instance, Bool

from msmbuilder3.config.app import MSMBuilderApp
from .vectorapp import VectorApp
from msmbuilder3 import tICA
from msmbuilder3 import DataSet


class TICAApp(MSMBuilderApp):
    name = 'tICA'
    path = 'msmbuilder3.command.ticaapp.TICAApp'
    short_description = 'Time-structure independent components analysis'
    long_description = '''Command line application for the tICA method. This
        tool can be used to train the tICA model AND/OR or use the tICA model
        to project data into a lower-dimensinonal subspace for further analysis.'''
    reference = 'Schwantes, CR and Pande, VS. JCTC, 2013, 9 (4), pp 2000-09'

    mode = Enum(['fit', 'transform', 'fit_transform'], default_value='fit_transform',
        help='''Mode in which to operate this app. When mode==`fit`, the model
        will be fit on training data and then the model itself will be saved to
        disk, with the filename given by `output`. Using `transform`, you can
        load up a pre-trained tICA model (the model will be loaded from
        `trained_path`, and use it to transform your dataset. Finally, using
        `fit_transform`, you can run both of these steps together, training 
        the model AND using it to project down your dataset.''', config=True)
    source = Enum(['vector', 'precomputed'], default_value='vector', config=True,
        help='''tICA takes as input a set of multivariate timeseries. Using
        `vector`, these timeseries can be computed on-the-fly from your
        molecular dynamics trajectories, by internally building an instance 
        of the `msmb vector` app, whose output is effectively piped (in unix
        parlance) into this app. To control the settings about how this
        vectorization is done, you can pass options to the vectorizer using
        the --VectorApp.<setting>=option syntax; use --help-all for details.
        Alertnatively, using `precomputed`, you may pass in timeseries data
        that has been precalculated.''')
    trained_path = Unicode('', config=True, help='''Path from which to load
        pre-trained tICA model. This is only used when `mode`==`transform`.''')
    n_components = Int(5, config=True, help='''Number of components to project
        onto. Thisoption is only in effect when `mode`==`transform` or
        `mode`==`fit_transform`''')
    lagtime = Int(1, config=True, help='''Lag time to use in calcualting the time
        lag correlation matrix. The units are in frames. This option is only in
        effect when `mode`==`fit` or `mode` == `fit_transform`.''')
    classes = [VectorApp]

    vectorapp = Instance(VectorApp, config=False)
    def _vectorapp_default(self):
        return VectorApp(config=self.config)
    tica = Instance(tICA, help='The compute engine', config=False)
    is_fit = Bool(False, help='Is the model currently fit?', config=False)
    input_provenance = None
    
    def start(self):
        self.fit()

        if self.mode == 'fit':
            self.log.info('Saving fit tICA model to `%s`' % self.output)
            with tables.open_file(self.output, 'w') as f:
                self.tica.to_pytables(f.root)
            return

        if self.mode in ['fit_transform', 'transform']:
            self.log.info('Writing DataSet: %s' % self.output)
            dataset = DataSet(self.output, mode='w', name='TICAApp')
            if self.source == 'precomputed':
                dataset.provenance = self.input_provenance
                
            for i, (data, fn) in enumerate(self.yield_transform(with_filenames=True)):
                 dataset[i] = data
                 dataset.set_trajfn(i, fn)
            dataset.close()
        else:
            raise RuntimeError()

    def fit(self):
        if self.mode == 'transform':
            # DONT run the fit, just load a prefitted model from disk
            with tables.open_file(self.load_from) as f:
                self.tica = tICA.from_pytables(f.root.tICA)
            self.is_fit = True
            tica.n_components = self.n_components

        else:
            self.tica = tICA(lag=self.lagtime, n_components=self.n_components)
            self.log.info('* Starting fitting of tICA model...')
            for data in self._yield_input():
                self.tica.fit_update(data)
            self.is_fit = True
            self.log.info('= Finished fitting of tICA model')

    def _yield_input(self, with_filenames=False):
        if self.source == 'vector':
            for data in self.vectorapp.yield_transform(with_filenames):
                yield data
        else:
            dataset = DataSet(self.input)
            for key in dataset.keys():
                if with_filenames:
                    yield dataset[key], dataset.get_trajfn(key)
                else:
                    yield dataset[key]
            self.input_provenance = dataset.provenance
            dataset.close()

    def yield_transform(self, with_filenames=False):
        self.log.info('*** Starting transformation of data into tIC space...')
        for row in self._yield_input(with_filenames):
            if with_filenames:
                yield self.tica.transform(row[0]), row[1]
            else:
                yield self.tica.transform(row)
        self.log.info('=== Finished transformation of data into tIC space')
