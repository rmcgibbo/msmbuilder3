Data Storage and IO
===================

``mdtraj``
----------
MSMBuilder3 uses the `mdtraj <http://mdtraj.s3.amazonaws.com/index.html>`_ library for reading and writing molecular dynamics
trajectories, and can trajectories from a variety of formats, including those produced by OpenMM, AMBER, Gromacs, CHARMM and NAMD.

``VectorSet``
-------------

Most of the data created by MSMBuilder3 represents a frame-by-frame mapping of set of one or more molecular dynamics trajectories
into a new representation. For example, we might "vectorize" a set of MD trajectories into an :math:`\mathbb{R}^N` vector space
of their backbone dihedral angles using ``DihedralVectorizer``. After clustering, the state-label for each frame in the MD
dataset is also described by this pattern -- a scalar label is associated with every frame in the dataset.

These data are stored on disk by MSMBuilder using `HDF5 <http://www.hdfgroup.org/HDF5/>`_, a format developed at the National
Center for Supercomputing Applications for storing and managing large datasets. ::

  $ msmb vector --input trajectories/ --method dihedral --output torsions.h5

  $ python
  >>> from msmbuilder import VectorSet
  >>> v = VectorSet('torsions.hdf5', 'r')
  >>> print v.metadata(0)
  {'filename': 'trajectories/trj0.xtc'}
  >>> print v[0]
  array([[ 0.16912827,  0.16519609,  0.98932853, ...,  0.62335412,
         0.98725736,  0.03586039],
       [ 0.55637575,  0.35643013,  0.45544275, ...,  0.32783077,
         0.23819742,  0.21762646],
       [ 0.25537176,  0.36707719,  0.10611014, ...,  0.09790263,
         0.31351897,  0.02649133],
       ..., 
       [ 0.97825112,  0.22748027,  0.23913709, ...,  0.75260398,
         0.48195404,  0.83463672],
       [ 0.07066931,  0.21002449,  0.61627287, ...,  0.2398005 ,
         0.21588609,  0.20242959],
       [ 0.12726351,  0.0414852 ,  0.3506236 , ...,  0.16548501,
         0.85602901,  0.26830346]])
  
