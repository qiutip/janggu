import os
import pkg_resources

import numpy as np
from HTSeq import GenomicInterval
from HTSeq import BAM_Reader
from bluewhalecore.data import BwChromVector
from bluewhalecore.data import BwGenomicArray


def test_bwcv_instance_unstranded(tmpdir):
    iv = GenomicInterval('chr10', 100, 120, '.')
    BwChromVector.create(iv, 'i', 'memmap', memmap_dir=tmpdir.strpath)
    assert os.path.exists(os.path.join(tmpdir.strpath, 'chr10..nmm'))


def test_bwcv_instance_unstranded_step(tmpdir):
    iv = GenomicInterval('chr10', 100, 120, '.')
    BwChromVector.create(iv, 'i', 'step', memmap_dir=tmpdir.strpath)
    assert not os.path.exists(os.path.join(tmpdir.strpath, 'chr10..nmm'))


def test_bwcv_instance_unstranded_ndarray(tmpdir):
    iv = GenomicInterval('chr10', 100, 120, '.')
    BwChromVector.create(iv, 'i', 'ndarray', memmap_dir=tmpdir.strpath)
    assert not os.path.exists(os.path.join(tmpdir.strpath, 'chr10..nmm'))


def test_bwcv_instance_stranded(tmpdir):
    iv = GenomicInterval('chr10', 100, 120, '+')
    BwChromVector.create(iv, 'i', 'memmap', memmap_dir=tmpdir.strpath)
    assert os.path.exists(os.path.join(tmpdir.strpath, 'chr10+.nmm'))

    iv = GenomicInterval('chr10', 100, 120, '-')
    BwChromVector.create(iv, 'i', 'memmap', memmap_dir=tmpdir.strpath)
    assert os.path.exists(os.path.join(tmpdir.strpath, 'chr10-.nmm'))


def test_bwga_instance_unstranded(tmpdir):
    iv = GenomicInterval('chr10', 100, 120, '.')
    ga = BwGenomicArray({'chr10': 300}, stranded=False, typecode='int8',
                        storage='memmap', memmap_dir=tmpdir.strpath)
    np.testing.assert_equal(list(ga[iv]), [0]*20)

    ga[iv] += 1
    np.testing.assert_equal(list(ga[iv]), [1]*20)
    np.testing.assert_equal(ga[iv].aggregate(), 20)
    iv = GenomicInterval('chr10', 0, 300, '.')
    np.testing.assert_equal(ga[iv].aggregate(), 20)
    assert os.path.exists(os.path.join(tmpdir.strpath, 'chr10..nmm'))


def test_bwga_instance_stranded(tmpdir):

    iv = GenomicInterval('chr10', 100, 120, '+')
    ga = BwGenomicArray({'chr10': 300}, stranded=True, typecode='int8',
                        storage='memmap', memmap_dir=tmpdir.strpath)
    np.testing.assert_equal(list(ga[iv]), [0]*20)

    ga[iv] += 1
    np.testing.assert_equal(list(ga[iv]), [1]*20)
    np.testing.assert_equal(ga[iv].aggregate(), 20)
    iv = GenomicInterval('chr10', 0, 300, '-')
    np.testing.assert_equal(ga[iv].aggregate(), 0)
    iv = GenomicInterval('chr10', 0, 300, '+')
    np.testing.assert_equal(ga[iv].aggregate(), 20)
    assert os.path.exists(os.path.join(tmpdir.strpath, 'chr10+.nmm'))
    assert os.path.exists(os.path.join(tmpdir.strpath, 'chr10-.nmm'))


def test_bwga_instance_stranded_step(tmpdir):

    iv = GenomicInterval('chr10', 100, 120, '+')
    ga = BwGenomicArray({'chr10': 300}, stranded=True, typecode='i',
                        storage='step', memmap_dir=tmpdir.strpath)
    np.testing.assert_equal(list(ga[iv]), [0]*20)

    ga[iv] += 1
    np.testing.assert_equal(list(ga[iv]), [1]*20)
    np.testing.assert_equal(ga[iv].aggregate(), 20)
    iv = GenomicInterval('chr10', 0, 300, '-')
    np.testing.assert_equal(ga[iv].aggregate(), 0)
    iv = GenomicInterval('chr10', 0, 300, '+')
    np.testing.assert_equal(ga[iv].aggregate(), 20)
    assert not os.path.exists(os.path.join(tmpdir.strpath, 'chr10+.nmm'))
    assert not os.path.exists(os.path.join(tmpdir.strpath, 'chr10-.nmm'))


def test_bwga_instance_unstranded_step(tmpdir):
    iv = GenomicInterval('chr10', 100, 120, '.')
    ga = BwGenomicArray({'chr10': 300}, stranded=False, typecode='i',
                        storage='step', memmap_dir=tmpdir.strpath)
    np.testing.assert_equal(list(ga[iv]), [0]*20)

    ga[iv] += 1
    np.testing.assert_equal(list(ga[iv]), [1]*20)
    np.testing.assert_equal(ga[iv].aggregate(), 20)
    iv = GenomicInterval('chr10', 0, 300, '.')
    np.testing.assert_equal(ga[iv].aggregate(), 20)
    assert not os.path.exists(os.path.join(tmpdir.strpath, 'chr10..nmm'))


def test_load_bwga_bam():
    data_path = pkg_resources.resource_filename('bluewhalecore', 'resources/')
    file = os.path.join(data_path, "yeast_I_II_III.bam")

    alignment_file = BAM_Reader(file)
    cvg = BwGenomicArray("auto", stranded=True, typecode='i')
    for alngt in alignment_file:
        if alngt.aligned:
            cvg[alngt.iv] += 1

    iv = GenomicInterval("chrIII", 217330, 217350, "+")
    np.testing.assert_equal(sum(list(cvg[iv])), 34)
    np.testing.assert_equal(cvg[iv].aggregate(), 34)