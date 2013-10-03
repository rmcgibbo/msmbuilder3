import numpy as np
from msmbuilder3.base import BaseModeller, TransformerMixin
from msmbuilder3 import PipelineTransformer, MergingTransformer


def test_pipeline():
    class TransformerA(BaseModeller, TransformerMixin):
        def transform(self, X):
            return X**2
    class TransformerB(BaseModeller, TransformerMixin):
        def transform(self, X):
            return X+2

    p = PipelineTransformer([TransformerA(), TransformerB()])
    assert p.transform(10) == 10**2 + 2


def test_merge():
    class TransformerA(BaseModeller, TransformerMixin):
        def transform(self, X):
            return X**2
    class TransformerB(BaseModeller, TransformerMixin):
        def transform(self, X):
            return X**3

    m = MergingTransformer([TransformerA(), TransformerB()])
    np.testing.assert_array_equal(m.transform(2*np.ones(1)), np.array([2**2, 2**3]))
