# Copyright (c) 2016 Florian Wagner
#
# This file is part of GenomeTools.
#
# GenomeTools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License, Version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Tests for the `ExpProfile` class."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import pytest
import numpy as np

from genometools.expression import ExpProfile, ExpMatrix


@pytest.fixture(scope='session')
def my_label():
    return 'sample'


@pytest.fixture
def my_profile(my_genes, my_label, my_x):
    prof = ExpProfile(genes=my_genes, label=my_label, x=my_x)
    return prof


@pytest.fixture
def my_profile2(my_genes, my_x):
    prof= ExpProfile(genes=my_genes, label=None, x=my_x)
    return prof


def test_init(my_profile, my_profile2, my_genes, my_x):
    for prof in [my_profile, my_profile2]:
        assert isinstance(prof, ExpProfile)
        assert isinstance(repr(prof), str)
        assert isinstance(str(prof), str)
        assert isinstance(prof.hash, str)
        assert prof.p == len(my_genes)
        assert np.all(prof.x == my_x)
        assert prof.genes == my_genes
    assert my_profile != my_profile2
    assert my_profile.label != my_profile2.label


def test_expanddim(my_profile):
    matrix = my_profile.to_frame()
    assert isinstance(matrix, ExpMatrix)


def test_tsv(tmpdir, my_profile):
    tmp_file = tmpdir.join('expression_profile.tsv').strpath
    my_profile.write_tsv(tmp_file)
    other = ExpProfile.read_tsv(tmp_file)
    assert other == my_profile


def test_copy(my_profile, my_genes, my_x):
    prof = my_profile.copy()
    assert prof is not my_profile
    assert prof.hash == my_profile.hash
    assert prof == my_profile
    prof.genes = my_genes
    prof.x = my_x
    assert prof == my_profile


def test_sort(my_profile):
    prof = my_profile.copy()
    prof.sort_genes(inplace=True)
    print(np.lexsort([prof.genes]) == np.arange(prof.p))
    assert np.all(np.lexsort([prof.genes]) == np.arange(prof.p))


def test_filter(my_profile, my_genome):
    print(my_genome.genes)
    prof = my_profile.filter_against_genome(my_genome)
    assert prof == my_profile