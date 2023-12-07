import os
import svgutils.transform as sg
from svgutils.compose import Unit


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
