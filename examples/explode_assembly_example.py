import cadquery as cq
from cq_annotate.views import explode_assembly

# Create the first assembly component
box1 = cq.Workplane().workplane(offset=0.0).box(10, 10, 10)

# Create a second assembly component to be assembled with the first
box2 = cq.Workplane().workplane(offset=0.0).box(10, 10, 10)

# The main assembly
assy = cq.Assembly()

# Add the assembly components
# By default the unexploded assembly will have two boxes that are
# touching at the origin
# The metadata parameter is required so that cq-annotate knows the
# direction and amount to translate the exploded assembly components by
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

# Explode the assembly, which will modify the existing assembly
# in-place
# Note that this will not work once a sub-assembly has been added to a main assembly
explode_assembly(assy)

# This only exists so that users running the example in CQ-editor
# can see the result
if "show_object" in globals():
    show_object(assy)
