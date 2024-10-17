import cadquery as cq
from math import degrees, sqrt


def add_assembly_arrows(assy, arrow_scale_factor=1.0):
    """
    Adds 3D arrows to the assembly at the locations of faces tagged with "arrow".
    Example: `my_object.faces(">Y").tag("arrow")`

    Parameters:
        assy - The assembly that may have locations tagged for arrows.
        arrow_scale_factor - Allows arrows to be scaled up and down so that they match the size of the view

    Returns:
        The same assembly with the arrows added at the proper location
    """

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
                arrow.faces(">Z")
                .workplane(centerOption="CenterOfBoundBox")
                .circle(head_circle)
                .extrude(head_length)
            )

            # Figure out the angle between the normal vector of the face and the length axis of the arrow
            face_normal = face[1].normalAt(cq.Vector(0, 0, 0))
            rotation_angle = face_normal.wrapped.AngleWithRef(
                cq.Vector(0, 0, 1).wrapped, cq.Vector(-1, -1, -1).wrapped
            )
            rotation_angle = degrees(rotation_angle)

            # Rotate the arrow around its tip so that it will be in the correct position
            arrow = arrow.rotate((-10, 0, 0), (10, 0, 0), rotation_angle)

            # This holds the object-arrow subassembly that is created
            sub_assy = cq.Assembly()

            # Make the original child and the sub-assembly one entity
            sub_assy.add(
                child,
                name=child.name,
                loc=child.loc,
                color=child.color,
                metadata=child.metadata,
            )

            # Make the assembly arrow part of the assembly
            sub_assy.add(
                arrow,
                name="arrow_" + str(i),
                loc=child.loc * face_loc,
                color=cq.Color(0.0, 0.0, 0.0, 1.0),
                metadata=child.metadata,
            )

            # Replace the previous single child with the child plus the arrow
            assy.children[i] = sub_assy._copy()
        except Exception as err:
            pass

    return assy


def add_assembly_lines(assy, line_diameter=0.5, line_length=None):
    """
    Adds 3D lines (cylinders) to the assembly at the locations of faces tagged with "assembly_line".
    The lines will utilize the explode_loc distance to determine the length of the line.
    Example: `my_object.faces(">Y").tag("assembly_line")`

    Parameters:
        assy - The assembly that may have locations tagged for assembly lines.
        line_diameter - Allows lines to be scaled up and down so that they match the size of the view
        line_length - ALlows the length of the assembly line to be specified rather than relying on automated methods

    Returns:
        The same assembly with the line added at the proper location
    """

    # Search each assembly part for a face tagged "assembly_line"
    for i, child in enumerate(assy.children):
        # Get the face location so that we can offset the line properly
        try:
            face = child._query(child.name + "?assembly_line")
        except:
            continue
        face_center = face[1].Center()
        face_loc = cq.Location((face_center.x, face_center.y, face_center.z))

        # Figure out the correct line length
        if line_length is None:
            # Get the explode translation tuple
            explode_translation = (
                child.metadata["explode_loc"]
                if "explode_loc" in child.metadata.keys()
                else child.metadata["explode_translation"]
            )
            explode_translation = explode_translation.toTuple()[0]

            # Allow the user to set a custom line length
            if "assembly_line_length" in child.metadata.keys():
                line_length_tuple = child.metadata["assembly_line_length"]
                line_length = sqrt(sum([i ** 2 for i in line_length_tuple]))
            else:
                # Calculate the length of the assembly line based on the amount of translation
                line_length = sqrt(sum([i ** 2 for i in explode_translation]))

        # Create the line object
        line = cq.Workplane(child.obj.workplaneFromTagged("assembly_line").plane)
        line.zDir = face[1].normalAt(cq.Vector(0, 0, 0))
        line = (
            line.workplane(invert=True).circle(line_diameter / 2.0).extrude(line_length)
        )

        # This holds the object-line subassembly that is created
        sub_assy = cq.Assembly()

        # Make the original child and the sub-assembly one entity
        sub_assy.add(
            child,
            name=child.name,
            loc=child.loc,
            color=child.color,
            metadata=child.metadata,
        )

        # Make the assembly line part of the assembly
        new_meta = child.metadata.copy()
        new_meta["edge_color"] = cq.Color(1.0, 0.0, 0.0, 1.0)
        new_meta[
            "edge_width"
        ] = 3  # Anything less than 3 will cause the custom color to be ignored
        sub_assy.add(
            line,
            name="assembly_line_" + str(i),
            loc=child.loc,
            color=cq.Color(1.0, 0.0, 0.0, 1.0),
            metadata=new_meta,
        )

        # Replace the previous single child with the child plus the line
        assy.children[i] = sub_assy._copy()
