# Cypher Python Editor  ![Static Badge](https://img.shields.io/badge/GitHub-grey?logo=github)
Cypher text editor for writing python code.


## About the project

<img src="https://i.imgur.com/fLflCU6.png" alt="ui"/>

A fun project I work on occasionally in my spare time, originally created for me to
explore new things about PySide2 and Qt5.

For now, it is a simple text editor that has only a few simple features added,
and can only execute one tab's code at a time, allowing only for importing built-in
modules.

The goal is to eventually add a lexer and some intellisense to the project, and
allowing for full project development.


## Getting Started

### Prerequisites

The tool needs the following library to be installed:

-[PySide2](https://pypi.org/project/PySide2/)

### Install as module

You can install the module from the repo with:
```bash
pip install git+https://github.com/nate-maxwell/Cypher
```

### Starting the editor

You can start the editor with the follow:
```bash
import cypher.editor

cypher.editor.main()
```


## Features

- [x] Python code execution
- [x] Save and load python files
- [x] Open project directories
- [x] Code syntax highlighting
- [ ] Create new files from editor
- [ ] Code execution with dependencies from other files
- [ ] Code editor short-cut support


## Disclaimer

This tool is still in development and updated sporadically.