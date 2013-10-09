Vectorizers
~~~~~~~~~~~

The vectorizers are a set of ``Transformers`` whose function is to transform
one or more molecular dynamics trajectories into a multivariate timeseries
by extracting one or more degrees of freedom from the trajectory. Oftentimes,
this involves breaking the rotational/translational symmetry of the cartesian
coordinates by extracting internal coordinates like distances, angles and 
torsions.

.. currentmodule:: msmbuilder3.flow
Vectorizers can often be the first steps as part of a :class:`Workflow` or :class:`Pipeline`.

.. currentmodule:: msmbuilder3

DistanceVectorizer
==================
.. autoclass::  DistanceVectorizer

AngleVectorizer
==================
.. autoclass::  AngleVectorizer

DihedralVectorizer
==================
.. autoclass::  DihedralVectorizer

PositionVectorizer
==================
.. autoclass::  PositionVectorizer


