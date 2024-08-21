# type: ignore
import importlib

from docutils import nodes
from sphinx.util.docutils import SphinxDirective


class TermynalDirective(SphinxDirective):
    required_arguments = 2
    instance_count = 0

    def run(self):
        TermynalDirective.instance_count += 1  # Increment the instance counter
        unique_id = f"example2termynal{TermynalDirective.instance_count}"
        base_command = self.arguments[0]
        parameters_module = self.arguments[1]

        # Import the parameters from the specified module
        module = importlib.import_module(parameters_module)
        parameters = getattr(module, "parameters")

        # Build the Termynal HTML content
        termynal_content = (
            f'<div id="{unique_id}" data-ty-lineDelay="300"  data-termynal>\n'
        )
        for input_data, output_data in parameters:
            input_str = " ".join(input_data)
            termynal_content += (
                f'  <span data-ty="input">{base_command} {input_str}</span>\n'
            )
            termynal_content += f"  <span data-ty>{output_data}</span>\n"
        termynal_content += "</div>\n"

        raw_html_node = nodes.raw("", termynal_content, format="html")

        # Add the script tag with the unique ID for initialization
        script_node = nodes.raw(
            "",
            f'<script src="_static/termynal.js" data-termynal-container="#{unique_id}"></script>',
            format="html",
        )

        return [raw_html_node, script_node]


def setup(app):
    app.add_directive("example2termynal", TermynalDirective)
    app.add_css_file("termynal.css")
