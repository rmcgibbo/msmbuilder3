import os
import sys
import pandas as pd
import numpy as np
import tables
from IPython.utils.traitlets import Unicode, Int, Enum, Instance

from msmbuilder3.config.app import MSMBuilderApp
from msmbuilder3 import DataSet
from msmbuilder3.dataset import UnrecognizedFormatError

class InfoApp(MSMBuilderApp):
    name = 'info'
    path = 'msmbuilder3.command.infoapp.InfoApp'
    short_description = '''Inspect an msmbuilder dataset'''

    def start(self):
        if not os.path.exists(self.input):
            self.error('No such file or directory: %s' % self.input)

        if not tables.is_pytables_file(self.input):
            self.error('Unrecognized format')

        try:
            ds = DataSet(self.input, 'r')
            self.print_dataset(ds)
            ds.close()
        except UnrecognizedFormatError:
            handle = tables.open_file(self.input)
            self.print_model(handle)
            handle.close()

    def print_dataset(self, ds):
        provenance = []
        for i, line in ds.provenance.iterrows():
            rowdict = dict(zip(['cmdline', 'executable', 'timestamp', 'user', 'workdir'], line))
            rowdict['id'] = i
            provenance.append('%(id)d) %(timestamp)s :: %(user)s\n  '
                              'cmdline: %(cmdline)s\n  executable: %(executable)s\n' % rowdict)

        keys = ds.keys()

        print 'Mapped Trajectory Dataset'
        print '=========================\n'
        print 'Name: %s' % ds.name
        print 'Number of trajectories: %s (from index %s to %s)' % (len(ds.keys()), min(keys), max(keys))

        print
        print 'Provenance'
        print '----------'
        print ''.join(provenance)

        print 'Dimensionality'
        print '--------------'
        for i in range(1+min(max(keys), 5)):
            entry = ds[i, 0]
            if np.isscalar(entry):
                print 'trj%s contains %s scalar entries' % (i, ds.length(i))
            else:
                print 'trj%s contains %s entries of shape %s' % (i, ds.length(i), entry.shape)
            print '     -> %s' % ds.get_trajfn(i)


    def print_model(self, handle):

        print 'Fit Statistical Model'
        print '=====================\n'
        print handle
