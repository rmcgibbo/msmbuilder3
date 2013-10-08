"""Classes to build complex composite models"""

import numpy as np
from base import BaseModeller, TransformerMixin, EstimatorMixin

class Workflow(BaseModeller):
    """
    Analyze an entire dataset with a set of estimators and 
    transformers whose dependency graph is a directed acyclic
    graph (DAG)
    
    Parameters
    ----------
    base_models : list
        list of base models to construct the workflow. All but
        the last model must be an instance of a subclass of
        TransformerMixin

    Examples
    --------

    >>> dih = DihedralVectorizer([[0, 1, 2, 3]])
    >>> ticas = Fan(tICA, param_set=[{'lag' : [25, 50], 
    ...                               'n_components' : np.arange(1, 5)}]
    >>> clusters = Fan(KCenters, param_set=[{'num_states' : np.arange(1000, 10000, 1000)}])
    >>> msms = Fan(MSM, param_set=[{'lag_time' : np.arange(10, 100, 10), 'symmetrize' : ['mle'] }])
    >>> models = Workflow([dih, ticas, clusters, msms, models])
    >>> models.fit_all(X)
    >>> for i, m in enumerate(models.iter_models()):
    ...     m.save('model%d.h5' % i)
    ...

    """

    def __init__(self, base_models):
        pass


    def fit_all(self, X):
        """
        fit all models with some data, X

        Parameters
        ----------
        X : np.ndarray or DataSet or TrajectorySet
            input data to fit the models. the type must correspond to
            what the initial model is expecting

        Returns
        -------
        self
        """


    def models_iter(self):
        """
        iterate over all fit models
        
        Returns
        -------
        models_iter : iterable
            iterable containing all leaf models of the workflow
        """

