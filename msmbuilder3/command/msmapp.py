import os
import sys
import numpy as np
import mdtraj as md
import tables
from IPython.utils.traitlets import Int, Enum, Instance, Bool

from msmbuilder3.config.app import MSMBuilderApp
from .kcentersapp import KCentersApp


class MSMApp(MSMBuilderApp):
    name = 'msm'
    path = 'msmbuilder3.command.msmapp.MSMApp'
    short_description = '''Build one or more Markov state models'''
    long_description = ''
    
    lagtime = Int(1, config=True, help='''Lag-time of the Markov state model,
        in units of frames''')
    symmetry = Enum(['mle', 'transpose', 'none'], default_value='mle', config=True,
        help='''Method by which to estimate a symmetric counts matrix. Symmetrization
        ensures reversibility, but may skew dynamics. We recommend maximum likelihood
        estimation (`mle`) when tractable, else try `transpose`. It is strongly
        recommended you read the documentation surrounding this choice.''')
    trim = Bool(True, config=True, help='''Ergodic trimming ensures that the
        model is built on  only the data's maximal ergodic subgraph''')
    source = Enum(['kcenters', 'precomputed'], config=True, help='''msm takes
        as input a set of discrete-state assignments for every frame in the dataset.
        Using `kcenters`, these state assignments can be computed on-the-fly from 
        clustering your molecular dynamics trajectories, by internally building
        an instance of the `msmb kcenters` app, whose output is effectively piped
        (in unix parlance) into this app. To control the settings about how this
        clustering is done, you can pass options to the kcenters using the
        --KCentersApp.<setting>=option syntax; use --help-all for details.
        Alertnatively, using `precomputed`, you may pass in timeseries data
        that has been precalculated.''', default_value='kcenters')
    
    kcentersapp = Instance(KCentersApp, config=False)
    def _kcentersapp_default(self):
        return KCentersApp(config=self.config)
    
    def start(self):
        if self.source == 'kcenters':
            assignments = self.kcentersapp.fit_predict()
        else:
            raise NotImplementedError()

        print assignments