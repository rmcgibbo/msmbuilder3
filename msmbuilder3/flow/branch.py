"""Classes to build estimators on multiple parameter sets"""

import numpy as np
from ..base import BaseModeller

class Branch(BaseModeller):
    """
    Fit the dataset to a single model class but with different
    parameter values. For example, this class is useful for 
    calculating implied timescales:

    Parameters
    ----------
    model : Subclass of EstimatorMixin and BaseModeller
        the class of model to fit with various parameters
    param_set : list of dicts
        the param_set represents the parameter sets to initialize
        each model. It is a list containing dicts whose keys are
        the kwargs passed to model.__init__ with iterables over
        the values of parameters we want to branch over. 
            
        For example, to construct a fan of MSMs built at different
        lag times (but the same symmetrization type) you would use 
        the following param_set

        >>> param_set = [{'symmetrize' : 'mle', 
        ...               'lag_time' : np.arange(5, 100, 5)}]
        >>> msms = Branch(MSM, param_set)
        >>> ...

    Examples
    --------

    >>> assignments = KCenters(...).transform(X)
    >>> param_set = [{'symmetrize' : ['mle'], 
                      'lag_time' : np.arange(5, 100, 5)}]
    >>> msms = Branch(MSM, param_set=param_set)
    >>> msms.fit_all(assignments)
    >>> for m in msms.iter_models():
    ...     times = - m.lag_time / np.log(m.eigenvalues_)
    ...     ...

    """

    def __init__(self, model, param_set):
        pass
    

    def fit_all(self, X):
        """
        Fit all of the models with data X

        Parameters
        ----------
        X : np.ndarray, DataSet, or TrajectorySet
            input data to fit each model on. This should be the
            type that the underlying model's fit method is 
            expecting.
    
        Returns
        -------
        self    
        """
        pass

    def iter_models(self):
        """
        Iterate over the fit models

        Returns
        -------
        model_iter : iterable
            iterable containing all models
        """
        pass
