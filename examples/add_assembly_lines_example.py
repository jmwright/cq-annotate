import cadquery as cq
from cq_annotate.views import explode_assembly
from cq_annotate.callouts import add_assembly_lines

# Create the first assembly component
screw = cq.Workplane().circle(3.0).extrude(10.0).faces(">Z").circle(4.5).extrude(4.0)

# Tag the face where the assembly arrow is desired
screw.faces("<Z").tag("assembly_line")

# Create a second assembly component to be assembled with the first
# and tag the appropriate face
box = cq.Workplane().rect(10, 10).extrude(10)
box = box.faces("<Z").circle(3.0).cutThruAll()
# box2.faces(">Z").tag("assembly_line")

# The main assembly
assy = cq.Assembly()

# Add the assembly components
# The name parameter is required so that tagged faces can be found
assy.add(
    screw,
    name="screw",
    color=cq.Color(1, 0, 0, 1),
    metadata={"explode_loc": cq.Location((0, 0, 20))},
)
assy.add(box, name="box", color=cq.Color(0, 1, 0, 1))

# Explode the assembly so that we have a reason to use the assembly lines
explode_assembly(assy)

# Add the arrows to the assembly and replace the original assembly
# The arrows end up being new assembly components, but are not
# positioned via constraints to decrease the risk that solving
# those constraints will not break the assembly
# The original arrow is too large for the box, so a scale factor
# is applied
add_assembly_lines(assy)

# This only exists so that users running the example in CQ-editor
# can see the result
if "show_object" in globals():
    show_object(assy)
