import codecs
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(
    name='asyncapi-sphinx-ext',
    version='1.0.1',
    author='Martin Ortbauer',
    author_email='mortbauer@gmail.com',
    url='http://github.com/mortbauer/asyncapi-sphinx-ext',
    license='MIT',
    description='Sphinx extension for Pub/Sub Documentation',
    py_modules=['asyncapi_sphinx_ext'],  
    long_description=codecs.open("README.rst", "r", "utf-8").read(),
    install_requires=['sphinx'],
    extras_require = {
        'yaml':  ["ruamel.yaml"]
    },
    entry_points={
        'sphinx.builders': [
            'asynapi = asyncapi_sphinx_ext'
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
)
