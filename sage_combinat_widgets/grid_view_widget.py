# -*- coding: utf-8 -*-
r"""
An editable Grid View Widget for Sage Jupyter Notebook.

AUTHORS ::

    Odile Bénassy, Nicolas Thiéry

"""
from .grid_view_editor import GridViewEditor, cdlink
from sage.graphs.generic_graph import GenericGraph
from ipywidgets import Layout, VBox, HBox, Text, HTML, ToggleButton, Button, ValueWidget, register
from six import text_type
from traitlets import Unicode

textcell_layout = Layout(width='3em', height='2em', margin='0', padding='0')
textcell_wider_layout = Layout(width='7em', height='3em', margin='0', padding='0')
buttoncell_layout = Layout(width='5em', height='4em', margin='0', padding='0')
buttoncell_smaller_layout = Layout(width='2em', height='2em', margin='0', padding='0')
css_lines = []
css_lines.append(".widget-text INPUT {border-collapse: collapse !important}")
css_lines.append(".gridbutton {margin:0; padding:0; width:2em; height:2em; border:1px solid #999; color:#666}")
css_lines.append(".blankbutton, .addablebutton {background-color:white; color:#666}")
css_lines.append(".blankbutton {border:0px !important}")
css_lines.append(".blankcell INPUT {border:0px !important}")
css_lines.append(".addablecell INPUT, .removablecell INPUT {background-position: right top; background-size: 1em; background-repeat: no-repeat}")
css_lines.append(".addablecell INPUT {background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAAA8BAAAAAA7DH7+AAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAnRSTlMAAHaTzTgAAAACYktHRAAPOjI+owAAAAlwSFlzAAAN1wAADdcBQiibeAAAAAd0SU1FB+MCBRIvKscf5nsAAAAtSURBVEjHY2AYBaSBmTNnThhVM6pmaKvhnIkVTBjqagZbOI+qGVVDHTXDAwAAnSews7vfUfkAAAAldEVYdGRhdGU6Y3JlYXRlADIwMTktMDItMDVUMTc6NDc6NDIrMDE6MDDD7zGLAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDE5LTAyLTA1VDE3OjQ3OjQyKzAxOjAwsrKJNwAAAABJRU5ErkJggg==')}")
css_lines.append(".addablecell INPUT, .addablebutton INPUT {border:1px dashed #999 !important}")
css_lines.append(".removablecell INPUT {background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAAA8BAAAAAA7DH7+AAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAAnRSTlMAAHaTzTgAAAACYktHRAAPOjI+owAAAAlwSFlzAAAN1wAADdcBQiibeAAAAAd0SU1FB+MCBRIvL7d1EvQAAAAgSURBVEjHY2AYBaNgFIwwwDkTK5gw1NWMglEwCgYxAAAoCFJ7GFQEKQAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAxOS0wMi0wNVQxNzo0Nzo0NyswMTowMJHXHiwAAAAldEVYdGRhdGU6bW9kaWZ5ADIwMTktMDItMDVUMTc6NDc6NDcrMDE6MDDgiqaQAAAAAElFTkSuQmCC')}")
css_lines.append(".dirty INPUT {background-color: pink !important}")
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

@register
class TextWithTooltip(Text):
    """Input text with a help title (tooltip)."""
    _view_name = Unicode('TextWithTooltipView').tag(sync=True)
    _view_module = Unicode('sage-combinat-widgets').tag(sync=True)
    _view_module_version = Unicode('^0.2.0').tag(sync=True)
    description_tooltip = Unicode().tag(sync=True)

    def set_tooltip(self, s=''):
        self.description_tooltip = s

class BaseTextCell(TextWithTooltip):
    r"""
    Abstract class for all text cells except blank.
    """
    displaytype = text_type

    def __init__(self, content, position, layout, **kws):
        super(BaseTextCell, self).__init__()
        self.value = content
        self.layout = layout
        self.continuous_update = False
        self.position = position
        self.add_class('gridcell')

class TextCell(BaseTextCell):
    r"""A regular text grid cell

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import TextCell
        sage: b = TextCell('my text', (1,2))
    """
    def __init__(self, content, position, layout=textcell_layout, **kws):
        super(TextCell, self).__init__(content, position, layout, **kws)

class StyledTextCell(TextCell):
    r"""A class for CSS-styled text grid cells.
    Not meant to be called directly.

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import StyledTextCell
        sage: b = StyledTextCell("ok", (1,2))
        Traceback (most recent call last):
        ...
        TraitError: Element of the '_dom_classes' trait of a StyledTextCell instance must be a unicode string, but a value of None <type 'NoneType'> was specified.
    """
    disable = None
    css_class = None
    style = None
    def __init__(self, content, position, layout=textcell_layout, **kws):
        super(StyledTextCell, self).__init__(content, position, layout, **kws)
        self.add_class(self.css_class)
        if self.disable:
            self.disabled = True
        if self.style:
            apply_css(self.style)

def apply_css(css_line):
    try:
        ip = get_ipython()
        for base in ip.__class__.__mro__:
            """If we are in a notebook, we will find 'notebook' in those names"""
            if 'otebook' in base.__name__:
                ip.display_formatter.format(HTML("<style>%s</style>" % css_line))
                break
    except:
        pass # We are in the test environment

def styled_text_cell(disabled=False, style_name='', style=None):
    r"""A function to create CSS-styled cells.
    A regular text cell has a value and a position.

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import styled_text_cell
        sage: styled_text_cell(disabled=True, style_name='mycssclass', style="")
        <class 'traitlets.traitlets.DisabledMycssclassTextCell'>
    """
    # FIXME passer la couleur en paramètre ? une chaîne CSS ?
    class_name = "{}TextCell".format(style_name.capitalize())
    if disabled:
        class_name = "Disabled" + class_name
    return type(class_name, (StyledTextCell,), {'disable': disabled, 'css_class': style_name, 'style': style})

class WiderTextCell(BaseTextCell):
    r"""A regular text grid cell

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import WiderTextCell
        sage: b = WiderTextCell('my text', (1,2))
    """
    def __init__(self, content, position, layout=textcell_wider_layout, **kws):
        super(WiderTextCell, self).__init__(content, position, layout, **kws)

class BlankCell(Text):
    r"""A blank placeholder cell

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import BlankCell
        sage: b = BlankCell()
    """
    displaytype = text_type

    def __init__(self, layout=textcell_layout, **kws):
        super(BlankCell, self).__init__()
        self.value = ''
        self.layout = layout
        self.disabled = True
        self.add_class('blankcell')

class AddableTextCell(BaseTextCell):
    r"""An addable placeholder for adding a cell to the widget

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import AddableTextCell
        sage: a = AddableTextCell((3,4))
    """
    def __init__(self, position, layout=textcell_layout):
        super(AddableTextCell, self).__init__('', position, layout=layout, continuous_update=False)
        self.add_class('addablecell')

class DisabledTextCell(BaseTextCell):
    r"""A disabled text grid cell

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import DisabledTextCell
        sage: b = DisabledTextCell('my text', (1,2))
    """
    def __init__(self, content, position, layout=textcell_layout, **kws):
        super(DisabledTextCell, self).__init__(content, position, layout=layout, **kws)
        self.disabled = True

class ButtonCell(ToggleButton):
    r"""A base class for button grid cells.

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import ButtonCell
        sage: b = ButtonCell(True, (1,2))
    """
    displaytype = bool

    def __init__(self, content, position, layout=buttoncell_smaller_layout, **kws):
        super(ButtonCell, self).__init__()
        self.layout = layout
        self.value = content
        self.position = position
        self.add_class('gridbutton')
        self.set_tooltip()

    def set_tooltip(self, s=None):
        r"""From a position (i,j),
        we just want the string 'i,j'
        to use as a tooltip on buttons.

        TESTS ::

            sage: from sage_combinat_widgets.grid_view_widget import ButtonCell
            sage: b = ButtonCell(True, (42, 7))
            sage: b.set_tooltip()
            sage: str(b.tooltip)
            '42, 7'
            sage: b.set_tooltip("My new tooltip")
            sage: str(b.tooltip)
            'My new tooltip'
        """
        if s:
            self.tooltip = s
        else:
            self.tooltip = str(self.position)[1:-1]

class StyledButtonCell(ButtonCell):
    r"""A class for CSS-styled button grid cells.
    Not meant to be called directly.

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import StyledButtonCell
        sage: b = StyledButtonCell(True, (1,2))
        Traceback (most recent call last):
        ...
        TraitError: Element of the '_dom_classes' trait of a StyledButtonCell instance must be a unicode string, but a value of None <type 'NoneType'> was specified.
    """
    disable = None
    css_class = None
    def __init__(self, content, position, layout=buttoncell_smaller_layout, **kws):
        super(StyledButtonCell, self).__init__(content, position, layout, **kws)
        self.add_class(self.css_class)
        if self.disable:
            self.disabled = True

def styled_button_cell(disabled=False, style_name=''):
    r"""A function to create CSS-styled buttons.
    A regular button has a value and a position.

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import styled_button_cell
        sage: styled_button_cell(disabled=True, style_name='mycssclass')
        <class 'traitlets.traitlets.DisabledMycssclassButton'>
    """
    # FIXME passer la couleur en paramètre ? une chaîne CSS ?
    class_name = "{}Button".format(style_name.capitalize())
    if disabled:
        class_name = "Disabled" + class_name
    return type(class_name, (StyledButtonCell,), {'disable': disabled, 'css_class': style_name})

DisabledButtonCell = styled_button_cell(disabled=True)
r"""A disabled button cell.

TESTS ::

    sage: from sage_combinat_widgets.grid_view_widget import DisabledButtonCell
    sage: b = DisabledButtonCell(True, (1,2))
    sage: b.disabled
    True
"""

class AddableButtonCell(ButtonCell):
    r"""An addable placeholder for adding a button cell to the widget
    An addable button has a position.

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import AddableButtonCell
        sage: a = AddableButtonCell((3,4))
    """
    def __init__(self, position, layout=buttoncell_smaller_layout, **kws):
        super(AddableButtonCell, self).__init__(False, position, layout, **kws)
        self.add_class('addablebutton')
        self.description = '+'
        self.tooltip = "Click to add a cell here"

class StyledPushButton(Button):
    r"""A class for CSS-styled push buttons.
    Not meant to be called directly.

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import StyledPushButton
        sage: b = StyledPushButton()
    """
    disable = None
    css_class = None
    def __init__(self, content=None, position=None, layout=buttoncell_smaller_layout, description='', placeholder=None):
        super(StyledPushButton, self).__init__()
        self.layout=layout
        self.description=description
        if self.disable:
            self.disabled = True
        self.add_class('gridbutton')
        if self.css_class:
            self.add_class(self.css_class)

def styled_push_button(disabled=False, style_name=''):
    r"""A function to create CSS-styled push buttons.
    A push button stores neither value nor position.

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import styled_push_button
        sage: styled_push_button(style_name='mycssclass').__name__
        'MycssclassPushButton'
    """
    class_name = "{}PushButton".format(style_name.capitalize())
    if disabled:
        class_name = "Disabled" + class_name
    return type(class_name, (StyledPushButton,), {'disable': disabled, 'css_class': style_name})

BlankButton = styled_push_button(disabled=True, style_name='blankbutton')
r"""A blank placeholder button.

TESTS ::

    sage: from sage_combinat_widgets.grid_view_widget import BlankButton
    sage: b = BlankButton()
    sage: b.__class__.__name__
    'DisabledBlankbuttonPushButton'
    sage: b.disabled
    True
    sage: assert 'blankbutton' in b._dom_classes
"""

def get_model_id(w):
    r"""
    For some reason, our widgets seem to lose their model_id
    This *hack* recovers it
    """
    for u in w.widgets:
        if w.widgets[u] == w:
            return u

class GridViewWidget(GridViewEditor, VBox, ValueWidget):
    r"""A widget for all grid-representable Sage objects
    """

    def __init__(self, obj, adapter=None, display_convention='en', cell_layout=None,
                 cell_widget_classes=[TextCell], cell_widget_class_index=lambda x:0,
                 blank_widget_class=BlankCell, addable_widget_class=AddableTextCell):
        r"""
        Grid View Widget initialization.

        INPUT:
            - ``cell_widget_classes``: a list of classes for building cell widgets
            - ``blank_widget_class``: a widget class for building blank cells
            - ``addable_widget_class``: a widget class for building blank cells

        TESTS ::

            sage: from sage_combinat_widgets.grid_view_widget import *
            sage: t = StandardTableaux(15).random_element()
            sage: w = GridViewWidget(t)
            sage: from sage.graphs.generators.families import AztecDiamondGraph
            sage: az = AztecDiamondGraph(4)
            sage: w = GridViewWidget(az, cell_widget_classes=[ButtonCell], blank_widget_class=BlankButton)

        Compatibility with `@interact`: the widget should be a
        :class:`ipywidgets.ValueWidget` and have a description field::

            sage: isinstance(w, ValueWidget)
            True
            sage: w.description
            "Grid view widget for Jupyter notebook with cell class '<class 'sage_combinat_widgets.grid_view_widget.ButtonCell'>', for object 'Subgraph of (2D Grid Graph for [8, 8])'"

        Basic compabitility test::

            sage: def f(x = w): return az.average_distance()
            sage: f = interact(f)
            <html>...</html>
        """
        GridViewEditor.__init__(self, obj, adapter)
        VBox.__init__(self)
        self._model_id = get_model_id(self)
        self.display_convention = display_convention
        self.description = "Grid view widget for Jupyter notebook with cell class '%s', for object '%s'" % (
            cell_widget_classes[0], obj)
        if not cell_layout:
            if issubclass(self.value.__class__, GenericGraph): # i.e. a graph
                cell_layout = buttoncell_smaller_layout
            else:
                cell_layout = textcell_layout
        self.cell_layout = cell_layout
        self.cell_widget_classes = cell_widget_classes
        self.cell_widget_class_index = cell_widget_class_index
        try:
            self.displaytype = cell_widget_classes[0].displaytype
        except:
            self.displaytype = None # Stateless cells
        self.cast = lambda x:self.adapter.display_to_cell(x, self.displaytype)
        self.blank_widget_class = blank_widget_class
        self.addable_widget_class = addable_widget_class
        self.draw()
        self.donottrack = False

    def to_cell(self, val):
        r"""
        From a widget cell value `val`,
        return a valid editor cell value.

        TESTS ::

            sage: from sage_combinat_widgets.grid_view_widget import GridViewWidget
            sage: t = StandardTableaux(5).random_element()
            sage: w = GridViewWidget(t)
            sage: w.to_cell('3')
            3
        """
        return self.cast(val)

    def add_links(self):
        r"""
        Link each individual widget cell
        to its corresponding trait in the editor

        TESTS ::

            sage: from sage.combinat.tableau import StandardTableaux
            sage: from sage_combinat_widgets.grid_view_widget import GridViewWidget
            sage: t = StandardTableaux(15).random_element()
            sage: w1 = GridViewWidget(t)
            sage: w2 = GridViewWidget(t, display_convention='fr')
            sage: len(w1.links)
            20
            sage: assert len(w1.links) == len(w2.links)
            sage: def test0(w): return (w.links[0].source[0].__class__, w.links[0].source[0].value, w.links[0].target[1])
            sage: def test10(w): return (w.links[10].source[0].__class__, w.links[10].source[0].value, w.links[10].target[1])
            sage: def test17(w): return (w.links[17].source[0].__class__, w.links[17].source[0].value, w.links[17].target[1])
            sage: assert test0(w1) == test0(w2)
            sage: assert test10(w1) == test10(w2)
            sage: assert test17(w1) == test17(w2)
            sage: from sage.combinat.skew_tableau import SkewTableau
            sage: s = SkewTableau([[None, None, 1, 2], [None, 1], [4]])
            sage: w1 = GridViewWidget(s)
            sage: w2 = GridViewWidget(s, display_convention='fr')
            sage: len(w1.links)
            10
            sage: assert len(w1.links) == len(w2.links)
            sage: def test0(w): return (w.links[0].source[0].__class__, w.links[0].source[0].value, w.links[0].target[1])
            sage: def test4(w): return (w.links[4].source[0].__class__, w.links[4].source[0].value, w.links[4].target[1])
            sage: assert test0(w1) == test0(w2)
            sage: assert test4(w1) == test4(w2)
            sage: len(w2.links)
            10
            sage: w2.links[2].source[0].__class__
            <class 'sage_combinat_widgets.grid_view_widget.TextCell'>
            sage: w2.links[6].source[0].__class__
            <class 'sage_combinat_widgets.grid_view_widget.AddableTextCell'>
            sage: from traitlets import Bunch
            sage: w2.add_cell(Bunch({'name': 'add_0_4', 'old': 0, 'new': 3, 'owner': w2, 'type': 'change'}))
            sage: w2.value
            [[None, None, 1, 2, 3], [None, 1], [4]]
            sage: w2.links[2].source[0].__class__
            <class 'sage_combinat_widgets.grid_view_widget.TextCell'>
            sage: w2.links[7].source[0].__class__
            <class 'sage_combinat_widgets.grid_view_widget.AddableTextCell'>
        """
        for pos in self.cells.keys():
            traitname = 'cell_%d_%d' % (pos)
            child = self.get_child(pos)
            if child and hasattr(child, 'value') and traitname in self.traits():
                self.links.append(cdlink((child, 'value'), (self, traitname), self.cast))
        for pos in self.addable_cells():
            # A directional link to trait 'add_i_j'
            traitname = 'add_%d_%d' % (pos)
            child = self.get_child(pos)
            if child and hasattr(child, 'value') and traitname in self.traits():
                self.links.append(cdlink((child, 'value'), (self, traitname), self.cast))

    def draw(self, cell_widget_classes=None, cell_widget_class_index=None,
             addable_widget_class=None, blank_widget_class=None):
        r"""
        Add children to the GridWidget:
        - Sage object/grid editor cells
        - Blank cells for empty cells in a row
        - Addable cells if any
        Used classes can be passed as arguments
        to enable changing shapes, colors ..
        """
        self.donottrack = True # Prevent any interactivity while drawing the widget
        self.reset_links()
        self.compute_height()
        positions = sorted(list(self.cells.keys()))
        rows = [[(pos, self.cells[pos]) for pos in positions if pos[0]==i] \
                for i in range(self.height)]
        vbox_children = []
        addable_positions = self.addable_cells()
        addable_rows = []
        removable_positions = self.removable_cells()
        addable_rows = [(i,[pos for pos in addable_positions if pos[0]==i]) \
                        for i in set([t[0] for t in addable_positions])]
        if not cell_widget_classes:
            cell_widget_classes = self.cell_widget_classes
        if not cell_widget_class_index:
            cell_widget_class_index = self.cell_widget_class_index
        if not addable_widget_class:
            addable_widget_class = self.addable_widget_class
        if not blank_widget_class:
            blank_widget_class = self.blank_widget_class
        for i in range(self.height):
            r = rows[i]
            if not r: # Empty row
                if (i,0) in addable_positions:
                    vbox_children.append(HBox((addable_widget_class((i,0), layout=self.cell_layout),)))
                else:
                    vbox_children.append(HBox((blank_widget_class(layout=self.cell_layout, disabled=True),)))
                continue
            j = 0
            hbox_children = []
            while j<=max([t[0][1] for t in rows[i]]):
                if (i,j) in positions:
                    cell_content = self.cells[(i,j)]
                    cell_widget_class = cell_widget_classes[cell_widget_class_index((i,j))]
                    cell_display = self.adapter.cell_to_display(cell_content, self.displaytype)
                    cell = cell_widget_class(cell_display,
                                             (i,j),
                                             layout=self.cell_layout,
                                             placeholder=cell_display)
                    if (i,j) in removable_positions:
                        if issubclass(cell_widget_class, ToggleButton):
                            cell.description = '-'
                            cell.disabled = False
                        else:
                            cell.add_class('removablecell')
                    hbox_children.append(cell)
                elif (i,j) in addable_positions:
                    # Inside the grid-represented object limits
                    hbox_children.append(addable_widget_class((i,j), layout=self.cell_layout))
                else:
                    hbox_children.append(blank_widget_class(layout=self.cell_layout))
                j+=1
                if j > max([t[0][1] for t in rows[i]]) and (i,j) in addable_positions:
                    # Outside of the grid-represented object limits
                    hbox_children.append(self.addable_widget_class((i,j), layout=self.cell_layout))
            vbox_children.append(HBox(hbox_children))
        for row in addable_rows:
            if row[0] > i:
                vbox_children.append(HBox(
                    [self.addable_widget_class((i,j), layout=self.cell_layout) for c in row[1]]))
        if self.display_convention == 'fr':
            vbox_children.reverse()
        self.children = vbox_children
        self.add_links()
        self.donottrack = False

    def get_child(self, pos):
        r"""
        Get child widget corresponding to self.cells[pos]

        TESTS ::

            sage: from sage_combinat_widgets.grid_view_widget import GridViewWidget
            sage: t = StandardTableau([[1, 4, 7, 8, 9, 10, 11], [2, 5, 13], [3, 6], [12, 15], [14]])
            sage: w1 = GridViewWidget(t)
            sage: w1.get_child((1,2)).value
            u'13'
            sage: w2 = GridViewWidget(t, display_convention='fr')
            sage: w1.get_child((1,2)).value == w2.get_child((1,2)).value
            True
        """
        if self.display_convention == 'fr':
            return self.children[self.total_height - pos[0] - 1].children[pos[1]]
        return self.children[pos[0]].children[pos[1]]

    def set_dirty(self, pos, val, e=None):
        super(GridViewWidget, self).set_dirty(pos, val, e)
        child = self.get_child(pos)
        child.add_class('dirty')
        if e:
            child.set_tooltip(self.dirty_info(pos))

    def unset_dirty(self, pos):
        super(GridViewWidget, self).unset_dirty(pos)
        child = self.get_child(pos)
        child.remove_class('dirty')
        child.set_tooltip()

def PartitionGridViewWidget(obj, display_convention='en'):
    r"""
    A default widget for partitions.

    TESTS ::

        sage: from sage_combinat_widgets.grid_view_widget import PartitionGridViewWidget
        sage: sp = SkewPartition([[7, 4, 2, 1],[2, 1, 1]])
        sage: w = PartitionGridViewWidget(sp,  display_convention='fr')
        sage: len(w.links)
        17
    """
    return GridViewWidget(obj, cell_widget_classes=[ButtonCell],
                          addable_widget_class=AddableButtonCell, display_convention=display_convention)
