# -*- coding: utf-8 -*-
r"""
An editable Grid View Editor for Sage objects

EXAMPLES::
    sage: from sage_combinat_widgets import GridViewEditor
    sage: t = StandardTableau([[1, 2, 5, 6], [3], [4]])
    sage: e = GridViewEditor(t)
    sage: e.addable_cells()
    [(0, 4), (1, 1), (3, 0)]
    sage: from sage.graphs.generators.basic import GridGraph
    sage: g = GridGraph((4,3))
    sage: e = GridViewEditor(g)
    sage: R = PolynomialRing(QQ, 9, 'x')
    sage: A = matrix(R, 3, 3, R.gens())
    sage: e = GridViewEditor(A)

AUTHORS: Odile Bénassy, Nicolas Thiéry
"""
import re, traitlets
from six import add_metaclass
from copy import copy
from sage.misc.bindable_class import BindableClass
from sage.all import SageObject
from sage.misc.abstract_method import AbstractMethod
from sage.misc.misc import uniq

def extract_coordinates(s):
    r"""
    Extract a coordinate pair from a string with tokens.

    TESTS::
        sage: from sage_combinat_widgets.grid_view_editor import extract_coordinates
        sage: extract_coordinates('add_0_4')
        (0, 4)
    """
    patt = re.compile('_([0-9]+)_([0-9]+)')
    m = patt.search(s)
    if m:
        return tuple(int(i) for i in m.groups())

def get_adapter(obj):
    r"""
    Return an adapter object for Sage object `obj`.

    INPUT:

        - ``obj`` -- a Sage object

    OUTPUT: an adapter object

    TESTS::
        sage: from sage_combinat_widgets.grid_view_editor import get_adapter
        sage: from sage.combinat.partition import Partition
        sage: p = Partition([3,2,1,1])
        sage: pa = get_adapter(p)
        sage: pa.cellzero
        False
        sage: from sage.combinat.tableau import StandardTableaux
        sage: t = StandardTableaux(7).random_element()
        sage: ta = get_adapter(t)
        sage: ta.cellzero
        0
    """
    from sage.combinat.partition import Partition
    if issubclass(obj.__class__, Partition):
        from sage_widget_adapters.combinat.partition_grid_view_adapter import PartitionGridViewAdapter
        return PartitionGridViewAdapter()
    from sage.combinat.skew_partition import SkewPartition
    if issubclass(obj.__class__, SkewPartition):
        from sage_widget_adapters.combinat.skew_partition_grid_view_adapter import SkewPartitionGridViewAdapter
        return SkewPartitionGridViewAdapter()
    from sage.combinat.tableau import Tableau
    if issubclass(obj.__class__, Tableau):
        from sage.combinat.tableau import SemistandardTableau, StandardTableau
        if issubclass(obj.__class__, StandardTableau):
            from sage_widget_adapters.combinat.tableau_grid_view_adapter import StandardTableauGridViewAdapter
            return StandardTableauGridViewAdapter()
        if issubclass(obj.__class__, SemistandardTableau):
            from sage_widget_adapters.combinat.tableau_grid_view_adapter import SemistandardTableauGridViewAdapter
            return SemistandardTableauGridViewAdapter()
        from sage_widget_adapters.combinat.tableau_grid_view_adapter import TableauGridViewAdapter
        return TableauGridViewAdapter()
    from sage.combinat.skew_tableau import SkewTableau
    if issubclass(obj.__class__, SkewTableau):
        from sage_widget_adapters.combinat.skew_tableau_grid_view_adapter import SkewTableauGridViewAdapter
        return SkewTableauGridViewAdapter()
    from sage.matrix.matrix2 import Matrix
    if issubclass(obj.__class__, Matrix):
        from sage_widget_adapters.matrix.matrix_grid_view_adapter import MatrixGridViewAdapter
        return MatrixGridViewAdapter(obj)
    from sage.graphs.graph import Graph
    if issubclass(obj.__class__, Graph):
        from sage_widget_adapters.graphs.graph_grid_view_adapter import GraphGridViewAdapter
        return GraphGridViewAdapter()

class cdlink(traitlets.link):
    r"""
    A directional link (for a start) with type casting
    """
    def __init__(self, source, target, cast):
        r"""
        Type-casting directional link initialisation.

        INPUT:

            - ``source`` -- a pair (source widget, trait name)
            - ``target`` -- a pair (target widget, trait name)
            - ``cast`` -- a cast function

        TESTS::
            sage: from sage_combinat_widgets.grid_view_editor import cdlink
            sage: from ipywidgets import Checkbox, Text
            sage: b = Checkbox()
            sage: t = Text()
            sage: l = cdlink((b, 'value'), (t, 'value'), str)
            sage: t.value
            u'False'
        """
        self.source, self.target, self.to_cell = source, target, cast
        try:
            setattr(target[0], target[1], cast(getattr(source[0], source[1])))
        finally:
            source[0].observe(self._update_target, names=source[1])
            target[0].observe(self._update_source, names=target[1])

    def __repr__(self):
        r"""
        Try to get a useful repr for our link class.
        """
        return "A typecasting directional link from source=(%s, %s) to target='%s'" % (self.source[0].__class__, self.source[0].value, self.target[1])

    def _update_target(self, change):
        if self.updating:
            return
        with self._busy_updating():
            setattr(self.target[0], self.target[1], self.to_cell(change.new))

import sage.misc.classcall_metaclass
class MetaHasTraitsClasscallMetaclass(traitlets.MetaHasTraits, sage.misc.classcall_metaclass.ClasscallMetaclass):
    pass
@add_metaclass(MetaHasTraitsClasscallMetaclass)
class BindableClassWithMeta(BindableClass):
    pass
class BindableEditorClass(traitlets.HasTraits, BindableClassWithMeta):
    pass

class GridViewEditor(BindableEditorClass):
    r"""Base Editor for grid-representable Sage Objects

    Composed of cells. No decision made here about cell representation.
    The cell trait objects will store values
    that are refered to through object cells as a dictionary
    with coordinates (row_number, cell_number_in_row) as keys
    """
    value = traitlets.Any()

    def __init__(self, obj, adapter=None):
        r"""
        Initialize editor.

        INPUT:

            - ``obj`` -- a Sage object
            - ``adapter`` -- an adapter object (optional)

        TESTS::
            sage: from sage_combinat_widgets import GridViewEditor
            sage: from sage.graphs.generic_graph import GenericGraph
            sage: e = GridViewEditor(graphs.AztecDiamondGraph(2))
            sage: e.cells
            {(0, 1): None, (0, 2): None, (1, 0): None, (1, 1): None, (1, 2): None, (1, 3): None, (2, 0): None,
            (2, 1): None, (2, 2): None, (2, 3): None, (3, 1): None, (3, 2): None}
            sage: e = GridViewEditor(StandardTableaux(5).random_element())
            sage: e.cells
            {(0, 0): 1, (1, 0): 2, (2, 0): 3, (3, 0): 4, (4, 0): 5}
            sage: e = GridViewEditor(vector((1,2,3)))
            Traceback (most recent call last):
            ...
            TypeError: Cannot find an Adapter for this object (<type 'sage.modules.vector_integer_dense.Vector_integer_dense'>)
            sage: e = GridViewEditor(x^5)
            Traceback (most recent call last):
            ...
            TypeError: Cannot find an Adapter for this object (<type 'sage.symbolic.expression.Expression'>)
        """
        self.initialization = True
        super(GridViewEditor, self).__init__()
        self.value = obj
        self.dirty = {}
        if adapter:
            self.adapter = adapter
        else:
            self.adapter = get_adapter(obj)
        if not self.adapter:
            raise TypeError("Cannot find an Adapter for this object (%s)" % obj.__class__)
        if not hasattr(self.adapter, 'compute_cells') or not callable(self.adapter.compute_cells):
            raise NotImplementedError("Method `compute_cells` is required!")
        self.compute()
        self.links = []

    def to_cell(self, val):
        r"""
        From a widget cell value `val`,
        return a valid editor cell value.
        Will be overloaded in widget code.
        """
        return val

    def validate(self, obj, value=None, obj_class=None):
        r"""
        Validate object type.
        """
        if obj_class:
            return issubclass(obj.__class__, obj_class)
        return issubclass(obj.__class__, SageObject)

    def modified_add_traits(self, **traits):
        r"""
        Dynamically add trait attributes to the HasTraits instance.
        Modified code according to Ryan Morshead's pull request
        Cf https://github.com/ipython/traitlets/pull/501
        """
        cls = self.__class__
        attrs = {"__module__": cls.__module__}
        if hasattr(cls, "__qualname__"):
          # __qualname__ introduced in Python 3.3 (see PEP 3155)
          attrs["__qualname__"] = cls.__qualname__
        attrs.update(traits)
        self.__class__ = type(cls.__name__, (cls,), attrs)
        for trait in traits.values():
            trait.instance_init(self)

    def compute(self, obj=None):
        r"""We have an object value
        but we want to compute cells
        as a dictionary (row_number, cell_number_in_row) -> trait
        """
        if not obj:
            obj = self.value
        if not obj:
            return
        self.cells = self.adapter.compute_cells(obj)
        celltype = self.adapter.celltype
        cellzero = self.adapter.cellzero
        addablecelltype = self.adapter.addablecelltype or celltype
        addablecellzero = self.adapter.addablecellzero or cellzero
        traitclass = self.adapter.traitclass
        traits_to_add = {}
        for pos in self.addable_cells():
            # Empty traits for addable cells
            emptytraitname = 'add_%d_%d' % pos
            try:
                emptytrait = traitclass(addablecellzero)
            except:
                try:
                    emptytrait = traitclass(addablecelltype)
                except:
                    raise TypeError("Cannot init the trait (traitclass=%s, celltype=%s, default_value=%s)" % (traitclass, addablecelltype, addablecellzero))
            emptytrait.name = emptytraitname
            traits_to_add[emptytraitname] = emptytrait
        for pos, val in self.cells.items():
            traitname = 'cell_%d_%d' % pos
            traitvalue = val
            if traitname in self._trait_values:
                self._trait_values[traitname] = traitvalue
            else:
                try:
                    trait = traitclass(traitvalue)
                except:
                    try:
                        trait = traitclass(celltype)
                        trait.value = traitvalue
                    except:
                        raise TypeError("Cannot init the trait (traitclass=%s, celltype=%s, default_value=%s)" % (traitclass, celltype, cellzero))
                trait.name = traitname
                traits_to_add[traitname] = trait
        self.traitclass = traitclass
        self.modified_add_traits(**traits_to_add)

    def compute_height(self):
        r"""
        Compute grid height, addable cells included.

        TESTS::
            sage: from sage_combinat_widgets import GridViewEditor
            sage: from sage.combinat.partition import Partition
            sage: e = GridViewEditor(Partition([3,3,2,1]))
            sage: e.compute_height()
            sage: e.height
            5
            sage: from sage.graphs.generators.families import AztecDiamondGraph
            sage: e = GridViewEditor(AztecDiamondGraph(2))
            sage: e.compute_height()
            sage: e.height
            4
        """
        if not hasattr(self, 'cells'):
            self.compute()
        maxpos = max(pos[0] for pos in self.cells)
        for pos in self.addable_cells():
            if pos[0] > maxpos:
                maxpos = pos[0]
        self.height = maxpos + 1

    def reset_links(self):
        r"""
        Reset all potentially existing links
        between widget cells and corresponding traits.
        """
        for lnk in self.links:
            lnk.unlink()
        self.links = []

    def draw(self, cast=None):
        r"""
        Build the visual representation
        and cdlink objects -- with cast function `cast`.
        """
        pass

    def get_value(self):
        r"""
        Return editor value.
        """
        return self.value

    def set_value(self, obj, compute=True):
        r"""
        Check compatibility, then set editor value.
        If compute=True, call methods compute() and draw().
        """
        if not self.validate(obj, self.value.__class__):
            raise ValueError("Object %s is not compatible." % str(obj))
        self.value = obj
        if compute:
            self.compute()
            self.draw()

    def get_cells(self):
        r"""
        Return grid editor cells.
        """
        return self.cells

    def set_value_from_cells(self, obj_class=None, cells={}):
        r"""We have an object value, but we want to change it according to cells
        Yet we want to keep the same class (or warn if that's impossible)

        INPUT:

            -  ``obj_class`` -- an object class (by default: self.value.__class__)
            -  ``cells`` -- a dictionary (i,j)->val
        """
        if not obj_class and self.value:
            obj_class = self.value.__class__
        if not obj_class:
            return
        if hasattr(self.adapter, 'from_cells'):
            try:
                obj = self.adapter.from_cells(cells)
            except:
                raise ValueError("Could not make an object of class '%s' from given cells" % str(obj_class))
        elif hasattr(obj_class, 'cells') or hasattr(obj_class, 'rows'): # e.g. a tableau / matrix / vector
            positions = sorted(list(cells.keys()))
            for cl in obj_class.__mro__:
                try:
                    obj = cl([[cells[pos] for pos in positions if pos[0]==i] for i in uniq([t[0] for t in positions])])
                except:
                    print("These cells cannot be turned into a %s" % cl)
        else:
            raise TypeError("Unable to cast the given cells into a grid-like object.")
        if not self.validate(obj, None, obj_class):
            raise ValueError("Could not make a compatible ('%s')  object from given cells" % str(obj_class))
        self.set_value(obj, False)

    @traitlets.observe(traitlets.All)
    def set_cell(self, change):
        r"""
        TESTS::
            sage: from sage_combinat_widgets import GridViewEditor
            sage: t = Tableau([[1, 2, 5, 6], [3], [4]])
            sage: e = GridViewEditor(t)
            sage: e.initialization = False # This class is not meant to work by itself without a widget.
            sage: from traitlets import Bunch
            sage: change = Bunch({'name': 'cell_0_2', 'old': 5, 'new': 7, 'owner': e, 'type': 'change'})
            sage: e.set_cell(change)
            sage: e.value
            [[1, 2, 7, 6], [3], [4]]
        """
        if self.initialization:
            return
        if not change.name.startswith('cell_'):
            return
        if change.old == traitlets.Undefined: # Do nothing on a newly added cell
            return
        if change.new == change.old or not change.new:
            return
        pos = extract_coordinates(change.name)
        val = change.new
        obj = copy(self.value)
        new_obj = self.adapter.set_cell(obj, pos, val, dirty=self.dirty)
        if new_obj == obj:
            self.dirty[pos] = val # Add an entry in self.dirty dictionary
            self.draw() # Reverse the display change
            return
        self.set_value(new_obj, False)
        # Edit the cell dictionary
        self.cells[pos] = val
        # Edit the trait
        traitname = 'cell_%d_%d' % pos
        self.set_trait(traitname, val)

    def addable_cells(self):
        r"""
        List addable cells for editor value
        """
        if not hasattr(self.adapter, 'addable_cells') or not callable(self.adapter.addable_cells):
            return [] # Optional method
        return self.adapter.addable_cells(self.value)

    def removable_cells(self):
        r"""
        List removable cells for editor value
        """
        if not hasattr(self.adapter, 'removable_cells') or not callable(self.adapter.removable_cells):
            return [] # Optional method
        return self.adapter.removable_cells(self.value)

    @traitlets.observe(traitlets.All)
    def add_cell(self, change):
        r"""
        TESTS:
            sage: from sage_combinat_widgets import GridViewEditor
            sage: t = Tableau([[1, 2, 5, 6], [3], [4]])
            sage: e = GridViewEditor(t)
            sage: from traitlets import Bunch
            sage: change = Bunch({'name': 'add_1_1', 'old': 0, 'new': 8, 'owner': e, 'type': 'change'})
            sage: e.add_cell(change)
            sage: e.value
            [[1, 2, 5, 6], [3, 8], [4]]
            sage: t = StandardTableau([[1, 2, 5, 6], [3], [4]])
            sage: e = GridViewEditor(t)
            sage: e.add_cell(change)
            Cell (1, 1) with value '8' cannot be added to this object!
            sage: e.value
            [[1, 2, 5, 6], [3], [4]]
            sage: e = GridViewEditor(SkewTableau([[None, None, 1, 2], [None, 1], [4]]))
            sage: e.add_cell(Bunch({'name': 'add_0_4', 'old': 0, 'new': 3, 'owner': e, 'type': 'change'}))
            sage: e.value
            [[None, None, 1, 2, 3], [None, 1], [4]]
            sage: e.add_cell(Bunch({'name': 'add_1_0', 'old': 0, 'new': 1, 'owner': e, 'type': 'change'}))
            sage: e.value
            [[None, None, 1, 2, 3], [1, 1], [4]]
        """
        if not change.name.startswith('add_') \
           or self.to_cell(change.new) == self.adapter.cellzero:
            return
        if not hasattr(self.adapter, 'add_cell'):
            raise TypeError("Cannot add cell to this object.")
        if self.adapter.add_cell.__func__.__class__ is AbstractMethod:
            return # Method not implemented
        val = change.new
        if val is True:
            val = False # if it's a button, reverse button toggling
        pos = extract_coordinates(change.name)
        obj = copy(self.value)
        new_obj = self.adapter.add_cell(obj, pos, val)
        if not self.validate(new_obj):
            raise ValueError("This new object is not compatible with editor object class (%s)" % self.value.__class__)
        if new_obj == obj: # The proposed change was invalid -> stop here
            self.draw() # Reverse the display change
            return
        self.set_value(new_obj) # Calls compute() and draw() by default

    @traitlets.observe(traitlets.All)
    def remove_cell(self, change):
        r"""
        TESTS::
            sage: from sage_combinat_widgets import GridViewEditor
            sage: t = Tableau([[1, 2, 5, 6], [3], [4]])
            sage: e = GridViewEditor(t)
            sage: from traitlets import Bunch
            sage: e.remove_cell(Bunch({'name': 'cell_0_3', 'old': 6, 'new': 0, 'owner': e, 'type': 'change'}))
            sage: e.value
            [[1, 2, 5], [3], [4]]
            sage: e.remove_cell(Bunch({'name': 'cell_2_0', 'old': 4, 'new': 0, 'owner': e, 'type': 'change'}))
            sage: e.value
            [[1, 2, 5], [3]]
            sage: e = GridViewEditor(SkewTableau([[None, None, 1, 2, 3], [None, 1], [4]]))
            sage: e.remove_cell(Bunch({'name': 'cell_0_4', 'old': 3, 'new': 0, 'owner': e, 'type': 'change'}))
            sage: e.value
            [[None, None, 1, 2], [None, 1], [4]]
        """
        if not change.name.startswith('cell_'):
            return
        if not hasattr(self.adapter, 'remove_cell'):
            raise TypeError("Cannot remove cell from this object.")
        if hasattr(self.adapter.remove_cell, '_optional') and self.adapter.remove_cell._optional: # Not implemented
            return
        if change.old == traitlets.Undefined: # Do nothing at widget initializing
            return
        if change.new == True: # if it's a button, reverse button toggling
            change.new = False
        if change.new != self.adapter.cellzero: # non empty cells are not to be removed
            return
        if change.new == self.adapter.addablecellzero:
            return # never remove addable cells ; will do sth only if adapter addablecellzero is specified (therefore not eq to cellzero)
        pos = extract_coordinates(change.name)
        obj = copy(self.value)
        new_obj = self.adapter.remove_cell(obj, pos)
        if not self.validate(new_obj):
            raise ValueError("This new object is not compatible with editor object class (%s)" % self.value.__class__)
        if new_obj == obj: # The proposed change was invalid -> stop here
            self.draw() # Reverse the display change
            return
        self.set_value(new_obj) # Calls compute() and draw() by default

    def append_row(self, r=None):
        r"""
        Append a row to editor value.

        TESTS::
            sage: from sage_combinat_widgets import GridViewEditor
            sage: from sage.matrix.matrix_space import MatrixSpace
            sage: S = MatrixSpace(ZZ, 4,3)
            sage: m = S.matrix([1,7,1,0,0,3,0,-1,2,1,0,-3])
            sage: e = GridViewEditor(m)
            sage: e.value
            [ 1  7  1]
            [ 0  0  3]
            [ 0 -1  2]
            [ 1  0 -3]
            sage: e.append_row((1,2,3))
            sage: e.value
            [ 1  7  1]
            [ 0  0  3]
            [ 0 -1  2]
            [ 1  0 -3]
            [ 1  2  3]
            sage: from sage.combinat.tableau import Tableau
            sage: e = GridViewEditor(Tableau([[1, 4, 7, 8, 9, 10, 11], [2, 5, 13], [3, 6], [12, 15], [14]]))
            sage: e.value
            [[1, 4, 7, 8, 9, 10, 11], [2, 5, 13], [3, 6], [12, 15], [14]]
            sage: e.append_row((1,2,3))
            Traceback (most recent call last):
            ...
            TypeError: 'NotImplementedType' object is not callable
        """
        if not hasattr(self.adapter, 'append_row'):
            raise TypeError("Cannot append row to this object.")
        obj = copy(self.value)
        obj = self.adapter.append_row(obj, r)
        self.set_value(obj) # Will take care of everything

    def insert_row(self, index, r=None):
        r"""
        Insert a row into editor value.
        """
        if not hasattr(self.adapter, 'insert_row'):
            raise TypeError("Cannot insert row to this object.")
        obj = copy(self.value)
        obj = self.adapter.insert_row(obj, index, r)
        self.set_value(obj) # Will take care of everything

    def remove_row(self, index=None):
        r"""
        Remove a row from editor value.
        """
        if not hasattr(self.adapter, 'remove_row'):
            raise TypeError("Cannot remove row from this object.")
        obj = copy(self.value)
        obj = self.adapter.remove_row(obj, index)
        self.set_value(obj) # Will take care of everything

    def append_column(self, c=None):
        r"""
        Append a column to editor value.

        TESTS::
            sage: from sage_combinat_widgets import GridViewEditor
            sage: from sage.matrix.matrix_space import MatrixSpace
            sage: S = MatrixSpace(ZZ, 4,3)
            sage: m = S.matrix([1,7,1,0,0,3,0,-1,2,1,0,-3])
            sage: e = GridViewEditor(m)
            sage: e.value
            [ 1  7  1]
            [ 0  0  3]
            [ 0 -1  2]
            [ 1  0 -3]
            sage: e.append_column((1,2,3))
            sage: e.value
            [ 1  7  1  1]
            [ 0  0  3  2]
            [ 0 -1  2  3]
            [ 1  0 -3  0]
            sage: from sage.combinat.tableau import Tableau
            sage: e = GridViewEditor(Tableau([[1, 4, 7, 8, 9, 10, 11], [2, 5, 13], [3, 6], [12, 15], [14]]))
            sage: e.value
            [[1, 4, 7, 8, 9, 10, 11], [2, 5, 13], [3, 6], [12, 15], [14]]
            sage: e.append_column((1,2,3))
            Traceback (most recent call last):
            ...
            TypeError: 'NotImplementedType' object is not callable
        """
        if not hasattr(self.adapter, 'append_column'):
            raise TypeError("Cannot append column to this object.")
        obj = copy(self.value)
        obj = self.adapter.append_column(obj, c)
        self.set_value(obj) # Will take care of everything

    def insert_column(self, index, c=None):
        r"""
        Insert a column into editor value.
        """
        if not hasattr(self.adapter, 'insert_column'):
            raise TypeError("Cannot insert column to this object.")
        obj = copy(self.value)
        obj = self.adapter.insert_column(obj, index, c)
        self.set_value(obj) # Will take care of everything

    def remove_column(self, index=None):
        r"""
        Remove a column from editor value.
        """
        if not hasattr(self.adapter, 'remove_column'):
            raise TypeError("Cannot remove column from this object.")
        obj = copy(self.value)
        obj = self.adapter.remove_column(obj, index)
        self.set_value(obj, True) # Will take care of everything
