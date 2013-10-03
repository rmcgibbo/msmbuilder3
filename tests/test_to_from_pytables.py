import os
import tempfile
import numpy as np
import tables
from mdtraj.testing import eq
from msmbuilder3.base import BaseModeller, EstimatorMixin


fn = None
def setup():
    global fn
    fn = tempfile.mkstemp()[1]

def teardown():
    os.unlink(fn)


class MyEstimator(BaseModeller, EstimatorMixin):
    def __init__(self, c, a, b, d, e):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def fit(self, X):
        self.one_ = np.array([1,2,3])
        self.two_ = 4.0
        self.three_ = np.array([1.5, 2.5, 3.5])
        return self


def test_estimator_pytables():
    m1 = MyEstimator(a=1, b='a', c=None, d=False, e=np.zeros(3)).fit(None)

    f = tables.open_file(fn, 'w')
    m1.to_pytables(f.root)
    f.close()

    g = tables.open_file(fn)
    m2 = MyEstimator.from_pytables(g.root.MyEstimator)

    print m1.__dict__
    print m2.__dict__

    for key, value in m1.get_params().iteritems():
        if any(isinstance(value, t) for t in [int, float, str]):
            assert value == getattr(m2, key, object())
        else:
            eq(value, getattr(m2, key, object()), err_msg='error on param key=%s' % key)

    for key in m1._get_estimate_names():
        value = getattr(m1, key)
        if any(isinstance(value, t) for t in [int, float, str]):
            assert value == getattr(m2, key, object())
        else:
            eq(value, getattr(m2, key, object()), err_msg='error on estimate key=%s' % key)

    g.close()
