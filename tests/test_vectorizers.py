import numpy as np
import mdtraj as md
import mdtraj.testing
from msmbuilder3 import (AngleVectorizer, DihedralVectorizer, PositionVectorizer,
                         DistanceVectorizer)

t = None
def setup():
    global t
    t = md.load(mdtraj.testing.get_fn('native.pdb'))


def test_distance_vectorizer():
    bi = [[0, 1], [3, 4,]]
    reference = md.geometry.compute_distances(t, bi)
    result = DistanceVectorizer(bi).transform(t)
    np.testing.assert_array_equal(result, reference)


def test_angle_vectorizer():
    ai = [[0,1,2], [3, 4, 5]]
    reference = md.geometry.compute_angles(t, ai)
    result = AngleVectorizer(ai).transform(t)
    np.testing.assert_array_equal(result, reference)


def test_dihedral_vectorizer():
    di = [[0,1,2, 3], [3, 4, 5, 6]]
    reference = md.geometry.compute_dihedrals(t, di)
    result = DihedralVectorizer(di).transform(t)
    np.testing.assert_array_equal(result, reference)


def test_position_vectorizer():
    reference = np.array(map(lambda xyz: md.geometry.alignment.transform(xyz, t.xyz[0]), t.xyz))
    result = PositionVectorizer(t).transform(t)
    np.testing.assert_array_equal(result, reference)



