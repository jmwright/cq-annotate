import pytest
import cadquery as cq
from cq_annotate.callouts import add_assembly_arrows, add_assembly_lines
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


def test_add_assembly_lines():
    """
    Make sure that assembly lines are added correctly to the assembly.
    """

    #
    # Create a simple screw
    #
    # The threaded portion
    screw = (
        cq.Workplane()
        .workplane(centerOption="CenterOfBoundBox")
        .circle(2.5 / 2.0)
        .extrude(6.0)
    )
    # Overall head shape
    screw = screw.faces(">Z").circle(4.5 / 2.0).extrude(2.5)
    # Add the hex drive cutout
    screw = (
        screw.faces(">Z")
        .workplane(centerOption="CenterOfBoundBox")
        .polygon(6, 2.0)
        .cutBlind(-2.0)
    )
    # Tag the bottom face for an assembly arrow
    screw.faces("<Z").tag("assembly_line")

    #
    # Create the object that the screw fits into
    #
    box1 = cq.Workplane().box(10, 10, 10)
    box1 = box1.faces(">Z").hole(2.5)

    #
    # Create the assembly that puts the objects together
    #
    assy = cq.Assembly()
    assy.add(box1, name="box")
    assy.add(
        screw,
        name="screw",
        loc=cq.Location((0.0, 0.0, -1.0)),
        metadata={"explode_loc": cq.Location((0.0, 0.0, 10.0))},
    )

    #
    # Add the assembly line
    #
    add_assembly_lines(assy)

    # Make sure that the assembly has the correct number of children
    # The lines are added as sub assemblies with their objects
    # 1 box + 1 screw + 1 arrow = 2 children/subassemblies
    assert len(assy.children) == 2


def test_add_assembly_lines_non_z():
    """
    Make sure that assembly lines are added correctly to the assembly when other axis selectors
    are used.
    """

    #
    # Create a simple screw
    #
    # The threaded portion
    screw = (
        cq.Workplane()
        .workplane(centerOption="CenterOfBoundBox")
        .circle(2.5 / 2.0)
        .extrude(6.0)
    )
    # Overall head shape
    screw = screw.faces(">Z").circle(4.5 / 2.0).extrude(2.5)
    # Add the hex drive cutout
    screw = (
        screw.faces(">Z")
        .workplane(centerOption="CenterOfBoundBox")
        .polygon(6, 2.0)
        .cutBlind(-2.0)
    )
    # Tag the bottom face for an assembly arrow
    screw.faces("<Z").tag("assembly_line")

    #
    # Create the object that the screw fits into
    #
    box1 = cq.Workplane().box(10, 10, 10)
    box1 = box1.faces(">X").workplane().hole(2.5)

    #
    # Create the assembly that puts the objects together
    #
    assy = cq.Assembly()
    assy.add(box1, name="box")
    assy.add(
        screw,
        name="screw",
        loc=cq.Location((0.0, 0.0, 0.0), (0, 1, 0), 90),
        metadata={"explode_loc": cq.Location((0.0, 0.0, 10.0))},
    )
    assy.add(
        screw,
        name="screw_2",
        loc=cq.Location((0.0, 0.0, 0.0), (0, 1, 0), -90),
        metadata={"explode_loc": cq.Location((0.0, 0.0, 10.0))},
    )

    # Explode the assembly, which will modify the existing assembly in-place
    explode_assembly(assy)

    #
    # Add the assembly line
    #
    add_assembly_lines(assy)

    # Make sure that the assembly has the correct number of children
    assert len(assy.children) == 3


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
