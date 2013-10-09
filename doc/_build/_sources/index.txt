MSMBuilder3
~~~~~~~~~~~

MSMBuilder3 is a substantial re-write of portions of the MSMBuilder codebase,
with an effort to make a more reusable, modular, flexible, and powerful software package for modeling and understanding long-timescale conformational dynamics in molecular systems using Markov state models and associated technologies.

A More Unified and Powerful API
===============================

The MSMBuilder3 API follows closely to the pattern used by `scikit-learn <http://scikit-learn.org/stable/>`_, the highly-successful machine learning library in python. It is focused around a uniform API for statistical models. We've also been inspired by the `OpenMM <https://github.com/SimTk/openmm/>`_ python API. By providing a clean, functional and `high-level` python API, we believe we put more power in the hands of users than we do with complex scripts that require effectively turing-complete input files. If you're going to be writing complex input files or bash scripts that string together MSMBuilder calls, why not write them in a real programming language like python?

API Documentation
-----------------

.. toctree::
   :maxdepth: 3
   
   installation
   vectorizer
   reduction
   cluster
   flow
   io

Transformers
------------
Many of these models implement the  ``Transformer`` API. That is, they are capable of transforming data from one representation into another. Examples of this behavior include classes for extracting distances, angles, and torsions from molecular dynamics trajectories (``DistanceVectorizer``, ``AngleVectorizer``, ``DihedralVectorizer``), classes for performing dimensionality reduction such as principle components analysis and time-structure independent components analysis (``PCA`` and ``tICA``), and even clustering, which  transforms a dataset from some vector space into a discrete space.::

  from msmbuilder3 import DihedralVectorizer
  from mdtraj import load

  d = DihedralVectorizer(indices=[[0,1,2,3], [1,2,3,4]])
  torsions = d.transform(load('trajectory.dcd', 'topology.pdb'))

Automating Complex Workflows
----------------------------
MSM workflows typically involve building more than a single Markov state models. Generally, one wishes to explore a parameter space: we might try using many different state decompositions, dimensionality reductions, or distance metrics.

The construction of a single MSM can be expressed as a ``Pipeline``, a sequence of ``Transforms`` and statistical models that process data sequentially. For example, trajectories might first be transformed into dihedral space, and then clustered (transformed into a discrete space), before being used to parametrize a Markov state model.

When building multiple models, the set of computations is now a tree, with the trajectory data at the root at the final MSMs as leaves. Branch points in the tree correspond to steps at which we wish to "fan out", trying :math:`N` different parameter sets for the next level of the computation: we might for example build a tree of models where we try 3 different ``tICA`` settings, 4 possible numbers of states during clustering, and 10 different lag times, creating in the end :math:`3 \times 4\times 10 = 120` Markov state models.

MSMBuilder3 aims to make this common use case easy to express and efficient to calculate. Since much of the work in building these models is shared (it's only necessary to run the ``tICA`` transformation three times and the clustering 12 times) and much of the work can be performed in parallel, MSMBuilder3 provides an MPI-aware ``Workflow`` class that can efficiently build these model sets, exploiting the data dependencies and opportunities for parallelism.::

  # buildmodels.py
  from msmbuilder import DihedralVectorizer
  from msmbuilder.cluster import KCenters
  from msmbuilder import MarkovModel
  from msmbuilder.flow import Workflow, Branch

  # Build a Workflow over multiple different clustering and MSM parmaeters
  wf = Workflow([
           DihedralVectorizer(indices=[[0,1,2,3], [1,2,3,4]]), 
           Branch(KCenters,    param_grid={'n_clusters': [100, 200, 300]}),
	   Branch(MarkovModel, param_grid={'lag_time': [2, 3, 4]})
  ])

  for model in wf.iter_models():
      # these models may be fit in parallel using MPI
      print model.get_params()
      print model.timescales_[:3]

::

  $ mpirun -np 8 python buildmodels.py
  {'DihedralVectorizer.indices': [[0,1,2,3], [1,2,3,4]], 'KCenters.n_clusters': 100, 'MarkovModel.lag_time': 2}
  array([ 8.37906603,  4.09490474,  2.38560312])
  {DihedralVectorizer.indices': [[0,1,2,3], [1,2,3,4]], 'KCenters.n_clusters': 100, 'MarkovModel.lag_time': 3}
  array([ 8.35428476,  4.13811012,  2.45454261])
  {DihedralVectorizer.indices': [[0,1,2,3], [1,2,3,4]], 'KCenters.n_clusters': 100, 'MarkovModel.lag_time': 4}
  array([ 8.33006856,  4.12403202,  2.43270423])
  {DihedralVectorizer.indices': [[0,1,2,3], [1,2,3,4]], 'KCenters.n_clusters': 200, 'MarkovModel.lag_time': 2}
  array([ 8.413737  ,  4.12926038,  2.46474582])
  {DihedralVectorizer.indices': [[0,1,2,3], [1,2,3,4]], 'KCenters.n_clusters': 200, 'MarkovModel.lag_time': 3}
  array([ 8.33165184,  4.13932783,  2.44134274])
  ...


A Single Command Line Executable
================================

Each of the statistical models and transformers and transformers is accessible on the command line as a
subcommand of a single unified ``msmb`` command. This way you can see all of the available MSMBuilder
commands in one place.

In general, the approach taken by the apps is to present a 1-1 representation of the MSMBuilder statistical
models and transformers on the command line. The compound estimators like ``Pipeline``, ``Branch`` and
``Workflow`` are not available on the command line.

The Help Text
-------------
::

    $ msmb -h

    MSMBuilder: Software for building Markov State Models for Biomolecular Dynamics
    ===============================================================================

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi sed nibh ut orci
    suscipit scelerisque. Sed ligula augue, blandit ac eleifend eleifend, dapibus ac

    Subcommands
    -----------
    tICA
        Time-structure independent components analysis
    vector
        Transform molecular dynamics trajectories into multidimensional
        timeseries in a suitable vector space
    kcenters
        K-centers clustering of multivariate timeseries
    kmeans
        K-means clustering of multivariate timeseries
    markovmodel
        Parameterize a Markov state model from labeled timeseries
    

The tICA App
------------

Here's the interface supplied by, for example, the tICA application. ::

  $ msmb tICA -h

  Time-structure Independent Components Analysis
  ==============================================

  Command line application for the tICA method.

  Reference
  ---------
  Schwantes, CR and Pande, VS. JCTC, 2013, 9 (4), pp 2000-09

  tICA Options
  ------------
  --lag_time=<Int> (TICAApp.lag_time)
      Default: 1
      Lag time to use in calcualting the timelag correlation matrix. The units are
      in frames.
  --n_components=<Int> (TICApp.n_components)
      Default: 5
      Number of components to project onto. Input timeseries are projected into the
      space spaned by the first `n_components` linearly uncorrelated components.

  General Options
  ---------------
  --input=<String> (MSMBuilderApp.input)
     Path to a VectorSet from which to load input data
  --output=<String> (MSMBuilderApp.output)
     Path to a VectorSet in which to save output data


