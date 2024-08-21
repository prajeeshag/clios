from docutils import nodes
from docutils.parsers.rst.directives import flag
from sphinx.util.docutils import SphinxDirective


class TermynalDirective(SphinxDirective):
    # Define the options (keyword arguments) this directive will accept
    option_spec = {"input": str, "progress": flag, "output": str}
    instance_count = 0

    def run(self):  # type: ignore
        TermynalDirective.instance_count += 1
        unique_id = f"example2termynal{TermynalDirective.instance_count}"
        input_ = self.options.get("input", "")
        progress = "progress" in self.options
        output = self.options.get("output", "")

        print(progress)

        # Build the Termynal HTML content
        content = f'<div id="{unique_id}" data-ty-lineDelay="300"  data-termynal>\n'
        content += f'  <span data-ty="input">{input_}</span>\n'
        if progress:
            content += '  <span data-ty="progress"></span>\n'
        content += f"  <span data-ty>{output}</span>\n"
        content += "</div>\n"
        raw_html_node = nodes.raw("", content, format="html")
        # Add the script tag with the unique ID for initialization
        script_node = nodes.raw(
            "",
            f'<script src="_static/termynal.js" data-termynal-container="#{unique_id}"></script>',
            format="html",
        )

        return [raw_html_node, script_node]


def setup(app):  # type: ignore
    app.add_directive("termynal", TermynalDirective)  # type: ignore
