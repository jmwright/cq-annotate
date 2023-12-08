import cadquery as cq
from cq_annotate.dimensioning import add_circular_dimensions

# Create a basic object that we will add a dimension to
bd = cq.Workplane("YZ").circle(10.0).circle(5.0).extrude(50.0)
bd.edges("%CIRCLE").edges(cq.selectors.RadiusNthSelector(1)).edges(">X").tag("radius_1")

# Add the radius dimension
assy = add_circular_dimensions(bd, arrow_scale_factor=0.1)

show_object(assy)
