# mashphage <img src="img/logo.png" align="right" width="120" />

<!-- badges: start -->
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
<!-- badges: end -->

## Fast and accurate whole-genome clustering of (actino) bacteriophages

The goal of mashphage is to provide a mean to rapidly and accurately cluster (actino) bacteriophage genome
in know clusters. Mashphage comes bundled with a genomic signature of actinobacteriophage genomes, which enables
to fastly and accurately assign actinobacteriophages genomes in the known cluster schemes.
However, the user can specify a custom path (with `-d` option) to a genomic signature created using `sourmash sketch`.

## Installation

First install `sourmash`:
```
conda install -c conda-forge -c bioconda sourmash

or 

pip install sourmash
```

Second install mashphage from pypi:
``` 
pip install mashphage
```

## Example

This is a basic example which shows you how to cluster a genome:

```
mashphage genome.fa
```

Enjoy!






