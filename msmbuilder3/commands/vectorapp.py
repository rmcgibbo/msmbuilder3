import os
import sys
import numpy as np
import mdtraj as md
import tables
from IPython.utils.traitlets import Unicode, Int, Enum, Instance

from msmbuilder3.config.app import MSMBuilderApp
from msmbuilder3.base import TransformerMixin
from msmbuilder3 import (PositionVectorizer, DistanceVectorizer,
                         AngleVectorizer, DihedralVectorizer)


class VectorApp(MSMBuilderApp):
    name = 'vector'
    path = 'msmbuilder3.commands.vectorapp.VectorApp'
    short_description = '''Transform molecular dynamics trajectories into multidimensional
                           timeseries in a suitable vector space'''
    long_description = ''
    method = Enum(['position', 'distance', 'angle', 'dihedral'], default_value='dihedral',
                  config=True, help='''The method by which we extract a multivariate feature
                  vector representation of each molecular dynamics frame. If method=='position',
                  the trajectories are aligned against a reference structure, and the cartesian
                  coordinates are used. If method=='distance', ''')
    indices = Unicode('indices.dat', config=True, help='''For method in ['distance', 'angle',
                       'dihedral'], supply a path to a file containing the indices of the atoms
                       to use for defining the pairs / triplets / quartets of atoms. This file
                       should contain a two-dimensional array of integers.''')

    vectorizer = Instance(TransformerMixin, config=False)
    def _vectorizer_default(self):
        indices = self._load_indices()
        methodmap = {'distance': DistanceVectorizer, 'angle': AngleVectorizer, 'dihedral': DihedralVectorizer}
        if self.method in methodmap:
            return methodmap[self.method](indices)

        raise NotImplementedError()

    def start(self):
        pass

    def yield_transform(self):
        if os.path.isdir(self.input):
            for file in os.listdir(self.input):
                t = md.load(os.path.join(self.input, file))
                yield self.vectorizer.transform(t)
        else:
            raise NotImplementedError()

    def _load_indices(self):
        try:
            indices = np.loadtxt(self.indices, int)
        except IOError as e:
            self.error(e)

        if self.method == 'position':
            if indices.shape[1] != 1:
                self.error('For vectorization method `positions`, each row of `%s` must contain a '
                           'single column. You supplied an array of shape %s'
                           % (self.indices, str(indices.shape)))
        elif self.method == 'distance':
            if indices.shape[1] != 2:
                self.error('For vectorization method `distance`, each row of `%s` must contain '
                           'two columns. You supplied an array of shape %s '
                           % (self.indices, indices.shape))
        elif self.method == 'angle':
            if indices.shape[1] != 3:
                self.error('For vectorization method `angle`, each row of `%s` must contain '
                           'three columns. You supplied an array of shape %s '
                           % (self.indices, indices.shape))
        elif self.method == 'dihedral':
            if indices.shape[1] != 4:
                self.error('For vectorization method `dihedral`, each row of `%s` must contain '
                           'four columns. You supplied an array of shape %s '
                           % (self.indices, indices.shape))
        return indices
