import tables
import numpy as np
import mdtraj as md

from IPython.utils.traitlets import Unicode, Int, Enum
from msmbuilder3.config.app import MSMBuilderApp
from msmbuilder3.commands.vectorapp import VectorApp
from msmbuilder3 import tICA

class TICAApp(MSMBuilderApp):
    name = 'tICA'
    path = 'msmbuilder3.commands.ticaapp.TICAApp'
    short_description = 'Time-structure independent components analysis'
    long_description = '''Command line application for the tICA method. This tool can be used to
    train the tICA model AND/OR or use the tICA model to project data into a lower-dimensinonal
    subspace for further analysis.'''
    reference = 'Schwantes, CR and Pande, VS. JCTC, 2013, 9 (4), pp 2000-09'

    mode = Enum(['fit', 'transform', 'fit_transform'], default_value='fit_transform', help='''Mode in
    which to operate this application. When mode==`fit`, the model will be fit on training
    data and then the model itself will be saved to disk, with the filename given by `output`.
    Using `transform`, you can load up a pre-trained tICA model (the model will be loaded from
    `trained_path`, and use it to transform your dataset. Finally, using `fit_transform`, you
    can run both of these steps together, training the model AND using it to project
    down your dataset.''', config=True)
    source = Enum(['fly', 'precomputed'], default_value='fly', config=True, help='''tICA takes
    as input a set of multivariate vector timeseries. Using `fly`, these timeseries can be computed
    on-the-fly from your molecular dynamics trajectories. To controll the settings about how this
    vectorization is done, you can pass options to the vectorizer using the --Vector.<setting>=option
    syntax; use --help-all for details. Alertnatively, using `precomputed`, you may pass in
    timeseries data that has been precalculated.''')
    load_from = Unicode('', config=True, help='''Path from which to load pre-trained tICA model.
    This is only used when `mode`==`transform`.''')
    n_components = Int(5, config=True, help='''Number of components to project onto. This option is
    only in effect when `mode`==`transform` or `mode`==`fit_transform`''')
    lag = Int(1, config=True, help='''Lag time to use in calcualting the timelag correlation matrix.
    The units are in frames. This option is only in effect when `mode`==`fit` or `mode` == 
    `fit_transform`.''')
    classes = [VectorApp]

    def start(self):
        if self.mode == 'transform':
            self.log.info('Loading model from `%s`' % self.load_from)
            with tables.open_file(self.load_from) as f:
                tica = tICA.from_pytables(f.root.tICA)

            tica.n_components = self.n_components
            return self.run_transform(tica)

        else:
            self.run_fit_or_fit_transform()

    def run_fit_or_fit_transform(self):
        assert self.mode in ['fit', 'fit_transform']
        tica = tICA(lag=self.lag, n_components=self.n_components)
        self.log.info('Fitting model')
        for data in self.yield_data():
            tica.fit_update(data)

        if self.mode == 'fit':
            self.log.info('Saving fit tICA object to `%s`' % self.output)
            with tables.open_file(self.output, 'w') as f:
                tica.to_pytables(f.root)
            return
        
        if self.mode == 'fit_transform':
            self.run_transform(tica)

    def run_transform(self, tica):
        self.log.info('Running dimensnionality reduction transform')
        results = []
        for data in self.yield_data():
            results.append(tica.transform(data))
        print results

    def yield_data(self):
        if self.source == 'fly':
            v = VectorApp(config=self.config)
            transform = v.get_vectorizer().transform
            self.log.info('Loading data with on-the-fly transform into `%s` space' % v.method)
            for traj in v.yield_trajectories():
                yield transform(traj)
        else:
            raise NotImplementedError()
