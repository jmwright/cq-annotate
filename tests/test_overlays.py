import pytest
import cadquery as cq
from cq_annotate.overlays import add_safety_warning


def test_add_safety_waring():
    # Set up the location of the test SVG and the text to be added
    text = "Safety Warning"
    svg_path = "tests/test_add_safety_waring.svg"

    # The SVG export options
    export_options = {
        "width": 800,
        "height": 600,
        "marginLeft": 30,
        "marginTop": 30,
        "showAxes": False,
        "projectionDir": (1.0, 1.0, 1.0),
        "strokeWidth": 0.2,
        "strokeColor": (1.0, 1.0, 1.0),
        # "hiddenColor": (0.1, 0.1, 0.1),
        "showHidden": False,
        "fitView": True,
    }

    # Create the test SVG
    box1 = cq.Workplane().box(10, 10, 10)
    cq.exporters.export(box1, svg_path, opt=export_options)

    # Add the safety warning to the SVG
    add_safety_warning(svg_path, text, use_icon=True)
