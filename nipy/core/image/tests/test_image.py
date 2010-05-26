# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import warnings

import numpy as np

from nipy.testing import assert_true, assert_false, assert_equal, \
    assert_raises, assert_array_almost_equal, TestCase, \
    anatfile, parametric, assert_almost_equal

from nipy.core.image import image
from nipy.core.api import Image, fromarray, subsample, slice_maker
from nipy.core.api import parcels, data_generator, write_data

from nipy.core.reference.coordinate_map import AffineTransform

def setup():
    # Suppress warnings during tests to reduce noise
    warnings.simplefilter("ignore")

def teardown():
    # Clear list of warning filters
    warnings.resetwarnings()

_data = np.arange(24).reshape((4,3,2))
gimg = fromarray(_data, 'ijk', 'xyz')


def test_init():
    new = Image(np.asarray(gimg), gimg.coordmap)
    yield assert_array_almost_equal, np.asarray(gimg), np.asarray(new)
    yield assert_raises, ValueError, Image, None, None


def test_maxmin_values():
    y = np.asarray(gimg)
    yield assert_equal, y.shape, tuple(gimg.shape)
    yield assert_equal, y.max(), 23
    yield assert_equal, y.min(), 0.0


def test_slice_plane():
    x = subsample(gimg, slice_maker[1])
    yield assert_equal, x.shape, gimg.shape[1:]


def test_slice_block():
    x = subsample(gimg, slice_maker[1:3])
    yield assert_equal, x.shape, (2,) + tuple(gimg.shape[1:])


def test_slice_step():
    s = slice(0,4,2)
    x = subsample(gimg, slice_maker[s])
    yield assert_equal, x.shape, (2,) + tuple(gimg.shape[1:])


def test_slice_type():
    s = slice(0,gimg.shape[0])
    x = subsample(gimg, slice_maker[s])
    yield assert_equal, x.shape, gimg.shape


def test_slice_steps():
    dim0, dim1, dim2 = gimg.shape
    slice_z = slice(0, dim0, 2)
    slice_y = slice(0, dim1, 2)
    slice_x = slice(0, dim2, 2)
    x = subsample(gimg, slice_maker[slice_z, slice_y, slice_x])
    newshape = tuple(np.floor((np.array(gimg.shape) - 1)/2) + 1)
    yield assert_equal, x.shape, newshape


def test_array():
    x = np.asarray(gimg)
    yield assert_true, isinstance(x, np.ndarray)
    yield assert_equal, x.shape, gimg.shape
    yield assert_equal, x.ndim, gimg.ndim


def test_generator():
    gen = data_generator(gimg)
    for ind, data in gen:
        yield assert_equal, data.shape, (3,2)


def test_iter():
    imgiter = iter(gimg)
    for data in imgiter:
        yield assert_equal, data.shape, (3,2)
    tmp = Image(np.zeros(gimg.shape), gimg.coordmap)
    write_data(tmp, data_generator(gimg, range(gimg.shape[0])))
    yield assert_true, np.allclose(np.asarray(tmp), np.asarray(gimg))
    tmp = Image(np.zeros(gimg.shape), gimg.coordmap)
    g = data_generator(gimg)
    write_data(tmp, g)
    yield assert_true, np.allclose(np.asarray(tmp), np.asarray(gimg))


def test_parcels1():
    rho = gimg
    parcelmap = np.asarray(rho).astype(np.int32)
    test = np.zeros(parcelmap.shape)
    v = 0
    for i, d in data_generator(test, parcels(parcelmap)):
        v += d.shape[0]
    yield assert_equal, v, np.product(test.shape)


def test_parcels3():
    rho = subsample(gimg, slice_maker[0])
    parcelmap = np.asarray(rho).astype(np.int32)
    labels = np.unique(parcelmap)
    test = np.zeros(rho.shape)
    v = 0
    for i, d in data_generator(test, parcels(parcelmap, labels=labels)):
        v += d.shape[0]
    yield assert_equal, v, np.product(test.shape)



def test_slicing_returns_image():
    data = np.ones((2,3,4))
    img = fromarray(data, 'kji', 'zyx')
    assert isinstance(img, Image)
    assert img.ndim == 3
    # 2D slice
    img2D = subsample(img, slice_maker[:,:,0])
    assert isinstance(img2D, Image)
    assert img2D.ndim == 2
    # 1D slice
    img1D = subsample(img, slice_maker[:,0,0])
    assert isinstance(img1D, Image)
    assert img1D.ndim == 1


class ArrayLikeObj(TestCase):
    """The data attr in Image is an array-like object.
    Test the array-like interface that we'll expect to support."""
    def __init__(self):
        self._data = np.ones((2,3,4))
    
    def get_ndim(self):
        return self._data.ndim
    ndim = property(get_ndim)
        
    def get_shape(self):
        return self._data.shape
    shape = property(get_shape)

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    def __array__(self):
        return self._data

def test_ArrayLikeObj():
    obj = ArrayLikeObj()
    # create simple coordmap
    xform = np.eye(4)
    coordmap = AffineTransform.from_params('xyz', 'ijk', xform)
    
    # create image form array-like object and coordmap
    img = image.Image(obj, coordmap)
    yield assert_true, img.ndim == 3
    yield assert_true, img.shape == (2,3,4)
    yield assert_true, np.allclose(np.asarray(img), 1)
    yield assert_true, np.allclose(np.asarray(img), 1)
    img[:] = 4
    yield assert_true, np.allclose(np.asarray(img), 4)


array2D_shape = (2,3)
array3D_shape = (2,3,4)
array4D_shape = (2,3,4,5)


def test_defaults_2D():
    data = np.ones(array2D_shape)
    img = image.fromarray(data, 'kj', 'yx')
    yield assert_true, isinstance(img._data, np.ndarray)
    yield assert_true, img.ndim == 2
    yield assert_true, img.shape == array2D_shape
    yield assert_raises, AttributeError, getattr, img, 'header'
    yield assert_true, img.affine.shape == (3,3)
    yield assert_true, img.affine.diagonal().all() == 1


def test_defaults_3D():
    img = image.fromarray(np.ones(array3D_shape), 'kji', 'zyx')
    yield assert_true, isinstance(img._data, np.ndarray)
    yield assert_true, img.ndim == 3
    yield assert_true, img.shape == array3D_shape
    # ndarray's do not have a header
    yield assert_raises, AttributeError, getattr, img, 'header'
    yield assert_true, img.affine.shape == (4,4)
    yield assert_true, img.affine.diagonal().all() == 1


def test_defaults_4D():
    data = np.ones(array4D_shape)
    names = ['time', 'zspace', 'yspace', 'xspace']
    img = image.fromarray(data, names, names)
    yield assert_true, isinstance(img._data, np.ndarray)
    yield assert_true, img.ndim == 4
    yield assert_true, img.shape == array4D_shape
    yield assert_raises, AttributeError, getattr, img, 'header'
    yield assert_true, img.affine.shape == (5,5)
    yield assert_true, img.affine.diagonal().all() == 1

def test_synchronized_order():

    data = np.random.standard_normal((3,4,7,5))
    im = Image(data, AffineTransform.from_params('ijkl', 'xyzt', np.diag([1,2,3,4,1])))

    im_scrambled = im.reordered_axes('iljk').reordered_reference('xtyz')
    im_unscrambled = image.synchronized_order(im_scrambled, im)
    
    yield assert_equal, im_unscrambled.coordmap, im.coordmap
    yield assert_almost_equal, im_unscrambled.get_data(), im.get_data()
    yield assert_equal, im_unscrambled, im
    yield assert_true, im_unscrambled == im
    yield assert_false, im_unscrambled != im

    # the images don't have to be the same shape

    data2 = np.random.standard_normal((3,11,9,4))
    im2 = Image(data, AffineTransform.from_params('ijkl', 'xyzt', np.diag([1,2,3,4,1])))

    im_scrambled2 = im2.reordered_axes('iljk').reordered_reference('xtyz')
    im_unscrambled2 = image.synchronized_order(im_scrambled2, im)

    yield assert_equal, im_unscrambled2.coordmap, im.coordmap

    # or the same coordmap

    data3 = np.random.standard_normal((3,11,9,4))
    im3 = Image(data, AffineTransform.from_params('ijkl', 'xyzt', np.diag([1,9,3,-2,1])))

    im_scrambled3 = im3.reordered_axes('iljk').reordered_reference('xtyz')
    im_unscrambled3 = image.synchronized_order(im_scrambled3, im)

    yield assert_equal, im_unscrambled3.axes, im.axes
    yield assert_equal, im_unscrambled3.reference, im.reference

def test_rollaxis():
    data = np.random.standard_normal((3,4,7,5))
    im = Image(data, AffineTransform.from_params('ijkl', 'xyzt', np.diag([1,2,3,4,1])))

    # for the inverse we must specify an integer
    yield assert_raises, ValueError, image.rollaxis, im, 'i', True

    # Check that rollaxis preserves diagonal affines, as claimed

    yield assert_almost_equal, image.rollaxis(im, 1).affine, np.diag([2,1,3,4,1])
    yield assert_almost_equal, image.rollaxis(im, 2).affine, np.diag([3,1,2,4,1])
    yield assert_almost_equal, image.rollaxis(im, 3).affine, np.diag([4,1,2,3,1])

    # Check that ambiguous axes raise an exception
    # 'l' appears both as an axis and a reference coord name
    # and in different places

    im_amb = Image(data, AffineTransform.from_params('ijkl', 'xylt', np.diag([1,2,3,4,1])))
    yield assert_raises, ValueError, image.rollaxis, im_amb, 'l'

    # But if it's unambiguous, then
    # 'l' can appear both as an axis and a reference coord name

    im_unamb = Image(data, AffineTransform.from_params('ijkl', 'xyzl', np.diag([1,2,3,4,1])))
    im_rolled = image.rollaxis(im_unamb, 'l')
    yield assert_almost_equal, im_rolled.get_data(), \
        im_unamb.get_data().transpose([3,0,1,2])

    for i, o, n in zip('ijkl', 'xyzt', range(4)):
        im_i = image.rollaxis(im, i)
        im_o = image.rollaxis(im, o)
        im_n = image.rollaxis(im, n)

        yield assert_almost_equal, im_i.get_data(), \
                                  im_o.get_data()

        yield assert_almost_equal, im_i.affine, \
            im_o.affine

        yield assert_almost_equal, im_n.get_data(), \
            im_o.get_data()

        for _im in [im_n, im_o, im_i]:
            im_n_inv = image.rollaxis(_im, n, inverse=True)

            yield assert_almost_equal, im_n_inv.affine, \
                im.affine

            yield assert_almost_equal, im_n_inv.get_data(), \
                im.get_data()


