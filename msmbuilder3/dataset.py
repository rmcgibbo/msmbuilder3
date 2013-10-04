"""PyTables-backed storage for data derived from mappings of molecular
dynamics trajectories
"""
# stdlib
import os
import sys
import time
import getpass
import warnings
import datetime

import tables
import numpy as np
from mdtraj.hdf5 import ensure_mode
try:
    # optional, but highly recommended
    import pandas as pd
except ImportError:
    pass

class UnrecognizedFormatError(IOError):
    pass

class DataSet(object):
    """PyTables backed storage for data derived from "mappings" of molecular
    dynamics trajectories.

    This class is designed to store lists of arrays -- `dataset[i, j]` giving
    some data entry on the `j`-th frame of the `i`-th trajectory in the
    project.
    
    Parameters
    ----------
    filename : str
        The filename to open
    mode : {'r', 'w'}
        Open the file to read ('r'), or write ('w')
    timestep : int
        In mode == 'w',
    name : str
        In mode == 'w'
    force_overwrite : bool
    compression : {'blosc', 'zlib', None}
    
    Attributes
    ----------
    provenance : pd.DataFrame
        A dataframe or (record array if you don't have pandas installed)
        containing the provenance information for this DataSet
    """

    trajectory_table = {
        'filename': tables.StringCol(1024),
        'nodename': tables.StringCol(1024),
    }

    provenance_table = {
        'user': tables.StringCol(1024),
        'timestamp': tables.StringCol(1024),
        'workdir': tables.StringCol(1024),
        'cmdline': tables.StringCol(1024),
        'executable': tables.StringCol(1024)
    }

    # List of opened datasets
    _open_datasets = []

    def __init__(self, filename, mode='r', timestep=1, name='dataset', force_overwrite=True, compression='blosc'):
        self._open = False
        self.mode = mode

        if not mode in ['r', 'w']:
            raise ValueError("mode must be one of ['r', 'w']")
        if mode == 'w' and not force_overwrite and os.path.exists(filename):
            raise IOError('"%s" already exists' % filename)

        if compression == 'blosc':
            compression = tables.Filters(complib='blosc', shuffle=True, complevel=9)
        elif compression == 'zlib':
            compression = tables.Filters(complib='zlib', shuffle=True, complevel=1)
        elif compression is None:
            compression = None
        else:
            raise ValueError("compression must be either 'zlib', 'blosc', or None")

        self._handle = tables.open_file(filename, mode=mode, filters=compression)
        self._open = True

        if self.mode == 'w':
            self._index = tables.Table(self._handle.root, 'index', self.trajectory_table, title='Index of the data group')
            self._provenance = tables.Table(self._handle.root, 'provenance', self.provenance_table, title='provenance')
            self._data = tables.Group(self._handle.root, 'data', new=True)
            self.timestep = timestep
            self.name = name
            self._appended_provenance = False
            self._handle.root._v_attrs.format = 'msmbuilder-dataset'
            self._handle.root._v_attrs.format_version = '1.0'
        else:
            if not hasattr(self._handle.root._v_attrs, 'format') or \
                    self._handle.root._v_attrs.format != 'msmbuilder-dataset':
                raise UnrecognizedFormatError('%s is not an msmbuilder dataset' % filename)
            if not hasattr(self._handle.root._v_attrs, 'format_version') or \
                    self._handle.root._v_attrs.format_version != '1.0':
                raise UnrecognizedFormatError('only msmbuilder-dataset version 1.0 is supported')
            self._index = self._handle.root.index
            self._provenance = self._handle.root.provenance
            self._data = self._handle.root.data

        self._open_datasets.append(self)

    @property
    def name(self):
        "Get the name of this dataset"
        if hasattr(self._handle.root._v_attrs, 'name'):
            return self._handle.root._v_attrs.name 
        return None

    @name.setter
    @ensure_mode('w')
    def name(self, value):
        "Set the name of this dataset. Only available when mode='w'"
        self._handle.root._v_attrs.name = value

    @property
    def timestep(self):
        return self._handle.root._v_attrs.timestep

    @timestep.setter
    def timestep(self, value):
        self._handle.root._v_attrs.timestep = value

    @property
    def provenance(self):
        if 'pandas' in sys.modules:
            return pd.DataFrame.from_records(self._provenance[:])
        return self._provenance[:]
    
    @provenance.setter
    def provenance(self, value):
        """Set the provenance table for this dataset
        """
        if 'pandas' in sys.modules and isinstance(value, pd.DataFrame):
            columns = []
            for k, v in self.provenance_table.iteritems():
                columns.append(v.recarrtype[2:])
                if k not in value:
                    value[k] = None
            formats = ','.join(columns)
            records = np.rec.fromarrays([value[x] for x in value.dtypes.keys()],
                             names=list(value.dtypes.keys()), formats=formats)
        elif isinstance(value, np.recarray):
            records = value
        else:
            raise TypeError('provenance must be a pandas DataFrame or numpy recarray')

        self._provenance.append(records)

    @ensure_mode('w')
    def __setitem__(self, key, value):
        "Set data on  the `key`-th trajectory on the dataset."
        if not np.isscalar(key) or key != int(key):
            raise TypeError('key must be an int. You supplied %s of type %s'
                            % (key, type(key)))
        if not isinstance(value, np.ndarray):
            raise TypeError('value must be a numpy array. You supplied %s of '
                            'type %s' % (value, type(value)))

        try:
            array = self._handle.get_node(self._data, name=self._node_name(key))
            array[:] = value
            new_array = False
        except tables.NoSuchNodeError:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=tables.NaturalNameWarning)
                array = self._handle.create_array(self._data, name=self._node_name(key), obj=value)
            new_array = True
            self._index.row['nodename'] = self._node_name(key)
            self._index.row.append()
            self._index.flush()

        array.flush()
        self._handle.flush()

    def __getitem__(self, key):
        if isinstance(key, tuple):
            trj_index = key[0]
            frame_index = key[1:]
            if not np.isscalar(trj_index) or trj_index != int(trj_index):
                raise IndexError('first index must be an int')
        elif int(key) == key:
            trj_index = key
            frame_index = slice(None)
        else:
            raise IndexError('index must be either an int or a sequence')

        try:
            return self._handle.get_node(self._data, self._node_name(trj_index))[frame_index]
        except tables.NoSuchNodeError:
            raise KeyError(key)
    
    def keys(self):
        return [self._key_name(e.name) for e in self._handle.iter_nodes(self._data)]

    @ensure_mode('w')
    def set_trajfn(self, key, value):
        if int(key) == key:
            trj_index = key
        else:
            raise IndexError('index must be either an int or a sequence')
        self._index.cols.filename[key] = value
        
    def get_trajfn(self, key):
        if int(key) == key:
            trj_index = key
        else:
            raise IndexError('index must be either an int or a sequence')
        return self._index[key]['filename']

    def length(self, key):
        """Get the length of a trajectory entry"""
        if int(key) == key:
            trj_index = key
        else:
            raise IndexError('index must be either an int or a sequence')

        try:
            return len(self._handle.get_node(self._data, self._node_name(trj_index)))
        except tables.NoSuchNodeError:
            raise KeyError(key)

    def close(self):
        "Close the HDF5 file handle"
        
        if self._open:
            if self.mode == 'w':
                self._append_provenance()
        
            self._handle.flush()
            self._handle.close()
            self._open = False
            if self in self._open_datasets:
                self._open_datasets.remove(self)
    
    
    # Methods for translating internally from pytables node names to the keys
    # used externally. These methods need to do the inverse of one another
    def _node_name(self, key):
        return str(key)
    def _key_name(self, node_name):
        return int(node_name)

    @ensure_mode('w')
    def _append_provenance(self):
        """Append current provence information to this file. This method is called
        automatically when datasets opened in mode='w' are closed."""
        if self._appended_provenance:
            return 
        self._provenance.row['user'] = getpass.getuser()
        self._provenance.row['timestamp'] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        self._provenance.row['workdir'] = os.path.abspath(os.curdir)
        self._provenance.row['cmdline'] = ' '.join([os.path.split(e)[1] if i==0 else e for i, e in enumerate(sys.argv)])
        self._provenance.row['executable'] = os.path.abspath(sys.argv[0])
        self._provenance.row.append()
        self._provenance.flush()
        self._appended_provenance = True

    def __del__(self):
        self.close()
        
    def __str__(self):
        return '<DataSet name=%(name)s, n_trajs=%(n_trajs)s, timestep=%(timestep)s>' \
            % {'name': self.name, 'n_trajs': len(self.keys()), 'timestep': self.timestep}
    def __repr__(self):
        return str(self)

# Close datasets when the interpreter exits.
def _close():
    for v in DataSet._open_datasets:
        v.close()
import atexit
atexit.register(_close)

if __name__ == '__main__':
    d = DataSet('assignments.h5', 'w')
    r = np.random.randn(5, 5)
    
    d[1] = r
    d[1] = r + 10
    
    provenance = pd.DataFrame([{'user': 'user1', 'workdir': 'workdir1'}, {'user': 'user2', 'workdir': 'workdir2'}])
    d.provenance = provenance
    d.close()
    # 
    d = DataSet('assignments.h5')
    print d[1]
    print d.provenance
    print d.keys()
    print d
    #print d[1]
    #print d.index()


