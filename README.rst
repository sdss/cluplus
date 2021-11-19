
`CLU+ `__
==========================================

|py| |pypi| |black| |Build Status| |docs| |Coverage Status|


Features
--------

- RPC/Corba/Zeroc Ice style actor communications
- Recursive config file loading

Installation
------------

``CLU#`` can be installed using ``pip`` as

.. code-block:: console

    pip install sdss-cluplus

or from source

.. code-block:: console

    git clone https://github.com/sdss/cluplus
    cd cluplus
    pip install .


Development
^^^^^^^^^^^

``cluplus`` uses `poetry <http://poetry.eustace.io/>`__ for dependency management and packaging. To work with an editable install it's recommended that you setup ``poetry`` and install ``cluplus`` in a virtual environment by doing

.. code-block:: console

    poetry install


Quick start
-----------

Creating a new actor with ``CLU`` is easy. To instantiate and run an actor you can simply do

.. code-block:: python

    import asyncio
    from clu import AMQPActor

    async def main(loop):
        actor = await Actor('my_actor').start()
        await actor.run_forever()

    asyncio.run(main(loop))



.. |Build Status| image:: https://img.shields.io/github/workflow/status/sdss/cluplus/Test
    :alt: Build Status
    :target: https://github.com/sdss/cluplus/actions

.. |Coverage Status| image:: https://codecov.io/gh/sdss/cluplus/branch/main/graph/badge.svg
    :alt: Coverage Status
    :target: https://codecov.io/gh/sdss/cluplus

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


