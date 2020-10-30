# Bash Curly

This is a demo project that generates strings based on template expressions of the form
`a{x,y}b`

The comma-separated expressions in the curly brackets are treated as alternatives, so the expression above generates two strings: `axb` and `ayb`.

Curly brackets can be nested arbitrarily deep:
`a{b{c,{d,e}f},g}h`
generates
`abch`
`abdfh`
`abefh`
`agh`
# Usage
Clone the repo and simply run `python .` in the repo directory.
Enter bash-curly template and press enter to see the generated outputs.
Press Ctrl+C or Ctrl+Z, Enter to end the program.