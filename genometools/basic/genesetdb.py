# Copyright (c) 2015, 2016 Florian Wagner
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

"""Module containing the `GeneSetDB` class.

Class supports unicode using UTF-8.

"""

import os
import io
import logging
from collections import OrderedDict

import xmltodict
import unicodecsv as csv

from . import GeneSet

logger = logging.getLogger(__name__)

class GeneSetDB(object):
    """A gene set database.

    This is a class that basically just contains a list of gene sets, and
    supports different ways of accessing individual gene sets. The gene sets
    are ordered, so each gene set has a unique position (index) in the
    database.

    Parameters
    ----------
    gene_sets: list or tuple of `GeneSet`
        See :attr:`gene_sets` attribute.

    Attributes
    ----------
    gene_sets: tuple of `GeneSet`
        The list of gene sets in the database. Note that this is a read-only
        property.
    """
    def __init__(self, gene_sets):
        
        assert isinstance(gene_sets, (list, tuple))
        for gs in gene_sets:
            assert isinstance(gs, GeneSet)

        self._gene_sets = OrderedDict([gs.id, gs] for gs in gene_sets)
        self._gene_set_ids = tuple(self._gene_sets.keys())
        self._gene_set_indices = OrderedDict([gs.id, i]
                for i, gs in enumerate(self._gene_sets.itervalues()))

    def __repr__(self):
        return '<%s object (n=%d; hash=%d)>' \
                %(self.__class__.__name__, self.n, hash(self))

    def __str__(self):
        return '<%s object (n=%d)>' %(self.__class__.__name__, self.n)

    def __getitem__(self, key):
        """Simple interface for querying the database.

        Depending on whether key is an integer or not, look up a gene set
        either by index, or by ID.
        """
        if isinstance(key, int):
            return self.get_by_index(key)
        else:
            return self.get_by_id(key)

    def __eq__(self, other):
        if self is other:
            return True
        elif type(self) != type(other):
            return False
        else:
            return repr(self) == repr(other)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(tuple(self.gene_sets))

    @property
    def gene_sets(self):
        return tuple(self._gene_sets.values())

    @property
    def n(self):
        """The number of gene sets in the database."""
        return len(self._gene_sets)

    def get_by_id(self, id_):
        """Look up a gene set by its ID.

        Parameters
        ----------
        id_: str or unicode
            The ID of the gene set.

        Returns
        -------
        GeneSet
            The gene set.

        Raises
        ------
        ValueError
            If the given ID is not in the database.
        """
        try:
            return self._gene_sets[id_]
        except KeyError:
            raise ValueError('No gene set with ID "%s"!' %(id_))

    def get_by_index(self, i):
        """Look up a gene set by its index.

        Parameters
        ----------
        i: int
            The index of the gene set.

        Returns
        -------
        GeneSet
            The gene set.

        Raises
        ------
        ValueError
            If the given index is out of bounds.
        """
        if i >= self.n:
            raise ValueError('Index %d out of bounds ' %(i) +
                    'for database with %d gene sets.' %(self.n))
        return self._gene_sets[self._gene_set_ids[i]]

    def index(self, id_):
        """Get the index corresponding to a gene set, identified by its ID.

        Parameters
        ----------
        id_: str or unicode
            The ID of the gene set.

        Returns
        -------
        int
            The index of the gene set.

        Raises
        ------
        ValueError
            If the given ID is not in the database.
        """
        try:
            return self._gene_set_indices[id_]
        except KeyError:
            raise ValueError('No gene set with ID "%s"!' %(id_))

    @classmethod
    def read_tsv(cls, path, encoding = 'utf-8'):
        """Read a gene set database from a tab-delimited text file.

        Parameters
        ----------
        path: str or unicode
            The path name of the the file.

        Returns
        -------
        None
        """
        gene_sets = []
        n = 0
        with open(path, 'rb') as fh:
            reader = csv.reader(fh, dialect = 'excel-tab',
                                encoding = encoding)
            for l in reader:
                n += 1
                gs = GeneSet.from_list(l)
                gene_sets.append(gs)
        logger.debug('Read %d gene sets.', n)
        logger.debug('Size of gene set list: %d', len(gene_sets))
        return cls(gene_sets)

    def write_tsv(self, path):
        """Write the database to a tab-delimited text file.

        Parameters
        ----------
        path: str or unicode
            The path name of the file.

        Returns
        -------
        None
        """
        with open(path, 'wb') as ofh:
            writer = csv.writer(ofh, dialect = 'excel-tab',
                quoting = csv.QUOTE_NONE, lineterminator = os.linesep)
            for gs in self._gene_sets.itervalues():
                writer.writerow(gs.to_list())

    @classmethod
    def read_msigdb_xml(cls, path, entrez2gene, species = None):
        """Read the complete MSigDB database from an XML file.

        The XML file can be downloaded from here:
        http://software.broadinstitute.org/gsea/msigdb/download_file.jsp?filePath=/resources/msigdb/5.0/msigdb_v5.0.xml

        Parameters
        ----------
        path: str or unicode
            The path name of the XML file.
        entrez2gene: dict or OrderedDict (str: unicode or str)
            A dictionary mapping Entrez Gene IDs to gene symbols (names).
        species: str or unicode, optional
            A species name (e.g., "Homo_sapiens"). Only gene sets for that
            species will be retained. (None)

        Returns
        -------
        GeneSetDB
            The gene set database containing the MSigDB gene sets.
        """
        assert isinstance(path, (str, unicode))
        assert isinstance(entrez2gene, (dict, OrderedDict))
        assert species is None or isinstance(species, (str, unicode))

        logger.debug('Path: %s', path)
        logger.debug('entrez2gene type: %s', str(type(entrez2gene)))

        i = [0]
        gene_sets = []

        total_gs = [0]
        total_genes = [0]

        species_excl = [0]
        unknown_entrezid = [0]

        src = 'MSigDB'

        def handle_item(pth, item):
            # callback function for xmltodict.parse()

            total_gs[0] += 1
            data = pth[1][1]

            spec = data['ORGANISM']
            # filter by species
            if species is not None and spec != species:
                species_excl[0] += 1
                return True

            id_ = data['SYSTEMATIC_NAME']
            name = data['STANDARD_NAME']
            coll = data['CATEGORY_CODE']
            desc = data['DESCRIPTION_BRIEF']
            entrez = data['MEMBERS_EZID'].split(',')

            genes = []
            for e in entrez:
                total_genes[0] += 1
                try:
                    genes.append(entrez2gene[e])
                except KeyError:
                    unknown_entrezid[0] += 1

            if not genes:
                logger.warning('Gene set "%s" (%s) has no known genes!',
                        name, id_)
                return True

            gs = GeneSet(id_, name, genes, source = src,
                    collection = coll, description = desc)
            gene_sets.append(gs)
            i[0] += 1
            return True

        # parse the XML file using the xmltodict package
        with io.open(path, 'rb') as fh:
            xmltodict.parse(fh.read(), encoding = 'UTF-8', item_depth = 2,
                    item_callback = handle_item)

        # report some statistics
        if species_excl[0] > 0:
            kept = total_gs[0] - species_excl[0]
            perc = 100 * (kept / float(total_gs[0]))
            logger.info('%d of all %d gene sets (%.1f %%) belonged to the ' +
                    'specified species.', kept, total_gs[0], perc)

        if unknown_entrezid[0] > 0:
            unkn = unknown_entrezid[0]
            #known = total_genes[0] - unknown_entrezid[0]
            perc = 100 * (unkn / float(total_genes[0]))
            logger.warning('%d of a total of %d genes (%.1f %%) had an ' +
                    'unknown Entrez ID.', unkn, total_genes[0], perc)

        logger.info('Parsed %d entries, resulting in %d gene sets.',
                total_gs[0], len(gene_sets))

        return cls(gene_sets)