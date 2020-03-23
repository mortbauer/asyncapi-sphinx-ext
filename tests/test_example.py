import pytest

from sphinx.util import docutils


@pytest.mark.sphinx('html', testroot='rst', freshenv=True)
def test_rst(app, status, warning):
    channels = []

    def on_channel_defined(app, node):
        channels.append(node)

    app.connect('asyncapi-channels-defined', on_channel_defined)
    app.builder.build_all()

    assert len(channels) == 2

@pytest.mark.sphinx('html', testroot='yaml', freshenv=True)
def test_yaml(app, status, warning):
    channels = []

    def on_channel_defined(app, node):
        channels.append(node)

    app.connect('asyncapi-channels-defined', on_channel_defined)
    app.builder.build_all()

    assert len(channels) == 2

@pytest.mark.sphinx('html', testroot='yaml-from-file', freshenv=True)
def test_yaml_from_file(app, status, warning):
    channels = []

    def on_channel_defined(app, node):
        channels.append(node)

    app.connect('asyncapi-channels-defined', on_channel_defined)
    app.builder.build_all()

    assert len(channels) == 1

@pytest.mark.sphinx('asyncapi', testroot='yaml-from-file', freshenv=True)
def test_yaml_from_file_asyncapi(app, status, warning):
    channels = []

    def on_channel_defined(app, node):
        channels.append(node)

    app.connect('asyncapi-channels-defined', on_channel_defined)
    app.builder.build_all()

    assert len(channels) == 1
