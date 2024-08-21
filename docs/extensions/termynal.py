import importlib

from docutils import nodes
from docutils.parsers.rst.directives import flag
from sphinx.util.docutils import SphinxDirective


class TermynalDirective(SphinxDirective):
    # Define the options (keyword arguments) this directive will accept
    option_spec = {"input": str, "progress": flag, "output": str}

    def run(self):  # type: ignore
        input_ = self.options.get("input", "")
        progress = "progress" in self.options
        output = self.options.get("output", "")

        # Build the Termynal HTML content
        content = '<div class="termy" data-ty-lineDelay="300"  data-termynal>\n'
        content += f'  <span data-ty="input">{input_}</span>\n'
        if progress:
            content += '  <span data-ty="progress"></span>\n'
        content += f"  <span data-ty>{output}</span>\n"
        content += "</div>\n"
        raw_html_node = nodes.raw("", content, format="html")
        return [raw_html_node]


class Example2TermynalDirective(SphinxDirective):
    required_arguments = 2

    def run(self):
        base_command = self.arguments[0]
        parameters_module = self.arguments[1]

        # Import the parameters from the specified module
        module = importlib.import_module(parameters_module)
        parameters = getattr(module, "parameters")

        # Build the Termynal HTML content
        termynal_content = (
            '<div class="termy" data-ty-lineDelay="300"  data-termynal>\n'
        )
        for input_data, output_data in parameters:
            input_str = " ".join(input_data)
            termynal_content += (
                f'  <span data-ty="input"> python {base_command} {input_str}</span>\n'
            )
            termynal_content += f"  <span data-ty>{output_data}</span>\n"
        termynal_content += "</div>\n"

        raw_html_node = nodes.raw("", termynal_content, format="html")

        return [raw_html_node]


def setup(app):  # type: ignore
    app.add_directive("example2termynal", Example2TermynalDirective)  # type: ignore
    app.add_directive("termynal", TermynalDirective)  # type: ignore
    app.add_css_file("termynal.css")  # type: ignore
    app.add_js_file("termynal.js", loading_method="defer")  # type: ignore
