# type: ignore
import importlib

from docutils import nodes
from sphinx.util.docutils import SphinxDirective


class ParametersCodeBlockDirective(SphinxDirective):
    required_arguments = (
        2  # Expecting two arguments: base command and parameters module
    )

    def run(self):
        base_command = self.arguments[0]
        parameters_module = self.arguments[1]

        # Import the parameters from the specified module
        module = importlib.import_module(parameters_module)
        parameters = getattr(module, "parameters")

        rst_content = ""
        for input_data, output_data in parameters:
            input_str = " ".join(input_data)
            rst_content += f"$ {base_command} {input_str}\n"
            rst_content += f"{output_data}\n\n"

        # Create a literal block node with the 'bash' language
        code_block_node = nodes.literal_block(rst_content, rst_content)
        code_block_node["language"] = "console"

        return [code_block_node]


def setup(app):
    app.add_directive("example_shell_block", ParametersCodeBlockDirective)
