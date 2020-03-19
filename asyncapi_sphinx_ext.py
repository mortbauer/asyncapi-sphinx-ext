
import os
from collections import defaultdict

from typing import Any, Dict, IO, List, Pattern, Set, Tuple, Iterable
from typing import cast
import logging

from sphinx import addnodes
from sphinx import roles
from sphinx.locale import _, __
from sphinx.domains import Domain
from sphinx.environment import BuildEnvironment
from sphinx.util.docutils import SphinxDirective, new_document
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.inspect import safe_getattr

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.directives.admonitions import BaseAdmonition

logger = logging.getLogger(__name__)

try:
    from ruamel.yaml import YAML
    yaml = YAML(typ='safe')
except:
    yaml = None


def get_fields(x,parent=''):
    """ recursively gets definition_lists and field_lists into dictionaries """
    fields = {}
    if isinstance(x, nodes.field_list):
        for child in x.children:
            if isinstance(child,nodes.field):
                field_name = child.children[0].rawsource.strip()
                field_value = child.children[1].rawsource.strip()
                fields[field_name] = field_value
    elif isinstance(x, nodes.definition_list):
        for child in x.children:
            if isinstance(child,nodes.definition_list_item):
                key = child.children[0].rawsource.strip()
                if len(child.children[1].children) == 1:
                    fields[key] = get_fields(child.children[1].children[0],parent=parent+key)
                else:
                    all_res = {}
                    for ch in child.children[1].children:
                        res = get_fields(ch,parent=parent+key)
                        if len(res) != 1:
                            logger.warning('Failed to get fields from %s',parent+key)
                        else:
                            skey = next(iter(res))
                            all_res[skey] = res[skey]
                    fields[key] = all_res
    return fields

def to_fields(x):
    if len(x) == 1:
        node = nodes.definition_list()
        df = nodes.definition_list_item()
        key = next(iter(x))
        df.append(nodes.term(text=key))
        node.append(df)
        dfv = nodes.definition()
        dfv.append(to_fields(x[key]))
        node.append(dfv)
        return node

class asyncapi_node(nodes.Admonition, nodes.Element):
    pass

class asyncapi_overview(nodes.General,nodes.Element):
    pass

def visit_asyncapi_html(self, node):
    self.body.append(self.starttag(node, 'asyncapi_overview'))

def depart_asyncapi_html(self, node):
    self.body.append('</asyncapi_overview>')

def visit_asyncapi_node(self, node):
    self.visit_admonition(node)

def depart_asyncapi_node(self, node):
    self.depart_admonition(node)

class AsyncApiChannelDirective(BaseAdmonition,SphinxDirective):
    node_class = asyncapi_node
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'class': directives.class_option,
        'name': directives.unchanged,
        'format': directives.unchanged,
    }

    def run(self):
        asyncapi_format = self.options.get('format', 'rst')
        # use all the text
        as_admonition = asyncapi_format == 'rst'
        if as_admonition:
            (channel,) = super().run()  # type: Tuple[Node]
            res = get_fields(channel.children[0])
        elif yaml is not None:
            channel = self.node_class('')
            text = '\n'.join(self.content).strip()
            res = yaml.load(text)
        else:
            raise Exception('Needs optional dependencies ruamel.yaml')
        # parse asyncapi spec
        channel['asyncapi'] = res 
        channel['docname'] = self.env.docname
        self.add_name(channel)
        self.set_source_info(channel)
        self.state.document.note_explicit_target(channel)
        if not as_admonition:
            for topic,topic_spec in res.items():
                for operation,operation_spec in topic_spec.items():
                    if operation == 'publish':
                        op = 'PUB'
                    elif operation == 'subscribe':
                        op = 'SUB'
                    else:
                        logger.error('Warning operation %s not supported',operation)
                        continue
                    message_spec = operation_spec.get('message',{})
                    p = nodes.strong(text=topic)
                    channel.append(p)
                    p = nodes.paragraph()
                    p.append(nodes.inline(text=op,classes=['guilabel']))
                    if 'contentType' in message_spec:
                        p.append(nodes.inline(text=' '))
                        p.append(nodes.inline(text=message_spec['contentType'],classes=['guilabel']))
                    channel.append(p)
                    p = nodes.paragraph()
                    p.append(nodes.emphasis(text=operation_spec.get('summary','')))
                    channel.append(p)
                    for key,spec in message_spec.get('payload',{}).get('properties',{}).items():
                        fl = nodes.field_list()
                        field = nodes.field()
                        field.append(nodes.field_name(key,nodes.Text(key)))
                        field.append(nodes.field_body('spec',self.make_property_spec(spec)))
                        fl.append(field)
                        channel.append(fl)
                    channel.append(nodes.paragraph())
        return [channel]

    def make_property_spec(self,property_spec):
        fl = nodes.field_list()
        for key,value in property_spec.items():
            field = nodes.field()
            field.append(nodes.field_name(key,nodes.Text(key)))
            field.append(nodes.field_body(value,nodes.Text(value)))
            fl.append(field)
        return fl

class AsynApiDomain(Domain):
    name = 'asyncapi'
    label = 'asyncapi'

    @property
    def channels(self) -> Dict[str, List[asyncapi_node]]:
        return self.data.setdefault('channels', {})

    def clear_doc(self, docname: str) -> None:
        self.channels.pop(docname, None)

    def merge_domaindata(self, docnames: List[str], otherdata: Dict) -> None:
        for docname in docnames:
            self.channels[docname] = otherdata['asyncapi'][docname]

    def process_doc(self, env: BuildEnvironment, docname: str,
                    document: nodes.document) -> None:
        channels = self.channels.setdefault(docname, [])
        for channel in document.traverse(asyncapi_node):
            env.app.emit('asyncapi_channel-defined', channel)
            channels.append(channel)

class AsyncApiDirective(SphinxDirective):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'class': directives.class_option,
        'name': directives.unchanged,
    }

    def run(self):
        # Simply insert an empty node which will be replaced later
        return [asyncapi_overview('',operation=self.arguments[0])]

class AsyncApiChannelProcessor:
    def __init__(self, app, doctree, docname):
        self.builder = app.builder
        self.config = app.config
        self.env = app.env
        self.domain = app.env.get_domain('asyncapi')

        self.process(doctree, docname)


    def create_table(self):
        table = nodes.table()
        tgroup = nodes.tgroup(cols=2)
        table += tgroup
        for colwidth in (30,70):
            tgroup += nodes.colspec(colwidth=colwidth)

        thead = nodes.thead()
        tgroup += thead
        # thead += self.create_table_row(('Topic','summary'))

        tbody = nodes.tbody()
        tgroup += tbody
        return table,tbody


    def process(self, doctree: nodes.document, docname: str) -> None:
        channels = sum(self.domain.channels.values(), [])  # type: List[todo_node]
        document = new_document('')

        for node in doctree.traverse(asyncapi_overview):
            table = self.create_full_table(node,channels,docname)
            node.replace_self(table)

    def create_full_table(self,node,channels,docname):
        wanted_operation = node['operation']
        table,tbody = self.create_table()
        per_topic = defaultdict(list)
        for channel in channels:
            for topic,topic_spec in channel['asyncapi'].items():
                for operation,op_spec in topic_spec.items():
                    if operation == wanted_operation:
                        source = channel.source.split(' of ')[1]
                        ref = self.create_channel_reference(source,channel, docname)
                        per_topic[topic].append((op_spec['summary'],ref))
        for topic,topic_spec in per_topic.items():
            summary = topic_spec[0][0]
            desc_node = nodes.inline(text=summary)
            for _,link in topic_spec:
                desc_node.append(nodes.inline(text=', '))
                desc_node.append(link)
            tbody.append(
                self.create_table_row(
                    (topic,desc_node)
                )
            )
        return table

    def create_table_row(self, row_cells):
        row = nodes.row()
        for cell in row_cells:
            entry = nodes.entry()
            row.append(entry)
            if isinstance(cell,str):
                entry.append(nodes.paragraph(text=cell))
            else:
                entry.append(cell)
        return row


    def create_channel_reference(self, text:str,channel: asyncapi_node, docname: str) -> nodes.paragraph:
        para = nodes.inline(classes=['asyncapi-source'])

        # Create a reference
        linktext = nodes.emphasis(text,text)
        reference = nodes.reference('', '', linktext, internal=True)
        try:
            reference['refuri'] = self.builder.get_relative_uri(docname, channel['docname'])
            reference['refuri'] += '#' + channel['ids'][0]
        except NoUri:
            # ignore if no URI can be determined, e.g. for LaTeX output
            pass

        para += reference

        return para

class AsyncApiBuilder(Builder):
    """
    Evaluates coverage of code in the documentation.
    """
    name = 'asyncapi'
    epilog = __('Testing of coverage in the sources finished, look at the '
                'results in %(outdir)s' + os.path.sep + 'python.txt.')

    def init(self):
        self.data = {'asyncapi':'2.0.0'}
        for key,data in self.config.asyncapi_data.items():
            self.data[key] = data

    def get_outdated_docs(self) -> str:
        return 'coverage overview'

    def write(self, *ignored: Any) -> None:
        channel_nodes = self.env.domaindata['asyncapi']['channels']
        import IPython
        # IPython.embed()
        channels = {}
        for document_name,nodes in channel_nodes.items():
            for node in nodes:
                for topic,topic_spec in node['asyncapi'].items():
                    channels[topic] = topic_spec
        self.data['channels'] = channels
       
    def finish(self) -> None:
        if yaml is not None:
            path = os.path.join(self.outdir, 'asyncapi.yaml')
            with open(path, 'w') as dumpfile:
                yaml.dump(self.data,dumpfile)
        else:
            raise Exception('Needs optional dependencies ruamel.yaml')

def setup(app):
    data = []
    app.setup_extension('sphinx.ext.autodoc')
    app.add_config_value('asyncapi_data', {}, False)
    app.add_node(asyncapi_node,html=(visit_asyncapi_node,depart_asyncapi_node))
    app.add_node(asyncapi_overview)
    app.add_directive('asyncapi_channels', AsyncApiChannelDirective)
    app.add_directive('asyncapi_overview', AsyncApiDirective)
    app.add_domain(AsynApiDomain)
    app.connect('doctree-resolved', AsyncApiChannelProcessor)
    app.add_builder(AsyncApiBuilder)
