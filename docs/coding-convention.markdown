#RuuXee Project Coding Convention

This is a coding convention standard for RuuXee Project.

# Files
## File Name
Following Python conventions, all file names are named in all-lower
ASCII characters. A long file name with full spelling is recommended,
but a short file name is also allowed if it's clear enough.

When writing long file names, it's recommended to use '-' as delimiters.
However, it comes with one exception: Please do not use '-' in Python
script files, because it does not meet Python syntax.

For example:

  README.md # Bad
  readme.md # Good
  codeconv.markdown # That's fine but the one below is better:
  coding-convention.markdown # Good
  server.py # Good
  server-roles.py # Bad. Invalid syntax.

##File formats

RuuXee project uses the following file formats during development:

* .py: Python scripts.
* .pyc: Pre-complied Python modules.
* .markdown: Documentation written in Markdown format.

RuuXee uses [Markdown](http://daringfireball.net/projects/markdown/syntax)
as main documentation format.

NOTE: Althogh a lot of projects use .md to indicate Markdown format,
it's not recommended to use it here bacause it conflicts with Modula2
source code. Some editors do not recognize it well.

#Python Coding Convention
All Python code follows naming convention from Python's standard coding
guide. See [PEP8](https://www.python.org/dev/peps/pep-0008/)

#HTML Coding Convention
TBD

#CSS Coding Convention
TBD
