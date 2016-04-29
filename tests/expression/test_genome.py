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

"""Tests for the `ExpGenome` class."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from copy import deepcopy
from collections import Iterable

import pytest

from genometools.misc import get_logger
from genometools.expression import ExpGene, ExpGenome

logger = get_logger(__name__, verbose=True)

def test_init(my_genome, my_exp_genes):
    assert isinstance(my_genome, ExpGenome)
    assert isinstance(repr(my_genome), str)
    assert isinstance(str(my_genome), str)
    assert isinstance(my_genome.hash, str)
    assert len(my_genome) == len(my_exp_genes)
    assert isinstance(my_genome, Iterable)

    genes = [eg.name for eg in my_exp_genes]
    assert my_genome.genes == genes
    assert my_genome.exp_genes == my_exp_genes

    other = deepcopy(my_genome)
    assert other is not my_genome
    assert other == my_genome

def test_from_names(my_genes):
    genome = ExpGenome.from_gene_names(my_genes)
    assert len(genome) == len(my_genes)
    for i, (g, eg) in enumerate(zip(my_genes, genome)):
        assert eg.name == g
        assert eg.chromosomes == []
        assert eg.ensembl_ids == []

def test_access(my_genome, my_exp_genes, not_my_gene):
    for i, eg in enumerate(my_exp_genes):
        assert my_genome.get_by_index(i) == eg
        assert my_genome.get_by_name(eg.name) == eg
        assert my_genome[i] == eg
        assert my_genome[eg.name] == eg
        assert my_genome.index(eg.name) == i
        assert eg in my_genome

    for i, eg in enumerate(my_genome):
        assert eg == my_exp_genes[i]

    with pytest.raises(ValueError):
        # test invalid gene name
        my_genome.get_by_name(not_my_gene)

    with pytest.raises(ValueError):
        # test invalid gene index
        my_genome.get_by_index(len(my_exp_genes))


def test_tsv(tmpdir, my_genome):
    tmp_file = str(tmpdir.join('genome.tsv'))
    # print(type(genome.exp_genes[0]))
    my_genome.write_tsv(tmp_file)
    other = ExpGenome.read_tsv(tmp_file)
    assert my_genome == other