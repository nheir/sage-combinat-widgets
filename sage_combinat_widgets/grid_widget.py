# -*- coding: utf-8 -*-
r"""
An editable GridWidget for Sage Jupyter Notebook

EXAMPLES ::
    sage: from sage_combinat_widgets import GridWidget
    sage: from sage.all import matrix, graphs
    sage: m = matrix([[1,2], [3,4]])
    sage: w = GridWidget(m)
    sage: g = graphs.GridGraph((3,3))
    sage: w = GridWidget(g)

AUTHORS:
- Odile Bénassy, Nicolas Thiéry

"""
from __future__ import print_function, absolute_import
from sage.misc.bindable_class import BindableClass
from sage.combinat.tableau import *
from sage.all import SageObject, matrix
from ipywidgets import Layout, VBox, HBox, Text, HTML
import traitlets

cell_layout = Layout(width='3em',height='2em', margin='0',padding='0')
css_lines = []
css_lines.append(".invisible {display: none; width: 0; height: 0;}")
css_lines.append(".visible {display: table}")
css_lines.append(".blbutton { background-color: white; }")
css_lines.append(".dwbutton { border-collapse: collapse; color: red; border: 1px solid #666;}")
css_lines.append(".left { border-right: 1px dotted #999; }")
css_lines.append(".right { border-left: 1px dotted #999; }")
css_lines.append(".bottom { border-top: 1px dotted #999; }")
css_lines.append(".top { border-bottom: 1px dotted #999; }")
css_lines.append(".green { background-color: lightgreen; }")
css_lines.append(".blue { background-color: lightblue; }")
css_lines.append(".pink { background-color: lightpink; }")
css_lines.append(".yellow { background-color: lightyellow; }")
css = HTML("<style>%s</style>" % '\n'.join(css_lines))

try:
    ip = get_ipython()
    for base in ip.__class__.__mro__:
        """If we are in a notebook, we will find 'notebook' in those names"""
        if 'otebook' in base.__name__:
            ip.display_formatter.format(css)
            break
except:
    pass # We are in the test environment

class Blank(Text):
    r"""A disabled placeholder input

    TESTS::
        sage: from sage_combinat_widgets.grid_widget import Blank
        sage: b = Blank()
    """

    def __init__(self):
        super(Blank, self).__init__('', disabled=True)
        self.layout = cell_layout
        self.add_class('bltext')

import sage.misc.classcall_metaclass
class MetaHasTraitsClasscallMetaclass (traitlets.traitlets.MetaHasTraits, sage.misc.classcall_metaclass.ClasscallMetaclass):
    pass
class BindableWidgetClass(BindableClass):
    __metaclass__ = MetaHasTraitsClasscallMetaclass

class GridWidget(VBox, BindableWidgetClass):
    r"""Base Jupyter Interactive Widget for Sage Grid Objects

    Composed of cells. Various Cell Classes are possible.
    cell_class will have a trait value, a description,
    and its coordinates (row_number, cell_number_in_row) serve as dict key
    """
    value = traitlets.Instance(SageObject)

    def __init__(self, obj=None, cell_class=Text, trait_class=traitlets.Unicode, **kwargs):
        r"""
        TESTS::

            sage: from sage_combinat_widgets import GridWidget
            sage: from sage.all import matrix, graphs
            sage: from sage.graphs.generic_graph import GenericGraph
            sage: v = vector((1,2,3))
            sage: w = GridWidget(v)
            sage: g = graphs.AztecDiamondGraph(3)
            sage: w = GridWidget(g)
            sage: t = StandardTableaux(5).random_element()
            sage: w = GridWidget(t)
        """
        super(GridWidget, self).__init__()
        if obj:
            self.value = obj
            self.compute(cell_class, trait_class)

    def compute(self, cell_class=Text, trait_class=traitlets.Unicode):
        self.cells = {}
        obj = self.value
        if hasattr(obj, 'vertices'): # Graph
            cells = getattr(obj, 'vertices')()
        elif hasattr(obj, 'cells'): # Tableau
            cells = getattr(obj, 'cells')()
        elif hasattr(obj, 'nrows'): # Matrix
            cells = [(i, j) for i in range(obj.nrows()) for j in range(obj.ncols())]
        elif hasattr(obj, 'row'): # Vector
            cells = [(i, j) for i in range(matrix(obj).nrows()) for j in range(matrix(obj).ncols())]
        else:
            cells = []
        rows = []
        columns = []
        for c in cells:
            if c[1] == 0:
                if columns:
                    rows.append(HBox(columns))
                columns = []
            traitname = 'cell_%d_%d' % c
            new_cell = cell_class('', layout=cell_layout, placeholder=str(c)[1:-1])
            self.add_traits(**{traitname : trait_class()})
            traitlets.link((self, traitname), (new_cell, 'value'))
            self.cells[c] = new_cell
            columns.append(new_cell)
        if columns:
            rows.append(HBox(columns))
        self.children = rows
