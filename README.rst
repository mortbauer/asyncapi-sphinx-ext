.. inclusion-marker-do-not-remove

AsyncAPI Sphinx Extension
#########################

.. image:: https://img.shields.io/pypi/pyversions/asyncapi-sphinx-ext
   :target: https://pypi.org/project/asyncapi-sphinx-ext/
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/v/asyncapi-sphinx-ext.svg
   :target: https://pypi.org/project/asyncapi-sphinx-ext/
   :alt: Package on PyPI

.. image:: https://img.shields.io/travis/mortbauer/asyncapi-sphinx-ext   
   :target: https://travis-ci.org/mortbauer/asyncapi-sphinx-ext
   :alt: Travis (.org)

.. image:: https://coveralls.io/repos/asyncapi-sphinx-ext/sphinx-testing/badge.png?branch=master
   :target: https://coveralls.io/r/asyncapi-sphinx-ext/sphinx-testing?branch=master

.. image:: https://img.shields.io/pypi/dm/asyncapi-sphinx-ext.svg
   :target: https://pypi.python.org/pypi/asyncapi-sphinx-ext
   :alt: Number of PyPI downloads

.. image:: https://img.shields.io/pypi/wheel/asyncapi-sphinx-ext.svg
   :target: https://pypi.python.org/pypi/asyncapi-sphinx-ext
   :alt: Wheel Status

.. image:: https://img.shields.io/readthedocs/asyncapi-sphinx-ext   
   :target: https://asyncapi-sphinx-ext.readthedocs.io/en/latest
   :alt: Read the Docs

This extension adds some directives to integrate documentation for your pub-sub
application using asyncapi_ specification.

You can use asyncapi_ specifications in your source code doc string or in your
documentation to generate a beautiful documentation plus overview. Further the
specification might be used for other things as well (not supported yet).

.. warning:: 

    This is still in a early stage.

Installation
************

Install the sphinx extension with `pip install asyncapi_sphinx_ext`.

Usage
*****

The extension adds two directives `asyncapi_channels` and `asyncapi_overview`.

The `asyncapi_channels` directive is used to add the some pub/sub documentation
and the `asyncapi_overview` is used to create a table with the all the pub/sub
topics defined.

For a full example checkout `usage_example`_.

Important Links
***************

:source: https://github.com/mortbauer/asyncapi-sphinx-ext
:documentation: https://asyncapi-sphinx-ext.readthedocs.org/en/latest/
:pypi: https://pypi.org/project/asyncapi-sphinx-ext/

.. _asyncapi: https://www.asyncapi.com/docs/specifications/2.0.0/
.. _usage_example: 
