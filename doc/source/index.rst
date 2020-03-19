.. include:: ../../README.rst
  :start-after: inclusion-marker-do-not-remove

Features
********
asyncapi_sphinx_ext adds two directives `asyncapi_channels` and
`asyncapi_overview` to document pub/sub endpoints, directly in your source code
as python docstring.

It further adds a `sphinx builder` to extract all the documented pub/sub
endpoints and export them as a single asyncapi yaml.


Configuration Parameters
************************

:asyncapi_data: Dictionary with AsyncApi spec meta data.

Invoking the builder
********************
::

    sphinx-build -b asyncapi source/ build/asynapi

Contents
********

.. toctree::
   :maxdepth: 2

   example_usage

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _asyncapi: https://www.asyncapi.com/docs/specifications/2.0.0/
