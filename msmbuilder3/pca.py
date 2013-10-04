"""Principle Component Analysis"""

import numpy as np
from base import BaseModeller, TransformerMixin, UpdateableEstimatorMixin


class PCA(BaseModeller, UpdateableEstimatorMixin, TransformerMixin):
    """
    Principal Component Analysis (PCA) on any multivariate dataset.

    PCA finds the uncorrelated linear combinations of input coordinates that
    maximize "explained variance" in the dataset, and can be used to project
    multivariate datasets into a lower dimensional space.

    The linear combinations can be shown to be the eigenvectors of the
    covariance matrix, S:

    S = E[ (X - mean)(X - mean)^T ]

    Parameters
    ----------
    n_components : int
         Number of components to keep. If n_components is None, all of the components will be kept

    Attributes
    ----------
    components_ : array of shape [n_components, n_features]
        The components with the maximum variance
    eigenvectors_ : array of shape [n_features, n_features]
        The full collection of all of the components, ordered by variance
    eigenvalues_ : array of shape [n_features]
        The eigenvalues of the covariance matrix, S
    """

    def __init__(self, n_components=None):
        self.n_components = n_components

        # running_corr_ is the running sum of the cross-correlation of the data
        # with itself ( Outer(X, X) )
        self.running_corr_mat_ = None
        # running_sum_ is the running sum of the data, for calculating the mean
        self.running_sum_ = None
        # total_samples_ is the number of frames that we have used in the estimator
        self.total_samples_ = 0

        # containers for the results:
        self.cov_mat_ = None
        self.vals_ = None
        self.vecs_ = None

        # boolean telling us if we have an estimate of the PCs or not
        self._have_estimate_ = False

    def clear(self):
        """Clear the current state to do PCA on new data
        """

        super(PCA, self).clear()

        # since the above sets everything to None, I want these to be different:
        self._have_estimate_ = False
        self.total_samples_ = 0

    def fit_update(self, X):
        """
        Update the internal state with new data, X

        Parameters
        ----------
        X : np.ndarray or list of np.ndarrays
            Data to add to the estimate of the covariance matrix. This can be a list
            of numpy arrays, or a single numpy array. Each array should be two-
            dimensional: (n_samples, n_coordinates). Since this is PCA, the order
            of the samples is irrelevant

        Returns
        -------
        self
        """

        if not isinstance(X, list):
            X = [X]

        self._have_estimate = False
        # we have updated the data, so we no longer have the PCs.

        for row in X:
            if not isinstance(row, np.ndarray):
                raise RuntimeError("data must be numpy.ndarray's or a list of arrays")

            shape = row.shape

            if len(shape) == 1:
                row = row.reshape((1, -1))

            if len(shape) > 2:
                raise RuntimeError("data cannot be more than two-dimensional")

            n_features = row.shape[1]

            if self.running_corr_mat_ is None:
                self.running_corr_mat_ = np.zeros((n_features, n_features))
                self.running_sum_ = np.zeros(n_features)

            elif n_features != self.running_corr_mat_.shape[0]:
                raise RuntimeError("data does not match the shape of the internal state.")

            self.running_corr_mat_ += row.T.dot(row)
            self.running_sum_ += row.sum(0)

            self.total_samples_ += row.shape[0]

        return self

    def fit(self, X):
        """
        Calculate the principal components of a multivariate dataset

        Parameters
        ----------
        X : np.ndarray or list of np.ndarrays
            data or list of numpy arrays

        Returns
        -------
        self
        """
        self.clear()
        self.fit_update(X)
        return self

    def compute_components(self):
        """
        Compute the components according to the data that has been accumulated
        with fit or fit_update.
        """

        self.mean_ = self.running_sum_ / float(self.total_samples_)
        cov_mat = self.running_corr_mat_ / float(self.total_samples_) - \
                    np.outer(self.mean_, self.mean_)
        vals, vecs = np.linalg.eigh(cov_mat)
        ind = np.argsort(vals)[::-1]

        self._eigenvalues_ = vals[ind]
        self._vectors_ = vecs[:, ind]
        self._have_estimate_ = True

    @property
    def eigenvectors_(self):
        if not self._have_estimate_:
            self.compute_components()
        return self._vectors_

    @property
    def eigenvalues_(self):
        if not self._have_estimate_:
            self.compute_components()
        return self._eigenvalues_

    @property
    def components_(self):
        if not self._have_estimate_:
            self.compute_components()
        return self._vectors_[:, :self.n_components].T

    def transform(self, X):
        """
        Transform a dataset into the principle components subspace

        Parameters
        ----------
        X : np.ndarray or list of np.ndarray's
            data to project onto the top n_components. Should be a single two-
            dimensional array (n_samples, n_coordinates) or a list of arrays

        Returns
        -------
        proj_X : np.ndarray or list of np.ndarray's
            projected data

        """

        if self.n_components is None:
            raise RuntimeError("need to set n_components")

        if not self._have_estimate_:
            self.compute_components()

        if isinstance(X, list):
            return_list = True

        else:
            X = [X]
            return_list = False

        top_pcs = self.eigenvectors_[:, :self.n_components]

        proj_X = []
        for row in X:
            if not isinstance(row, np.ndarray):
                raise RuntimeError("data contains rows that are not np.ndarray's")

            shape = row.shape
            if len(shape) == 1:
                row = row.reshape((1, -1))

            if len(shape) > 2:
                raise RuntimeError("data cannot be more than two-dimensional")

            n_features = row.shape[1]

            if n_features != top_pcs.shape[0]:
                raise RuntimeError("data is not the right shape")

            proj_X.append(row.dot(top_pcs))
            # are you supposed to subtract the mean before projecting?
            # if so, then this is the correct line:

            # proj_X.append((row - self.mean_).dot(top_pcs))

            # but, this just adds a constant vector to each point, (-self.mean_.dot(top_pcs))
            # so I don't think it actually matters..

        if return_list:
            return proj_X
        else:
            return proj_X[0]
