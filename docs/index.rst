====
biip
====


Biip is a Python library for making sense of the data in barcodes.

The library can interpret the following formats:

- GTIN-8, GTIN-12, GTIN-13, and GTIN-14 numbers,
  commonly found in EAN-8, EAN-13, and ITF-14 barcodes.

- GS1 AI element strings,
  commonly found in GS1-128 barcodes.

- UPC-A and UPC-E numbers, as found in UPC-A and UPC-E barcodes.

For details on how the barcode data is interpreted, please refer to the
`GS1 General Specifications (PDF) <https://www.gs1.org/docs/barcodes/GS1_General_Specifications.pdf>`_.


Installation
============

Biip requires Python 3.9 or newer.

Biip is available from `PyPI <https://pypi.org/project/biip/>`_:

.. code-block:: console

    $ python3 -m pip install biip

Optionally, with the help of ``py-moneyed``, Biip can convert amounts with
currency information to :class:`moneyed.Money` objects.
To install Biip with ``py-moneyed``, run:

.. code-block:: console

    $ python3 -m pip install "biip[money]"


Project resources
=================

- `Documentation <https://biip.readthedocs.io/>`_
- `Source code <https://github.com/jodal/biip>`_
- `Releases <https://github.com/jodal/biip/releases>`_
- `Issue tracker <https://github.com/jodal/biip/issues>`_
- `Contributors <https://github.com/jodal/biip/graphs/contributors>`_
- `Users <https://github.com/jodal/biip/wiki/Users>`_


.. toctree::
    :maxdepth: 2
    :caption: Usage

    quickstart

.. toctree::
    :maxdepth: 2
    :caption: Reference

    api/biip
    api/gln
    api/gs1
    api/gs1-checksums
    api/gtin
    api/sscc
    api/symbology
    api/upc


License
=======

Copyright 2020-2025 Stein Magnus Jodal and contributors.
Licensed under the
`Apache License, Version 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.
