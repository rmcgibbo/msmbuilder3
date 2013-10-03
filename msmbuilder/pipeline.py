import numpy as np
from base import BaseModeller, TransformerMixin


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


class PipelineTransformer(BaseModeller, TransformerMixin):
    """
    Transforms a trajectory or timeseries by applying a pipeline
    sequence of transformations in order, with the results of one
    feeding the input to the subsequent transformer.

    Examples
    --------
    >>> a = DistanceVectorizer([[1,2]])
    >>> b = tICA(n_components=2)

    >>> X = md.load('trajectory.h5')
    >>> features = PipelineTransformer([a, b]).transform(X)
    """

    def __init__(self, transformers):
        self.transformers = transformers

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
