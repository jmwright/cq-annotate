import cadquery as cq
from math import degrees


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
