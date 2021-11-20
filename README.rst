
CLU+
==========================================

|py| |pypi| |Build Status| |docs| |Coverage Status|

``CLU+`` adds some enhancements to sdss-clu

Features
--------
- RPC/Corba/Zeroc Ice style actor communications
- Asyncio & classic python usage
- Complex data with json-pickle
- Recursive config file loading

Installation
------------

``CLU+`` can be installed using ``pip`` as

.. code-block:: console

    pip install sdss-cluplus

or from source

.. code-block:: console

    git clone https://github.com/sdss/cluplus
    cd cluplus
    pip install .


Next, head to the `Getting started <https://github.com/wasndas/cluplus/wiki>`__ section for more information about using clu+. All the examples are available `here <https://github.com/wasndas/cluplus/wiki/Examples>`__.



.. |Build Status| image:: https://img.shields.io/github/workflow/status/wasndas/cluplus/Test
    :alt: Build Status
    :target: https://github.com/wasndas/cluplus/actions

.. |Coverage Status| image:: https://codecov.io/gh/wasndas/cluplus/branch/master/graph/badge.svg?token=i5SpR0OjLe
    :alt: Coverage Status
    :target: https://codecov.io/gh/wasndas/cluplus

.. |py| image:: https://img.shields.io/badge/python-3.7%20|%203.8%20|%203.9-blue
    :alt: Python Versions
    :target: https://docs.python.org/3/

.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest
    :alt: Documentation Status
    :target: https://cluplus.readthedocs.io/en/latest/?badge=latest

.. |pypi| image:: https://badge.fury.io/py/sdss-cluplus.svg
    :alt: PyPI version
    :target: https://badge.fury.io/py/sdss-cluplus

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
