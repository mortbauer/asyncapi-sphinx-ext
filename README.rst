.. inclusion-marker-do-not-remove

AsyncAPI Sphinx Extension
#########################

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
