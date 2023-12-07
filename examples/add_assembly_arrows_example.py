import cadquery as cq
from cq_annotate.callouts import add_assembly_arrows

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
# The name parameter is required so that tagged faces can be found
assy.add(box1, name="box1", color=cq.Color(1, 0, 0, 1))
assy.add(box2, name="box2", color=cq.Color(0, 1, 0, 1))

# Add the arrows to the assembly and replace the original assembly
# The arrows end up being new assembly components, but are not
# positioned via constraints to decrease the risk that solving
# those constraints will not break the assembly
# The original arrow is too large for the box, so a scale factor
# is applied
assy = add_assembly_arrows(assy, arrow_scale_factor=0.5)

# This only exists so that users running the example in CQ-editor
# can see the result
if "show_object" in globals():
    show_object(assy)
