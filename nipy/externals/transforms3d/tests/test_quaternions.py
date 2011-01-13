''' Test quaternion calculations '''

import math

import numpy as np

# Recent (1.2) versions of numpy have this decorator
try:
    from numpy.testing.decorators import slow
except ImportError:
    def slow(t):
        t.slow = True
        return t

from nose.tools import assert_raises, assert_true, assert_false, \
    assert_equal

from numpy.testing import assert_array_almost_equal, assert_array_equal

from .. import quaternions as tq

from .samples import euler_mats

# Example quaternions (from rotations)
euler_quats = []
for M in euler_mats:
    euler_quats.append(tq.mat2quat(M))
# M, quaternion pairs
eg_pairs = zip(euler_mats, euler_quats)

# Set of arbitrary unit quaternions
unit_quats = set()
params = range(-2,3)
for w in params:
    for x in params:
        for y in params:
            for z in params:
                q = (w, x, y, z)
                Nq = np.sqrt(np.dot(q, q))
                if not Nq == 0:
                    q = tuple([e / Nq for e in q])
                    unit_quats.add(q)


def test_fillpos():
    # Takes np array
    xyz = np.zeros((3,))
    w,x,y,z = tq.fillpositive(xyz)
    yield assert_true, w == 1
    # Or lists
    xyz = [0] * 3
    w,x,y,z = tq.fillpositive(xyz)
    yield assert_true, w == 1
    # Errors with wrong number of values
    yield assert_raises, ValueError, tq.fillpositive, [0, 0]
    yield assert_raises, ValueError, tq.fillpositive, [0]*4
    # Errors with negative w2
    yield assert_raises, ValueError, tq.fillpositive, [1.0]*3
    # Test corner case where w is near zero
    wxyz = tq.fillpositive([1,0,0])
    yield assert_true, wxyz[0] == 0.0


def test_conjugate():
    # Takes sequence
    cq = tq.conjugate((1, 0, 0, 0))
    # Returns float type
    yield assert_true, cq.dtype.kind == 'f'


def test_quat2mat():
    # also tested in roundtrip case below
    M = tq.quat2mat([1, 0, 0, 0])
    yield assert_array_almost_equal, M, np.eye(3)
    M = tq.quat2mat([3, 0, 0, 0])
    yield assert_array_almost_equal, M, np.eye(3)
    M = tq.quat2mat([0, 1, 0, 0])
    yield assert_array_almost_equal, M, np.diag([1, -1, -1])
    M = tq.quat2mat([0, 2, 0, 0])
    yield assert_array_almost_equal, M, np.diag([1, -1, -1])
    M = tq.quat2mat([0, 0, 0, 0])
    yield assert_array_almost_equal, M, np.eye(3)
    

def test_inverse():
    # Takes sequence
    iq = tq.inverse((1, 0, 0, 0))
    # Returns float type
    yield assert_true, iq.dtype.kind == 'f'
    for M, q in eg_pairs:
        iq = tq.inverse(q)
        iqM = tq.quat2mat(iq)
        iM = np.linalg.inv(M)
        yield assert_true, np.allclose(iM, iqM)


def test_eye():
    qi = tq.eye()
    yield assert_true, qi.dtype.kind == 'f'
    yield assert_true, np.all([1,0,0,0]==qi)
    yield assert_true, np.allclose(tq.quat2mat(qi), np.eye(3))


def test_norm():
    qi = tq.eye()
    yield assert_true, tq.norm(qi) == 1
    yield assert_true, tq.isunit(qi)
    qi[1] = 0.2
    yield assert_true, not tq.isunit(qi)


@slow
def test_mult():
    # Test that quaternion * same as matrix * 
    for M1, q1 in eg_pairs[0::4]:
        for M2, q2 in eg_pairs[1::4]:
            q21 = tq.mult(q2, q1)
            yield assert_array_almost_equal, np.dot(M2,M1), tq.quat2mat(q21)


@slow
def test_qrotate():
    vecs = np.eye(3)
    for vec in np.eye(3):
        for M, q in eg_pairs:
            vdash = tq.rotate_vector(vec, q)
            vM = np.dot(M, vec.reshape(3,1))[:,0]
            yield assert_array_almost_equal, vdash, vM


@slow
def test_quaternion_reconstruction():
    # Test reconstruction of arbitrary unit quaternions
    for q in unit_quats:
        M = tq.quat2mat(q)
        qt = tq.mat2quat(M)
        # Accept positive or negative match
        posm = np.allclose(q, qt)
        negm = np.allclose(q, -qt)
        yield assert_true, posm or negm


def test_angle_axis2quat():
    q = tq.axangle2quat([1, 0, 0], 0)
    yield assert_array_equal, q, [1, 0, 0, 0]
    q = tq.axangle2quat([1, 0, 0], np.pi)
    yield assert_array_almost_equal, q, [0, 1, 0, 0]
    q = tq.axangle2quat([1, 0, 0], np.pi, True)
    yield assert_array_almost_equal, q, [0, 1, 0, 0]
    q = tq.axangle2quat([2, 0, 0], np.pi, False)
    yield assert_array_almost_equal, q, [0, 1, 0, 0]


def sympy_aa2mat(vec, theta):
    # sympy expression derived from quaternion formulae
    v0, v1, v2 = vec # assumed normalized
    sin = math.sin
    cos = math.cos
    return np.array([
            [      1 - 2*v1**2*sin(0.5*theta)**2 - 2*v2**2*sin(0.5*theta)**2, -2*v2*cos(0.5*theta)*sin(0.5*theta) + 2*v0*v1*sin(0.5*theta)**2,  2*v1*cos(0.5*theta)*sin(0.5*theta) + 2*v0*v2*sin(0.5*theta)**2],
            [ 2*v2*cos(0.5*theta)*sin(0.5*theta) + 2*v0*v1*sin(0.5*theta)**2,       1 - 2*v0**2*sin(0.5*theta)**2 - 2*v2**2*sin(0.5*theta)**2, -2*v0*cos(0.5*theta)*sin(0.5*theta) + 2*v1*v2*sin(0.5*theta)**2],
            [-2*v1*cos(0.5*theta)*sin(0.5*theta) + 2*v0*v2*sin(0.5*theta)**2,  2*v0*cos(0.5*theta)*sin(0.5*theta) + 2*v1*v2*sin(0.5*theta)**2,       1 - 2*v0**2*sin(0.5*theta)**2 - 2*v1**2*sin(0.5*theta)**2]])


def sympy_aa2mat2(vec, theta):
    # sympy expression derived from direct formula
    v0, v1, v2 = vec # assumed normalized
    sin = math.sin
    cos = math.cos
    return np.array([
            [v0**2*(1 - cos(theta)) + cos(theta),
             -v2*sin(theta) + v0*v1*(1 - cos(theta)),
             v1*sin(theta) + v0*v2*(1 - cos(theta))],
            [v2*sin(theta) + v0*v1*(1 - cos(theta)),
             v1**2*(1 - cos(theta)) + cos(theta),
             -v0*sin(theta) + v1*v2*(1 - cos(theta))],
            [-v1*sin(theta) + v0*v2*(1 - cos(theta)),
              v0*sin(theta) + v1*v2*(1 - cos(theta)),
              v2**2*(1 - cos(theta)) + cos(theta)]])


def test_axis_angle():
    for M, q in eg_pairs:
        vec, theta = tq.quat2axangle(q)
        q2 = tq.axangle2quat(vec, theta)
        yield tq.nearly_equivalent, q, q2
        aa_mat = tq.axangle2rmat(vec, theta)
        yield assert_array_almost_equal, aa_mat, M
        aa_mat2 = sympy_aa2mat(vec, theta)
        yield assert_array_almost_equal, aa_mat, aa_mat2
        aa_mat22 = sympy_aa2mat2(vec, theta)
        yield assert_array_almost_equal, aa_mat, aa_mat22



            
