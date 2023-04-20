import shortcodes

import util


@shortcodes.register("syllabus")
def syllabus(pargs, kwargs, node):
    """Display syllabus."""
    syllabi = util.get_config("syllabus")
    result = ["<ul>"]
    for (slug, title, syllabus) in syllabi:
        result.append(f'<li><a href="@root/{slug}" markdown="1">{title}</a>')
        if syllabus:
            result.append("<ul>")
            for item in syllabus:
                result.append(f'<li markdown="1">{item}</li>')
            result.append("</ul>")
        result.append("</li>")
    result.append("</ul>")
    result = "\n".join(result)
    return result
