import numpy as np
from msmbuilder3.cluster import KCenters

def test_kcenters_1():
    data = np.random.randn(100,4)
    k = KCenters(10).fit(data)
    
    np.testing.assert_array_equal(k.labels_, k.predict(data))
    np.testing.assert_array_equal(k.labels_[k.center_indices_], np.arange(10))