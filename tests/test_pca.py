import numpy as np
from msmbuilder3 import PCA
import sklearn.decomposition

def test_pca():
    X = np.random.randn(10,10)
    skpca = sklearn.decomposition.PCA(n_components=4)
    skpca.fit(X)

    pca = PCA(n_components=4)
    pca.fit(X)

    reference = skpca.components_
    result = pca.components_

    # make sure the components are normalized the same way
    for i in range(4):
        reference[i] = reference[i] / np.sum(reference[i])
        result[i] = result[i] / np.sum(result[i])

    np.testing.assert_array_almost_equal(result, reference)

def test_pca_fit_update():
    X = np.random.randn(100, 10)
    Y = np.random.randn(200, 10)

    skpca = sklearn.decomposition.PCA(n_components=4)
    skpca.fit(np.vstack((X, Y)))

    pca = PCA(n_components=4)
    pca.fit(X)
    pca.fit_update(Y)

    reference = skpca.components_
    result = pca.components_

    # make sure the components are normalized the same way
    for i in range(4):
        reference[i] = reference[i] / np.sum(reference[i])
        result[i] = result[i] / np.sum(result[i])

    np.testing.assert_array_almost_equal(result, reference)

