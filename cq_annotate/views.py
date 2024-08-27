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
        # Make sure there is an explode location provided
        if "explode_loc" in child.metadata:
            child.loc = child.loc * child.metadata["explode_loc"]

        # Also accomodate the "explode_translation" metadata key
        if "explode_translation" in child.metadata:
            child.loc = child.loc * child.metadata["explode_translation"]

        # Handle assembly arrows being bundled with objects
        for sub_child in child.children:
            # Make sure there is an explode location provided
            if "explode_loc" in sub_child.metadata:
                sub_child.loc = sub_child.loc * sub_child.metadata["explode_loc"]

            # Also accomodate the "explode_translation" metadata key
            if "explode_translation" in sub_child.metadata:
                sub_child.loc = (
                    sub_child.loc * sub_child.metadata["explode_translation"]
                )
