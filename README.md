# cq-annotate

An annotation extension designed to work with the CadQuery parametric CAD API.

## Methods

* `add_assembly_arrows` - Automatically adds assembly arrows to faces in an assembly tagged "arrow". The arrow will face in the opposite direction of the normal of the face so that in something like an exploded assembly view the arrows should be indicating the direction to reassemble the assembly. The arrow size can be altered using the `arrow_scale_factor` parameter. More information can be found in the docstring for this method.
* `explode_assembly` - Creates an exploded view of an assembly by translating the parts of the assembly by the `explode_loc` value defined by the designer in the `metadata` parameter of each part. This requires more work on the part of the designer, but provides the proper level of control to ensure that exploded views look correct. More information can be found in the docstring for this method.

## Examples

* [add_assembly_arrows_example.py](./examples/add_assembly_arrows_example.py) - A fully commented example showing a simple example of how to use assembly arrows.
* [explode_assembly_example.py](./examples/explode_assembly_example.py) - A fully commented example showing how a simple assembly can be set up to explode to show the individual components better.
