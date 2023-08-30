import pytest
import cadquery as cq
from cq_annotate import add_circular_dimensions


def test_add_radius_dimension():
    """
    Tests adding a callout for the radius dimension.
    """

    from cadquery.vis import show

    bd = cq.Workplane("YZ").circle(10.0).circle(5.0).extrude(50.0)
    bd.edges("%CIRCLE").edges(cq.selectors.RadiusNthSelector(1)).edges(">X").tag(
        "radius_1"
    )

    # Add the radius dimension
    assy = add_circular_dimensions(bd, arrow_scale_factor=0.1)

    show(assy)

    # assert(len(assy.children) == 3)

    bd2 = cq.Workplane("XY").circle(100.0).circle(90.0).extrude(50.0)
    bd2.edges("%CIRCLE").edges(cq.selectors.RadiusNthSelector(1)).edges(">Z").tag(
        "radius_2"
    )

    # Add the radius dimension
    assy2 = add_circular_dimensions(bd2, arrow_scale_factor=0.1)

    show(assy2)

    assert len(assy2.children) == 3
