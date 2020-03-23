import os
from collections import defaultdict

from typing import Any, Dict, IO, List, Pattern, Set, Tuple, Iterable
from typing import cast
import logging

from sphinx import addnodes
from sphinx import roles
from sphinx.errors import NoUri
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
                        for skey in res:
                            if skey in all_res:
                                logger.warning('Overwriting key %s in %s.%s',skey,parent,key)
                            all_res[skey] = res[skey]
                    fields[key] = all_res
    return fields

def to_fields(x):
    to_definiton_list = False
    for v in x.values():
        if isinstance(v,dict):
            to_definiton_list = True
            break
    if to_definiton_list:
        node = nodes.definition_list()
        previous_fieldlist = None
        for key,v in x.items():
            df = nodes.definition_list_item()
            if isinstance(v,str): # embed field_list inside definition_list
                if previous_fieldlist is None:
                    fv = previous_fieldlist = nodes.field_list()
                    df.append(fv)
                    node.append(df)
                else:
                    fv = previous_fieldlist
                fvf = nodes.field()
                fv.append(fvf)
                fvf.append(nodes.field_name(text=key))
                fvf.append(nodes.field_body(v,nodes.Text(v)))
            else:
                previous_fieldlist = None
                df.append(nodes.term(text=key))
                dfv = nodes.definition()
                dfv.append(to_fields(v))
                df.append(dfv)
                node.append(df)
    else:
        node = nodes.field_list()
        for key,v in x.items():
            df = nodes.field()
            df.append(nodes.field_name(text=key))
            dfv = nodes.field_body(v,nodes.Text(v))
            df.append(dfv)
            node.append(df)
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
        'from_file': directives.unchanged,
    }

    def run(self):
        asyncapi_format = self.options.get('format', 'rst')
        filepath = self.options.get('from_file')
        if filepath is not None:
            if asyncapi_format != 'yaml':
                logger.warning('Selected from_file and rst which is not supported')
            else:
                self.set_source_info(self)
                cur_dir = os.path.dirname(self.source)
                filepath = os.path.join(cur_dir,filepath)
                with open(filepath,'r') as infile:
                    content = infile.read()
        else:
            content = '\n'.join(self.content).strip()
        # use all the text
        as_admonition = asyncapi_format == 'rst'
        if as_admonition:
            (channel,) = super().run()  
            res = get_fields(channel.children[0])
        elif yaml is not None:
            res = yaml.load(content)
        else:
            raise Exception('Needs optional dependencies ruamel.yaml')
        channels = []
        for topic,topic_spec in res.items():
            for op,op_spec in topic_spec.items():
                channel = self.node_class('')
                channel['asyncapi'] = dat = {topic:{op:op_spec}} 
                channel['docname'] = self.env.docname
                self.add_name(channel)
                self.set_source_info(channel)
                self.state.document.note_explicit_target(channel)
                channel.append(to_fields(dat))
                channels.append(channel)
        return channels


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
            env.app.emit('asyncapi-channels-defined', channel)
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
                        if ' of ' in channel.source:
                            link_text = channel.source.split(' of ')[1]
                        else:
                            link_text = channel['ids'][0][2:]
                        ref = self.create_channel_reference(link_text,channel, docname)
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
    app.add_event('asyncapi-channels-defined')
    app.add_config_value('asyncapi_data', {}, False)
    app.add_node(asyncapi_node,html=(visit_asyncapi_node,depart_asyncapi_node))
    app.add_node(asyncapi_overview)
    app.add_directive('asyncapi_channels', AsyncApiChannelDirective)
    app.add_directive('asyncapi_overview', AsyncApiDirective)
    app.add_domain(AsynApiDomain)
    app.connect('doctree-resolved', AsyncApiChannelProcessor)
    app.add_builder(AsyncApiBuilder)
