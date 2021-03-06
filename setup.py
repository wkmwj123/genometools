# Copyright (c) 2015, 2016 Florian Wagner
#
# This file is part of GenomeTools.
#
# GenomeTools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, Version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# import sys

import os
from os import path
import io

from setuptools import setup, find_packages, Command

root = 'genometools'
name = 'genometools'
version = '0.4.1'

here = path.abspath(path.dirname(__file__))
description = 'GenomeTools: A Python Toolkit for Working with Genomic Data.'

install_requires = [
    'six>=1.5.2, <2',
    'future>=0.15.2, <1',
    'requests>=2.9.1, <3',
    'unicodecsv>=0.14.1, <1',
    'xmltodict>=0.10.1, <1',
    'ftputil>=3.3.1, <4',
    'numpy>=1.8, <2',
    'pandas>=0.20.1, <1',
    'xlmhg>=2.4.9, <3',
    'google-cloud-storage>=0.23.1',
    'oauth2client>=4, <5',
    'jinja2>=2.9.5, <3',
    'biopython>=1.69',
    'sortedcontainers>=1.5.7,<2'
]

# do not require installation if built by ReadTheDocs
# (we mock these modules in docs/source/conf.py)
if 'READTHEDOCS' not in os.environ or \
        os.environ['READTHEDOCS'] != 'True':
    install_requires.extend([
        #'six>=1.10.0, <2',
        'scipy>=1, <2',
        'plotly>=2, <3',
    ])
else:
    install_requires.extend([
        #'pandas>=0.13, <1',
    ])

# get long description from file
long_description = ''
with io.open(path.join(here, 'README.rst'), encoding='UTF-8') as fh:
    long_description = fh.read()


class CleanCommand(Command):
    """Removes files generated by setuptools.

    """
    # see https://github.com/trigger/trigger/blob/develop/setup.py
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        error_msg = 'You must run this command in the package root!'
        if not os.getcwd() == here:
            raise OSError(error_msg)
        else:
            os.system('rm -rf ./dist ./build ./*.egg-info ')

setup(
    name=name,

    version=version,

    description=description,
    long_description=long_description,

    # homepage
    url='https://github.com/flo-compbio/genometools',

    author='Florian Wagner',
    author_email='florian.wagner@duke.edu',

    license='GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='genome genes tools analysis expression sequencing',

    # packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    packages=find_packages(exclude=['docs', 'tests*']),
    # packages=find_packages(root),

    # libraries = [],

    install_requires=install_requires,

    # tests_require=[],

    extras_require={
        'docs': [
            'sphinx',
            'sphinx-rtd-theme',
            'sphinx-argparse',
            'mock',
        ],
        'tests': [
            'pytest>=2.8.5, <4',
            'pytest-cov>=2.2.1, <3',
        ],
    },

    # data
    # package_data={'genometools': ['data/RdBu_r_colormap.tsv']},
    package_data={
        'genometools': [
            'data/*.tsv',
            'data/gcloud/pipelines/*.sh',
            'data/gcloud/pipelines/STAR/*.sh',
            'data/gcloud/scripts/*.sh',
            'data/tests/*']
    },

    # data outside the package
    # data_files=[('my_data', ['data/data_file'])],

    entry_points={
        'console_scripts': [
            # Ensembl scripts
            'ensembl_filter_fasta.py = genometools.ensembl.filter_fasta:main',

            'ensembl_extract_protein_coding_genes.py = '
                'genometools.ensembl.cli.extract_protein_coding_genes:main',

            'ensembl_extract_protein_coding_gene_ids.py = '
                'genometools.ensembl.extract_protein_coding_gene_ids:main',

            'ensembl_extract_protein_coding_exon_annotations.py = '
                'genometools.ensembl.extract_protein_coding_exon_annotations:'
                'main',

            # NCBI scripts
            'ncbi_extract_entrez2gene.py = '
                'genometools.ncbi.extract_entrez2gene:main',

            # GEO scripts
            'geo_generate_sample_sheet.py = '
                'genometools.geo.generate_sample_sheet:main',

            # SRA scripts
            'sra_find_experiment_runs.py = '
                'genometools.sra.find_experiment_runs:main',

            # sequencing scripts
            'seq_trim_fastq.py = '
                'genometools.seq.trim_fastq:main',

            # RNA-Seq scripts
            'rnaseq_stringtie_gene_level_expression.py = '
                'genometools.rnaseq.stringtie_gene_level_expression:main',

            # expression scripts
            'exp_convert_entrez2gene.py = '
                'genometools.expression.convert_entrez2gene:main',
        ],
    },

    cmdclass={
        'clean': CleanCommand,
    },

)
