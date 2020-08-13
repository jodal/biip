====
biip
====


Biip is a Python library for making sense of the data in barcodes.

The library can interpret the following formats:

- GTIN-8, GTIN-12, GTIN-13, and GTIN-14 numbers,
  commonly found in EAN-8, EAN-13, UPC-A, UPC-E, and ITF-14 barcodes.

- GS1 AI element strings,
  commonly found in GS1-128 barcodes.

For details on how the barcode data is interpreted, please refer to the
`GS1 General Specifications (PDF) <https://www.gs1.org/docs/barcodes/GS1_General_Specifications.pdf>`_.


Installation
============

Biip is available from `PyPI <https://pypi.org/project/biip/>`_:

.. code-block:: console

    $ python3 -m pip install biip

Biip requires Python 3.7 or newer.


.. toctree::
    :maxdepth: 2
    :caption: Usage

    api


.. toctree::
    :maxdepth: 2
    :caption: About

    changes


License
=======

Biip is copyright 2020 Stein Magnus Jodal and contributors.
Biip is licensed under the
`Apache License, Version 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.
