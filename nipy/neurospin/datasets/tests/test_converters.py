# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Test for the converters.
"""
import os
import nose

from .. import as_volume_img
from nipy.io import imageformats

data_file = os.path.join(imageformats.__path__[0], 'tests',
                                            'data', 'example4d.nii.gz')

def test_conversion():

    brifti_obj = imageformats.load(data_file)
    vol_img = as_volume_img(data_file)
    yield nose.tools.assert_equals, as_volume_img(vol_img), \
                    vol_img
    yield nose.tools.assert_equals, as_volume_img(brifti_obj), \
                    vol_img


def test_basics():
    yield nose.tools.assert_raises, ValueError, as_volume_img, 'foobar'


try:
    import nifti
    def test_from_nifti():
        nim = nifti.NiftiImage(data_file)
        yield nose.tools.assert_equals, as_volume_img(data_file), \
                    as_volume_img(nim)

except ImportError:
    pass

