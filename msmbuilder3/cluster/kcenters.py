import numpy as np
import mdtraj as md
import scipy.spatial.distance
from msmbuilder3.base import BaseModeller, TransformerMixin, EstimatorMixin


class KCenters(BaseModeller, EstimatorMixin):
    """
    K-Centers clustering of multivariate vector datasets

    Parameters
    ----------
    n_clusters : int
        The number of clusters to seed
    seed : int, 'random'
        The index of of the data point to use as the 0th cluster center
    precision = {'single', 'double'}

    Attributes
    ----------
    labels_ : numpy array of size [n_samples]
        The index of the cluster to which each sample belongs. These indices
        range from 0 to n_cluster-1.
    scores_ : numpy array of size [n_samples]
        The distance between each of the samples and the data point deemed the
        "center" of the clsuter to which the sample belongs.
    centers_ : numpy array of size [n_clusters, n_features]
        The data points that are deemed the centers of the clusters
    center_indices : numpy array of size [n_clusters]
        The indices, with respect to the original dataset, X, of the data
        points that have been deemed cluster centers.
    """
    def __init__(self, n_clusters, seed='random', precision='single', metric='euclidean'):
        self.n_clusters = n_clusters
        self.seed = seed
        self.precision = precision
        self.metric = metric

    def fit(self, X):
        """
        Run KCenters clustering on the dataset X

        Parameters
        ----------
        X : numpy array of shape [n_samples, n_features]
            The input dataset

        Returns
        -------
        self
        """
        dtype = {'single': np.float32, 'double': np.float64}[self.precision]
        X = md.utils.ensure_type(X, dtype, ndim=2, name='X', warn_on_cast=False)
        n_samples, n_features = X.shape

        self.scores_ = np.inf * np.ones(n_samples, dtype)
        self.labels_ = np.empty(n_samples, np.int32)
        self.centers_ = np.empty((self.n_clusters, n_features), dtype)
        self.center_indices_ = np.empty(self.n_clusters, np.int32)

        # get the index of the first cluster center
        if self.seed == 'random':
            new_center = np.random.randint(n_samples)
        else:
            new_center = seed

        for i in xrange(self.n_clusters):
            # KCenters main loop
            d = scipy.spatial.distance.cdist([X[new_center]], X, metric=self.metric)[0]
            new_assignments = np.where(d < self.scores_)[0]
            self.scores_[new_assignments] = d[new_assignments]
            self.labels_[new_assignments] = i
            self.centers_[i] = X[new_center]
            self.center_indices_[i] = new_center
            new_center = np.argmax(self.scores_)

        return self

    def fit_predict(self, X):
        """
        Run KCenters clustering on the dataset X

        Parameters
        ----------
        X : numpy array of shape [n_samples, n_features]
            The input dataset

        Returns
        -------
        labels_ : numpy array of size [n_samples]
            The index of the cluster to which each sample belongs.
            These indices range from 0 to n_cluster-1.
        """
        self.fit(X)
        return self.labels_

    def predict(self, X):
        """
        Predict the cluster labels of new data points

        Parameters
        ----------
        X_new : numpy array of shape [n_samples, n_features]
            An input dataset

        Returns
        -------
        labels : numpy array of size [n_samples]
            The index of the cluster to which each sample belongs.
            These indices range from 0 to n_cluster-1.
        """
        if not hasattr(self, 'centers_'):
            raise RuntimeError('The model must be fit before predict() can be run')
        dtype = {'single': np.float32, 'double': np.float64}[self.precision]
        X = md.utils.ensure_type(X, dtype, ndim=2, name='X', warn_on_cast=False)
        d = scipy.spatial.distance.cdist(X, self.centers_, metric=self.metric)
        return np.argmin(d, axis=1)
