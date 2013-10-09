Working with multiple models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. currentmodule:: msmbuilder3.flow

MSMBuilder3 aims to make the it as easy as possible to efficiently build statistical models that tie together multiple transformations and estimators. The construction of a single MSM can be expressed as a :class:`Pipeline`, a sequence of ``Transforms`` and statistical models that process data sequentially. For example, trajectories might first be transformed into dihedral space, and then clustered (transformed into a discrete space), before being used to parametrize a Markov state model.

.. currentmodule:: msmbuilder3

Sets of models that share a common data source are often built like a tree, with the trajectory data at the root at the final MSMs as leaves. Branch points in the tree correspond to steps at which we wish to "fan out", trying :math:`N` different parameter sets for the next level of the computation: we might for example build a tree of models where we try 3 different :class:`tICA` settings, 4 possible numbers of states during clustering, and 10 different lag times, creating in the end :math:`3 \times 4 \times 10 = 120` Markov state models.

.. currentmodule:: msmbuilder3.flow
Pipeline
========
.. autoclass::  Pipeline

Branch
========
.. autoclass::  Branch

Workflow
========
.. autoclass::  Workflow

