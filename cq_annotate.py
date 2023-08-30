import os
from math import degrees, radians, cos, sin
import cadquery as cq
import svgutils.transform as sg
from svgutils.compose import Unit


def add_assembly_arrows(assy, arrow_scale_factor=1.0):
    """
    Adds 3D arrows to the assembly at the locations of faces tagged with "arrow".
    Example: `my_object.faces(">Y").tag("arrow")`

    Parameters:
        assy - The assembly that may have locations tagged for arrows.
        arrow_scale_factor - Allows arrows to be scaled up and down so that they match the size of the

    Returns:
        The same assembly with the arrows added at the proper location
    """

    # Sibassembly that will hold all of the assembly arrows
    sub_assy = cq.Assembly()

    # Search each assembly part for a face tagged "arrow"
    for i, child in enumerate(assy.children):
        try:
            # Get the face location so that we can offset the arrow properly
            face = child._query(child.name + "?arrow")
            face_center = face[1].Center()
            face_loc = cq.Location((face_center.x, face_center.y, face_center.z))

            # Create the arrow object
            tip_circle = 0.5 * arrow_scale_factor
            head_circle = 2.5 * arrow_scale_factor
            head_length = 10.0 * arrow_scale_factor
            arrow = cq.Workplane().circle(tip_circle).extrude(head_length, taper=-30)
            arrow = (
                arrow.faces(">Z").workplane(centerOption="CenterOfBoundBox").circle(head_circle).extrude(head_length)
            )

            # Figure out the angle between the normal vector of the face and the length axis of the arrow
            face_normal = face[1].normalAt(cq.Vector(0, 0, 0))
            rotation_angle = face_normal.wrapped.AngleWithRef(
                cq.Vector(0, 0, 1).wrapped, cq.Vector(-1, -1, -1).wrapped
            )
            rotation_angle = degrees(rotation_angle)

            # Rotate the arrow around its tip so that it will be in the correct position
            arrow = arrow.rotate((-10, 0, 0), (10, 0, 0), rotation_angle)

            # Make the assembly arrow part of the assembly
            sub_assy.add(
                arrow,
                name="arrow_" + str(i),
                loc=child.loc * face_loc,
                color=cq.Color(0.0, 0.0, 0.0, 1.0),
            )
        except Exception:
            pass

    # If the sub-assembly
    if len(sub_assy.children) > 0:
        assy.add(sub_assy, name="arrows")

    return assy


def explode_assembly(assy):
    """
    Explodes an assembly by moving the parts away in predefined directions and distances
    that should be included in each assembly child's metadata.
    Example: `assy.add(my_object, metadata={"explode_loc": cq.Location((0, 30, 0))})`
    If parts are rotated and moved by setting the location or by constraint solving, one
    technique is to pass a face selector parameter to the constructor for your part so
    that you can be sure the correct face will be tagged, no matter the orientation.

    NOTE: This will not work once a sub-assembly has been added to a main assembly.

    Parameters:
        assy - The assembly which is to be exploded.

    Returns:
        Nothing, modifies the assembly in-place
    """

    # Explode the stereoscope sub-assembly
    for child in assy.children:
        if "explode_loc" in child.metadata:
            child.loc = child.loc * child.metadata["explode_loc"]


def add_safety_warning(svg_path, text, use_icon=True, font_size=24):
    """
    Adds a safety warning to an SVG file. The warning can be a text message with an optional icon.

    Parameters:
        svg_path - File path to the SVG to add the safety warning to.
        text - String that should be displayed as the safety warning.
        use_icon - Whether or not to display a stock safety icon with the text warning.
        font_size - Font size to use for the warning text.

    Returns:
        Nothing, modifies the SVG file in-place
    """

    # Load the SVG that we want to annotate
    view = sg.fromfile(svg_path)
    view_size = view.get_size()
    view = view.getroot()

    if use_icon:
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        icon = sg.fromfile(os.path.join(cur_dir, "icons/safety_warning.svg")).getroot()
        icon.moveto(5, 5, scale_x=0.4, scale_y=0.4)

    # Create an SVG to put the result in
    fig = sg.SVGFigure(
        Unit(str(view_size[0].split(".")[0]) + "px"),
        Unit(str(view_size[1].split(".")[0]) + "px"),
    )

    # Add text labels
    txt1 = sg.TextElement(45, 35, text, size=font_size, weight="bold")

    # Build the final SVG
    imgs = [view, txt1]
    if use_icon:
        imgs.append(icon)
    fig.append(imgs)

    # Save the SVG
    fig.save(svg_path)


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
        arrow = (
            arrow.rotate((0, 0, 0), radial_vec, 90)
        )
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
        text = cq.Workplane(plane_name).workplane(centerOption="CenterOfBoundBox").text("R " + str(rad), fontsize=4, distance=1.0)
        assy.add(text, loc=cq.Location(loc_tup))

    return assy
