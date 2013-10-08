"""Classes to build composite transformers"""

import numpy as np
from base import BaseModeller, TransformerMixin, EstimatorMixin


class MergingTransformer(BaseModeller, TransformerMixin):
    """
    Transforms a trajectory or timeseries by applying a collection of
    other transformers and stacking the results together.

    This transformer applies a series of other transformers to the input
    trajectories, giving a single set of features for each frame which might
    each be computed by a different vectorizer. For example, a
    MergingVectorizer built from a DistanceVectorizer and AngleFeaturizer
    would, when `transform`ing a trajectory, return both the calculated
    distances and angles in a single array.

    Examples
    --------
    >>> a = AngleVectorizer([[0, 1, 2]])
    >>> b = DistanceVectorizer([[1,2]])
    >>> X = md.load('trajectory.h5')
    >>> features = MergingTransformer([a, b]).transform(X)
    """

    def __init__(self, transformers):
        self.transformers = transformers

    def transform(self, X):
        """Extract features from each frame in a trajectory

        X_new : numpy array of shape [n_frames, features]
            The features for each frame, computed by applying each of the
            vectorizers and concatenating their results
        """
        return np.hstack([v.transform(X) for v in self.transformers])


class Pipeline(BaseModeller, TransformerMixin, EstimatorMixin):
    """
    Fits and/or transforms a dataset according to a sequence of
    models. The last model can be an estimator or transformer, but
    the first n - 1 models must use the TransformerMixin as the 
    outputs will be fed as input to the next model.

    Parameters
    ----------
    models : list
        list containing several models. The last can be an Estimator,
        but all models befor the last must subclass TransformerMixin

    Examples
    --------
    >>> a = DistanceVectorizer([[1,2]])
    >>> b = tICA(n_components=2)

    >>> X = md.load('trajectory.h5')
    >>> features = PipelineTransformer([a, b]).transform(X)
    """

    def __init__(self, models):
        self.models = models

    def transform(self, X):
        """
        Apply this sequence of transformations to new data

        Parameters
        ----------
        X : any
            One or more trajectories or arrays, suitable as input for the
            first transformer in the pipeline

        Returns
        -------
        X_new : numpy array of shape [n_frames, features]
            The features for each frame, computed by the chain of transformers
            operating sequentially
        """

        for t in self.transformers:
            X = t.transform(X)
        return X


    def transform_iter(self, X):
        """
        Transform an entire dataset one item at a time. 

        Parameters
        ----------
        X : Dataset, TrajectorySet, or iterable
            Dataset to iterate through. This can be a dataset, trajectoryset
            or any iterable (e.g. the result of transform_iter from another 
            model.)

        Returns
        -------
        transformed_X : iterable
            iterable over the entire dataset
        """


    def fit(self, X):
        """
        Fit the sequence of models to a dataset

        Parameters
        ----------
        X : Dataset or TrajectorySet
            Dataset or TrajectorySet to fit all estimators to. This only makes
            sense if there are models in the sequence that are estimators.

        Returns
        -------
        self
        """


    def fit_transform(self, X):
        """
        Fit the sequence of models to a dataset and then transform
        the results according to the final model

        Parameters
        ----------
        X : Dataset or TrajectorySet
            Dataset or TrajectorySet to fit the estimators to. After fitting
            all models, X will be transformed.

        Returns
        -------
        transformed_X : np.ndarray
            transformed dataset
        """

        self.fit(X)
        return self.transform(X)


