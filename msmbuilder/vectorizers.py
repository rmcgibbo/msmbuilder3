import numpy as np
import mdtraj as md
from .base import BaseModeller, TransformerMixin


class PositionVectorizer(BaseModeller, TransformerMixin):
    """
    Transform a molecular dynamics trajectory into a multvariate
    timeseries of the positions of specified atoms in cartesian space

    This transformer will extract the positions of the atoms in a trajectory
    after aliging (RMSD) the structure to a reference frame.

    Parameters
    ----------
    reference : Trajectry
        The structure with which to align the fit trajectories to. If
        `reference` is a trajectory containing more than one frame, only
        the first frame will be used to align structures to.
    alignment_indices : numpy array of shape [n_alignment_indices]
        The indices of the atoms with which to perform RMSD alignment. If
        both `reference` and `alignment_indices` are none, no alignment
        will be done, and the cartesian coordinates of the trajectories
        will be used *as is*.
    """

    def __init__(self, reference=None, alignment_indices=slice(None)):
        self.alignment_indices = alignment_indices
        self.reference = reference

    @property
    def _target(self):
        """_target is the cartesian coordinates of the alignment
        atoms of the first frame of the reference trajectory."""
        if not hasattr(self, '__target') or not self.__target:
            self.__target = self.reference.xyz[0, self.alignment_indices]
        return self.__target

    def transform(self, X):
        """
        Extract the positions of all of the atoms in a trajectory
        after aliging them to a reference

        Parameters
        ----------
        X : md.Trajectory
            A molecular dynamics trajectory

        Returns
        -------
        X_new : numpy array of shape [n_frames, n_atoms*3]
            `X_new[i, 3*j+d]` will contain the cartesian coordinate of the
            `i`-th frame in the `d`th dimension (x, y or z) after alignment.
        """
        if isinstance(X, list):
            return map(self._transform, X)
        return self._transform(X)

    def _transform(self, X):
        # This can be probably done more efficiently in C
        X_new = np.empty_like(X.xyz)
        for i in range(X.n_frames):
            X_new[i] = md.geometry.alignment.transform(X.xyz[i, self.alignment_indices], self._target)

        return X_new


class DistanceVectorizer(BaseModeller, TransformerMixin):
    """
    Transform a molecular dynamics trajectory into a multvariate 
    timeseris of pairwise distances between specified atoms

    This transformer turns trajectories into vectors of pairwise distances
    between specified atoms.

    Parameters
    ----------
    pair_indices : numpy_array of shape [n_distances, 2]
        Pairs of indices of the atoms between which you wish to calculate
        distances
    use_periodic_boundries : bool
        Compute distances accross periodic boundary conditions. This is used
        only when when the trajectories contain PBC information.

    Examples
    --------
    >>> X = md.load('trajectory.h5')
    >>> distances = DistanceVectorizer([[1,2]]).transform(X)
    """

    def __init__(self, pair_indices, use_periodic_boundries=False):
        self.pair_indices = pair_indices
        self.use_periodic_boundries = use_periodic_boundries

    def transform(self, X):
        """
        Extract the distance between pairs of atoms from a trajectory

        Parameters
        ----------
        X : Trajectory, or list of Trajectories
            One or more molecular dynamics trajectories

        Returns
        -------
        d : numpy array of shape [n_frames, n_distances]
            One or more arrays of pairwise distances
        """
        if isinstance(X, list):
            return map(self._transform, X)
        return self._transform(X)

    def _transform(self, X):
        return md.geometry.compute_distances(X, self.pair_indices, self.use_periodic_boundries)


class AngleVectorizer(BaseModeller, TransformerMixin):
    """
    Transform a molecular dynamics trajectory into a multivariate
    timeseries of the angles between specific atoms

    This transformer turns trajectories into vectors of angles
    between specified triplets atoms.

    Parameters
    ----------
    triplet_indices : numpy_array of shape [n_angles, 3]
        Each row of specified three indices, p0, p1, p2 of atoms. The
        calculated angle will be around the central atom, p1.

    Notes
    -----
    This vectorizer will not inspect periodic boundary conditions, and
    will give incorrect results if an angle bridges across periodic images.

    Examples
    --------
    >>> X = md.load('trajectory.h5')
    >>> distances = AngleVectorizer([[0, 1, 2]]).transform(X)
    """

    def __init__(self, triplet_indices):
        self.triplet_indices = triplet_indices

    def transform(self, X):
        """Extract the angles between atoms from a trajectory

        Parameters
        ----------
        X : Trajectory or list of Trajectories
            One or more molecular dynamics trajectories

        Returns
        -------
        d : numpy array of shape [n_frames, n_angles]
            One or more arrays of angles, in radians
        """
        if isinstance(X, list):
            return map(self._transform, X)
        return self._transform(X)
    
    def _transform(self, X):
        return md.geometry.compute_angles(X, self.triplet_indices)


class DihedralVectorizer(BaseModeller, TransformerMixin):
    """
    Transform a trajectory into a multivariate timeseries of the
    torsion angles between specific atoms

    This transformer turns trajectories into vectors of torsion angles
    between specified quartets of atoms.

    Notes
    -----
    This vectorizer will not inspect periodic boundary conditions, and
    will give incorrect results if an angle bridges across periodic images.

    Parameters
    ----------
    quartet_indices_indices : numpy_array of shape [n_dihedrals, 4]
        Each row of specifies four indices, p0, p1, p2, p3 of atoms. The
        calculated angle will be between the plane formed by atoms p0, p1,
        and p2 and the plane formed by atoms p1, p2, and p3.

    Examples
    --------
    >>> X = md.load('trajectory.h5')
    >>> distances = DihedralVectorizer([[0, 1, 2, 3]]).transform(X)
    """
    def __init__(self, quartet_indices):
        self.quartet_indices = quartet_indices

    def transform(self, X):
        """
        Extract torsion angles from a trajectory

        Parameters
        ----------
        X : Trajectory or list of trajectories
            One or more molecular dynamics trajectories

        Returns
        -------
        d : numpy array of shape [n_frames, n_dihedrals]
            One or more arrays of dihedral angles, in radians
        """
        if isinstance(X, list):
            return map(self._transform, X)
        return self._transform(X)

    def _transform(self, X):
        return md.geometry.compute_dihedrals(X, self.quartet_indices)
