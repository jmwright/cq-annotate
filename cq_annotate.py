from math import degrees
import cadquery as cq


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
                arrow.faces(">Z").workplane().circle(head_circle).extrude(head_length)
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
            assy.add(
                arrow,
                name="arrow_" + str(i),
                loc=child.loc * face_loc,
                color=cq.Color(0.0, 0.0, 0.0, 1.0),
            )
        except Exception:
            pass

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
