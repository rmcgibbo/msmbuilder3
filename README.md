MSMBuilder3
===========

MSMBuilder3 is a substantial re-write of portions of the MSMBuilder
codebase, with an effort to make a more reusable, modular, flexible, and
powerful software package for modeling and understanding long-timescale
conformational dynamics in molecular systems using Markov state models
and associated technologies.

Dataflow Model
--------------

Much of MSMBuilder3 involves manipulating molecular dynamics
trajectories by projecting individual conformations from simulation
"data" from one space into another. Clustering projects each frame from
$\mathbb{R}^{3N}$ phase space into the discrete space of clusters,
$\{1, \ldots, K\}$, where $N$ is the number of atoms in the system and
$K$ is the number of clusters. Other transformations like extracting the
backbone torsion angles from a peptide or tICA transform conformations
from one high-dimensional space into a lower dimensional space. Some
transformations project data into higher dimensional spaces, like the
construction of contact maps.

Much of the construction of a Markov state model can be expressed as a
pipeline: data starts in $\mathbb{R}^{3N}$, and may be transformed by a
variety of filters in sequence before the final statistical model is
constructed. For example, we might first extract dihedral angles, run
tICA to identify the slow components, and then cluster using these slow
components.

MSMBuilder3 makes these transformations available to you individually on
the command line, and also makes it possible to internally "pipe" the
data between steps, to construct a single "pipelined" estimator without
saving intermediate results to disk.

Examples
--------

Vectorize a trajectory by extracting backbone dihedral angles :

    $ msmb vector -h

    Transform molecular dynamics trajectories into multidimensional timeseries in a
    suitable vector space
    ===============================================================================

    vector options
    --------------
    --indices=<Unicode> (VectorApp.indices)
        Default: 'indices.dat'
        For method in ['distance', 'angle', 'dihedral'], supply a path to a file
        containing the indices of the atoms to use for defining the pairs / triplets
        / quartets of atoms. This file should contain a two-dimensional array of
        integers.
    --input=<Unicode> (MSMBuilderApp.input)
        Default: 'input'
        Input data source (file). Path to one or more timeseries or trajectory
        files.
    --method=<Enum> (VectorApp.method)
        Default: 'dihedral'
        Choices: ['position', 'distance', 'angle', 'dihedral']
        The method by which we extract a multivariate feature vector representation
        of each molecular dynamics frame. If method=='position', the trajectories
        are aligned against a reference structure, and the cartesian coordinates are
        used. If method=='distance',
    --output=<Unicode> (MSMBuilderApp.output)
        Default: 'output'
        Output data source (file). The form of the output depends on the subcommand
        invoked.

    To see all available configurables, use `--help-all`

    [VectorApp] Exiting application: vector

    $ ls trajectories/
    trj0.h5  trj1.h5

    $ cat indices.dat
    0 1 2 3
    1 2 3 4
    2 3 4 5
    3 4 5 6

    $ msmb vector --method=dihedral --indices=indices.dat --input=trajectories/ --output=dihedrals.hdf
    [VectorApp] Writing DataSet: dihedrals.hdf

    $ msmb info --input=dihedrals.hdf
    Mapped Trajectory Dataset
    =========================

    Name: VectorApp-dihedral
    Number of trajectories: 2 (from index 0 to 1)

    Provenance
    ----------
    0) 2013-10-04 17:35:19 :: rmcgibbo
      cmdline: msmb vector --method dihedral --indices indices.dat --input trajectories/ --output dihedrals.hdf
      executable: /Users/rmcgibbo/local/msmbuilder3/msmb

    Dimensionality
    --------------
    trj0 contains 501 entries of shape (4,)
         -> /Users/rmcgibbo/local/msmbuilder3/trj0.h5
    trj1 contains 501 entries of shape (4,)
         -> /Users/rmcgibbo/local/msmbuilder3/trj1.h5

Running tICA, we can project this data from a four dimensional space
into a two dimensional space :

    $ msmb tICA --source=precomputed --input=dihedrals.hdf --n_components=2
    [TICAApp] * Starting fitting of tICA model...
    [TICAApp] = Finished fitting of tICA model
    [TICAApp] Writing DataSet: output
    [TICAApp] *** Starting transformation of data into tIC space...
    [TICAApp] === Finished transformation of data into tIC space

    $ msmb info --input=tics.hdf
    Mapped Trajectory Dataset
    =========================

    Name: TICAApp
    Number of trajectories: 2 (from index 0 to 1)

    Provenance
    ----------
    0) 2013-10-04 17:35:19 :: rmcgibbo
      cmdline: msmb vector --method dihedral --indices indices.dat --input trajectories/ --output dihedrals.hdf
      executable: /Users/rmcgibbo/local/msmbuilder3/msmb
    1) 2013-10-04 17:38:51 :: rmcgibbo
      cmdline: msmb tICA --source precomputed --input dihedrals.hdf --n_components 2 --output tics.hdf
      executable: /Users/rmcgibbo/local/msmbuilder3/msmb

    Dimensionality
    --------------
    trj0 contains 501 entries of shape (2,)
         -> /Users/rmcgibbo/local/msmbuilder3/trj0.h5
    trj1 contains 501 entries of shape (2,)
         -> /Users/rmcgibbo/local/msmbuilder3/trj1.h5

We can also effectively run these two commands simultaneously, such that
the dihedral angles are computed on-the-fly. This is effectively piping
data from the `vector` app into the `tICA` app. :

    msmb tICA --input=trajectories/ --source=vector --Vector.method=dihedral --output=tica.hdf
    [TICAApp] * Starting fitting of tICA model...
    [TICAApp] = Finished fitting of tICA model
    [TICAApp] Writing DataSet: tica.hdf
    [TICAApp] *** Starting transformation of data into tIC space...
    [TICAApp] === Finished transformation of data into tIC space

### Installation

MSMBuilder3 requires a functioning scientific python distribution,
including the `numpy`, `scipy`, `pandas`, `matplotlib`, `tables` and
`ipython` packages. You'll need to install `MDTraj`, a package for
manipulating molecular dynamics trajectories. See [Installing the Scipy
Stack](http://www.scipy.org/install.html) and [Getting Started with
MDTraj](http://mdtraj.s3.amazonaws.com/getting_started.html) for
details.

Once you have the dependencies, you can install msmbuilder3 using
`python setup.py install` to add the `msmb` script to your `PATH`, or
you can run the `msmb` script directly in the source directory.
