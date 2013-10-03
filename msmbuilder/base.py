import inspect
import itertools
import tables
import numpy as np
import mdtraj as md


class BaseModeller(object):
    """Base class for all statistical modelling

    Notes
    -----
    All subclasses should specified all their parameters
    at the cass level in their __init__ as explicit keyword
    args (no *args, **kwargs)
    """

    def get_params(self):
        """Get parameters for this modeller

        Returns
        -------
        params : mapping of string to any
            Parameter names mapped to their values.
        """
        out = dict()
        for key in self._get_param_names():
            value = getattr(self, key)
            out[key] = value

        return out

    def set_params(self, **params):
        """Set the parameters of this modeller

        Returns
        -------
        self
        """
        if not params:
            return self

        valid_params = self._get_param_names()
        for key, value in params.iteritems():
            if key not in valid_params:
                raise ValueError('Invalid parameter %s for modeller %s'
                                 % (key, self.__class__.__name__))
            setattr(self, key, value)

        return self

    @classmethod
    def _get_param_names(cls):
        """Get the parameter names for this modeller"""
        try:
            init = cls.__init__
            args, varargs, kw, default = inspect.getargspec(init)
            if varargs is not None:
                raise RuntimeError("mdtraj modellers should always "
                                   "specify their parameters in the signature"
                                   " of their __init__ (no varargs)."
                                   " %s doesn't follow this convention."
                                   % (cls, ))
            # remove self
            args.pop(0)
        except TypeError:
            # no explicit __init__
            args = []
        
        args.sort()
        return args


class TransformerMixin(object):
    """Mixin class for all transformers"""

    def transform(self, X):
        """Transform a dataset X from one represenation/basis to another

        Parameters
        -----------
        X : numpy array, trajectory, list of numpy arrays, or list of trajectories
            If X is an individual array or trajectory, we transform it
            into the new space indivually. If X is a list of arrays or
            trajectories, the whole dataset is transformed, and we return a
            list of new arrays

        Returns
        -------
        X_new : numpy array of shape [n_samples, n_features_new], or list of such arrays
            Transformed data, a represenation of the input data X in the new
            space produced by this transformer
        """
        raise NotImplementedError()


class EstimatorMixin(object):
    """Mixin class for all estimators"""

    def fit(self, X):
        """Fit this vectorizer to training data

        Parameters
        ----------
        X : any
            The dataset to fit the estimator with. This dataset should
            encompas all of the data. Repeated calls to `fit` do not
            incrementally update the estimator.

        Returns
        -------
        self
        """
        return self

    def _get_estimate_names(self):
        """Each estimator object, when `fit` on a dataset, produces
        estimates which are instance variables on the class whose names
        end with an underscore, e.g. self.mean_ or self.variance_.

        Returns
        -------
        names : list of strings
             A list of the names of each of the variables currently
             estimated by this estimator.
        """
        # I'm not sure how robust this is...
        return [e for e in self.__dict__.keys() if e.endswith('_') and not e.startswith('_')]

    def to_pytables(self, parentnode):
        """Serialize this estimator to a PyTables group, attaching
        it to the parent node.

        It this estimator wraps a series of other estimators, as
        in a pipeline, it should call to_pytables on its children
        recursively.

        Parameters
        ----------
        parentnode : tables.Group
            The parent node in the HDF5 hierachy that this group
            should be attached to.
        """
        group = tables.Group(parentnode, name=self.__class__.__name__, new=True)

        # Supported types are int, float, str and numpy arrays. Atomic types (int, float, str)
        # will go in a Table named params, and numpy arrays will each go in an individual
        # Array

        params = self.get_params()
        estimates = {k: getattr(self, k) for k in self._get_estimate_names()}

        simple_typemap = {int: tables.Int64Col(), float: tables.FloatCol(), str: tables.StringCol(1024),
                          np.int64: tables.Int64Col(), np.int32: tables.Int32Col(), np.float32: tables.Float32Col(),
                          np.float64: tables.Float64Col(), bool: tables.BoolCol}

        table_description = {}
        table_entries = {}
        for key, value in itertools.chain(params.iteritems(), estimates.iteritems()):
            if value is None:
                # just skip Nones. They're indicated by their absense.
                continue
            if isinstance(value, np.ndarray):
                parentnode._v_file.create_array(group, key, obj=value)
            else:
                try:
                    table_description[key] = simple_typemap[type(value)]
                    table_entries[key] = value
                except KeyError:
                    raise RuntimeError("I don't know how to serialize the parameter %s (type=%s) to pytables" 
                                       % (key, type(value)))

        table = parentnode._v_file.create_table(group, 'params', expectedrows=1, description=table_description)
        for key, value in table_entries.iteritems():
            table.row[key] = value
        
        return group

    @classmethod
    def from_pytables(cls, group):
        """Instantiate a copy of this estimator from a pytables group.
        This performs the inverse of to_pytables.
        """

        instance = cls()
        # instance.set_params(extract parameters from group)
        # if this group contains any nested subgroups and cls
        # is some kind of meta-modeller like a pipeline, then
        # this method needs to recursively call from_pytables
        # on the subgroups, to fully instantiate instance.
        return instance


if __name__ == '__main__':
    class Test(BaseModeller, EstimatorMixin):
        def __init__(self, a=1, b='a', c=None):
            self.a = 1
            self.b = b
            self.c = c
            
        def fit(self, X):
            self.mean_ = np.array([1,2,3])
            self.mean0_ = self.mean_[1] 
            self.mean1_ = 4.0
            return self

    t = Test().fit(None)
    f = tables.open_file('f.h5', 'w')
    t.to_pytables(f.root)
    print f
    print f.root.Test.params.row[:]

    f.close()



class UpdateableEstimatorMixin(EstimatorMixin):
    def fit_update(self, X):
        """Update the statistical model described by this estimator by
        exposing it to new data, without "forgetting" the data that
        it has seen in any previous calls to `fit` or `fit_update`

        Parameters
        ----------
        X : any
            The dataset to update the estimator with.

        Returns
        -------
        self
        """
        raise NotImplementedError()

    def fit(self, X):
        """Fit this estimator to training data

        Parameters
        ----------
        X : any
            The dataset to fit the estimator with. This dataset should
            encompas all of the data. Repeated calls to `fit` do not
            incrementally update the estimator.

        Returns
        -------
        self
        """
        self.clear()
        if isinstance(X, list):
            for x in X:
                self.fit_update(x)
        else:
            self.fit_update(X)
        return self

    def clear(self):
        """Clear the state of this estimator, so that it can be refit
        on fresh data without retaining knowledge of data it has been
        previously exposed to.

        All instance variables ending in '_' (estimated quantities)
        will be set to None
        """

        for name in self.__dict__.keys():
            if name.endswith('_'):
                setattr(self, name, None)