import os
import sys
import numpy as np
import mdtraj as md
import tables
from IPython.utils.traitlets import Int, Enum, Instance, Bool, List

from msmbuilder3.config.app import MSMBuilderApp
from msmbuilder3.commands.ticaapp import TICAApp
from msmbuilder3.commands.vectorapp import VectorApp
from msmbuilder3.cluster import KCenters



class KCentersApp(MSMBuilderApp):
    name = 'kcenters'
    path = 'msmbuilder3.commands.kcentersapp.KCentersApp'
    short_description = '''K-Centers clustering'''
    long_description = ''

    n_clusters = Int(100, config=True, help='Number of clusters')
    seed = Int(-1, config=True, help='''The seed serves to initialize the
        first cluster. If -1, the first cluster will be randomly chosen from
        the dataset. Otherwise, `seed` should be an integer between zero and
        one minus the number of samples in the dataset.''')
    source = Enum(['tICA', 'vector', 'precomputed'], default_value='tICA', config=True,
        help='''KCenters takes as input a set of multivariate timeseries. Using `tICA`, 
        these timeseries are computed on-the-fly by internally building an instance
        of the `msmb tICA` app, whose output is effectively piped (in unix parlance)
        into this app. To control the settings about how this tICA is done, you can
        pass options to the tICAApp using the --tICAApp.<setting>=option syntax.
        Using`vector`, the timeseries can be computed instead directly from your
        molecular dynamics trajectories, by internally building an instance of
        the `msmb vector` app. Alertnatively, using `precomputed`, you may pass in
        timeseries data that has been precalculated.''')
    mode = Enum(['fit', 'fit_predict', 'predict'], default_value='fit_predict', config=True,
        help='''Mode in which to operate this app. When mode==`fit`, the model
        will be fit on training data and then the model itself will be saved to
        disk, with the filename given by `output`. Using `transform`, you can
        load up a pre-trained kcenters model (the model will be loaded from
        `trained_path`, and use it to assign your dataset. Finally, using
        `fit_transform`, you can run both of these steps together, training
        the model AND using it to assign your dataset.''')
    classes = [VectorApp, TICAApp]


    is_fit = Bool(False, config=False, help='Is the model currently fit?', )
    breakpoints = List([0], config=False, help='''The index of the breakpoints
        between trajectories. This is necessary to reconstruct the trajectories
        in state-space, since they were concantenated together for clustering''')
    
    kcenters = Instance(KCenters, config=False)
    def _kcenters_default(self):
        seed = 'random' if self.seed < 0 else seed
        return KCenters(n_clusters=self.n_clusters, seed=seed)

    ticaapp = Instance(TICAApp, config=False)
    def _ticaapp_default(self):
        ticaapp = TICAApp(config=self.config)
        ticaapp.fit()
        return ticaapp

    vectorapp = Instance(VectorApp, config=False)
    def _vectorapp_default(self):
        return VectorApp(config=self.config)

    def start(self):
        print 'assignments'
        print self.fit_predict()

    def fit(self):
        if self.is_fit:
            return

        dataset = []
        for data in self._yield_input():
            self.breakpoints.append(sum(self.breakpoints) + len(data))
            dataset.append(data)
        dataset = np.concatenate(dataset)

        self.log.info('** Starting fitting KCenters...')
        self.kcenters.fit(dataset)
        self.log.info('** Finished fitting KCenters')
        self.is_fit = True

    def fit_predict(self):
        self.fit()
        n_trajs = len(self.breakpoints)-1
        return [self.kcenters.labels_[self.breakpoints[i]:self.breakpoints[i+1]] for i in range(n_trajs)]

    def _yield_input(self):
        if self.source == 'tICA':
            source = self.ticaapp
        elif self.source == 'vector':
            source = self.vectorapp

        for data in source.yield_transform():
            yield data
