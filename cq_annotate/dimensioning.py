from math import radians, cos
import cadquery as cq


def add_circular_dimensions(obj, arrow_scale_factor=1.0):
    """
    Adds 3D arrows, leader lines and text to create diameter
    and radius dimensions.

    Parameters:
        obj - Object that has circular edges tagged for dimensions.
        arrow_scale_factor - Allows arrows to be scaled up and down so to match the scale of the object.

    Returns:
        An assembly containing the object along with the arrows, leader lines and text added at the proper location.
    """

    # Get the face location so that we can offset the arrow properly
    rad_edges = []
    for key, value in obj.ctx.tags.items():
        if key.startswith("radius"):
            rad_edges.append(key)

    # Build the base assembly
    assy = cq.Assembly()
    assy.add(obj)

    # Create the arrow head that points to each circular edge
    for rad_edge in rad_edges:
        # rad = edgs.val().BoundingBox().ylen / 2.0
        # length = obj.val().BoundingBox().xlen

        # Check to make sure the user only selected one edge
        edgs = obj.edges(tag=rad_edge)
        if len(edgs.all()) > 1:
            print("Please make sure that only 1 edge is tagged by the selector.")
            return None

        # Figure out the radius based on the dimensions of the edge
        rad = obj.edges(tag=rad_edge).val().radius()

        # Set the proportions of the arrow head
        tip_circle = 0.5 * arrow_scale_factor
        head_circle = 2.5 * arrow_scale_factor
        head_length = 10.0 * arrow_scale_factor

        # Figure out how the plane is oriented
        x_dir = obj.edges(tag=rad_edge).plane.xDir
        z_dir = obj.edges(tag=rad_edge).plane.zDir
        if x_dir == cq.Vector(1.0, 0.0, 0.0) and z_dir == cq.Vector(0.0, 0.0, 1.0):
            plane_name = "XY"
            extrude_sel = ">X"
            radial_vec = (0, 1, 0)
            circumference_vec = (0, 0, 1)
            rot_x = 0.0
            rot_y = -45.0
            rot_z = 0.0
            offset = obj.edges(tag=rad_edge).val().Center().z
            loc_vec = (
                rad * cos(radians(45)),
                rad * cos(radians(45)),
                offset,
            )
        elif x_dir == cq.Vector(0, 1, 0) and z_dir == cq.Vector(1, 0, 0):
            plane_name = "YZ"
            extrude_sel = ">Y"
            radial_vec = (0, 0, 1)
            circumference_vec = (1, 0, 0)
            rot_x = 45.0
            rot_y = 0.0
            rot_z = 0.0
            offset = obj.edges(tag=rad_edge).val().Center().x
            loc_vec = (
                offset,
                rad * cos(radians(45)),
                rad * cos(radians(45)),
            )

        # Create the arrow head and path up to the text
        arrow = (
            cq.Workplane(plane_name).circle(tip_circle).extrude(head_length, taper=-30)
        )
        arrow = arrow.rotate((0, 0, 0), radial_vec, 90)
        arrow = (
            arrow.faces(extrude_sel)
            .workplane(centerOption="CenterOfBoundBox")
            .circle(tip_circle)
            .extrude(10.0, combine=True)
            .faces(extrude_sel)
            .workplane(centerOption="CenterOfBoundBox")
            .transformed(rotate=(rot_x, rot_y, rot_z))
            .circle(tip_circle)
            .extrude(5.0)
        )
        arrow = arrow.rotate((0, 0, 0), circumference_vec, 45)

        # Add the arrow to the assembly
        assy.add(arrow, loc=cq.Location(loc_vec))

        # Calculate the correct position of the text
        if plane_name == "YZ":
            lr = assy.toCompound().BoundingBox().ylen / 2.0
            tb = assy.toCompound().BoundingBox().zlen / 2.0
            loc_tup = (offset, tb, lr)
        elif plane_name == "XY":
            lr = assy.toCompound().BoundingBox().xlen / 2.0
            tb = assy.toCompound().BoundingBox().ylen / 2.0
            loc_tup = (lr, tb, offset)

        # Create the text that will display the radius value
        text = (
            cq.Workplane(plane_name)
            .workplane(centerOption="CenterOfBoundBox")
            .text("R " + str(rad), fontsize=4, distance=1.0)
        )
        assy.add(text, loc=cq.Location((loc_tup[0], loc_tup[1] + 15.0, loc_tup[2])))

    return assy
