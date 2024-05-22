import pytest
import cadquery as cq
from cq_annotate.callouts import add_assembly_arrows
from cq_annotate.views import explode_assembly


def test_add_assembly_arrows():
    """
    Make sure that assembly arrows are added correctly to the assembly.
    """

    # Create the first assembly component
    box1 = cq.Workplane().workplane(offset=20.0).box(10, 10, 10)

    # Tag the face where the assembly arrow is desired
    box1.faces(">Z").tag("arrow")

    # Create a second assembly component to be assembled with the first
    # and tag the appropriate face
    box2 = cq.Workplane().box(10, 10, 10)
    box2.faces("<Z").tag("arrow")

    # The main assembly
    assy = cq.Assembly()

    # Add the assembly components
    assy.add(box1, name="box1", color=cq.Color(1, 0, 0, 1))
    assy.add(box2, name="box2", color=cq.Color(0, 1, 0, 1))

    # Add the arrows to the assembly and replace the original assembly
    assy = add_assembly_arrows(assy, arrow_scale_factor=0.5)

    # Make sure that the assembly has the correct number of children
    # The arrows are added as sub assemblies with their objects
    # 2 boxes + 2 arrows = 2 children/subassemblies
    assert len(assy.children) == 2


def test_explode_assembly():
    """
    Make sure that the explode_assembly function works correctly.
    """

    # Create the first assembly component
    box1 = cq.Workplane().workplane(offset=0.0).box(10, 10, 10)

    # Create a second assembly component to be assembled with the first
    box2 = cq.Workplane().workplane(offset=0.0).box(10, 10, 10)

    # The main assembly
    assy = cq.Assembly()

    # Add the assembly components
    assy.add(
        box1,
        loc=cq.Location((0, 0, 5)),
        metadata={"explode_loc": cq.Location((0, 0, 10))},
        color=cq.Color(1, 0, 0, 1),
    )
    assy.add(
        box2,
        loc=cq.Location((0, 0, -5)),
        metadata={"explode_loc": cq.Location((0, 0, -10))},
        color=cq.Color(0, 1, 0, 1),
    )

    # Make sure that the assembly children start at the correct positions
    assert assy.children[0].loc.toTuple()[0][2] == 5.0
    assert assy.children[1].loc.toTuple()[0][2] == -5.0

    # Explode the assembly, which will modify the existing assembly in-place
    explode_assembly(assy)

    # Make sure that the assembly children are now at the correct positions
    assert assy.children[0].loc.toTuple()[0][2] == 15.0
    assert assy.children[1].loc.toTuple()[0][2] == -15.0
