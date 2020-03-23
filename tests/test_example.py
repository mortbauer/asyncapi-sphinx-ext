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
