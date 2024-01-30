"""
# Cypher UI Component Classes

* Update History

    `2024-01-27` - Init.
"""


import os
from pathlib import Path

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

import cypher.languages.python_syntax
import cypher.languages.json_syntax


class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, code_editor):
        super().__init__(code_editor)
        self.editor = code_editor

    def sizeHint(self):
        return QtCore.QSize(self.editor.line_number_area_width, 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QtWidgets.QPlainTextEdit):
    """
    A code editing QPlainTextEdit. This is used for highlighting syntax
    of code written within the text field.

    A line number widget is built into the side to tell you the current
    line number.
    """
    indented = QtCore.Signal(range)
    unindented = QtCore.Signal(range)

    def __init__(self, path: Path):
        super(CodeEditor, self).__init__()
        self.file_path = path

        self.setTabStopDistance(QtGui.QFontMetricsF(self.font()).horizontalAdvance(' ') * 4)

        self.line_number_area = LineNumberArea(self)
        self._create_shortcut_signals()
        self._create_connections()
        self.update_line_number_area_width(0)

    def _create_shortcut_signals(self):
        self.indented.connect(self.indent)
        self.unindented.connect(self.unindent)

    def _create_connections(self):
        self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'), self.update_line_number_area_width)
        self.connect(self, QtCore.SIGNAL('updateRequest(QRect,int)'), self.update_line_number_area)
        self.connect(self, QtCore.SIGNAL('cursorPositionChanged()'), self.highlight_current_line)

    @property
    def line_number_area_width(self) -> int:
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 20 + self.fontMetrics().width('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width, 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.line_number_area_width, cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QtGui.QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QtGui.QColor(21, 21, 21))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(QtCore.Qt.lightGray)
                painter.drawText(0, top, self.line_number_area.width(), height, QtCore.Qt.AlignLeft, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def highlight_current_line(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()

            lineColor = QtGui.QColor(QtCore.Qt.yellow).lighter(160)

            selection.format.setBackground(lineColor)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def add_line_prefix(self, prefix: str, line: int):
        """
        Adds the prefix substring to the start of a line.

        Args:
            prefix: The substring to append to the start of the line.
            line: The line number to append.
        """
        cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(line))
        self.setTextCursor(cursor)
        self.textCursor().insertText(prefix)

    def remove_line_prefix(self, prefix: str, line: int):
        """
        Removes the prefix substring from the start of a line.

        Args:
            prefix: The substring to remove from the start of the line.
            line: The line number to adjust.
        """
        cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(line))
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        text = cursor.selectedText()
        if text.startswith(prefix):
            cursor.removeSelectedText()
            cursor.insertText(text.split(prefix, 1)[-1])

    def _get_selection_range(self) -> tuple[int, int]:
        """
        Returns the first and last line of a continuous selection.

        Returns
            tuple[int, int]: First line number and last line number.
        """
        if not self.textCursor().hasSelection():
            return 0, 0

        cursor = self.textCursor()
        start_pos = cursor.selectionStart()
        end_pos = cursor.selectionEnd()

        cursor.setPosition(start_pos)
        first_line = cursor.blockNumber()
        cursor.setPosition(end_pos)
        last_line = cursor.blockNumber()

        return first_line, last_line

    def indent(self, lines: range):
        """Indent the lines within the given range."""
        for i in lines:
            self.add_line_prefix('\t', i)

    def unindent(self, lines: range):
        """Unindent the lines within the given range."""
        for i in lines:
            self.remove_line_prefix('\t', i)

    def keyPressEvent(self, e):
        """Enable shortcuts in keypress event."""
        first_line, last_line = self._get_selection_range()

        if e.key() == QtCore.Qt.Key_Tab and last_line - first_line:
            lines = range(first_line, last_line + 1)
            self.indented.emit(lines)
            return

        if e.key() == QtCore.Qt.Key_Backtab:
            lines = range(first_line, last_line + 1)
            self.unindented.emit(lines)
            return

        super(CodeEditor, self).keyPressEvent(e)


class EditorTabWidget(QtWidgets.QTabWidget):
    """
    A tab handler for CodeEditor() tabs.
    Includes new tab functionality.

    Largely built following https://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
    """
    def __init__(self):
        super().__init__()

        self.tabs: list[CodeEditor] = list()
        self.tab_paths: list[Path] = list()
        self.current_index = 0
        self.old_index = 0

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.remove_tab)

    def insert_code_tab(self, index: int, path: Path, command: str = ''):
        """
        Inserts a tab at the given index named after the given label.
        Can be given a command if loading text from a file.

        Args:
            index: The index to add the tab at.

            path: The path to the file to create the tab from.

            command: Any pre-written python code to add.
        """
        if path in self.tab_paths:
            self.setCurrentIndex(self.tab_paths.index(path))
            return

        tab = CodeEditor(path)
        tab.setPlainText(command)

        if path.suffix == '.py':
            cypher.languages.python_syntax.PythonHighlighter(tab.document())
        elif path.suffix == '.json':
            cypher.languages.json_syntax.JsonHighlighter(tab.document())

        self.insertTab(index, tab, path.name)
        self.tabs.insert(index, tab)
        self.tab_paths.insert(index, path)

        self.setCurrentIndex(index)

    def remove_tab(self, index: int):
        self.tab_paths.pop(index)
        self.tabs.pop(index)
        self.removeTab(index)

    def save_files(self):
        for i, p in enumerate(self.tab_paths):
            with open(p, 'w') as out_file:
                out_file.write(self.tabs[i].toPlainText())

    def close_all_tabs(self, save: bool = False):
        for i, p in enumerate(self.tab_paths):
            if save:
                with open(p, 'w') as out_file:
                    out_file.write(self.tabs[i].toPlainText())
            self.remove_tab(i)


class FolderTree(QtWidgets.QTreeWidget):
    """A tree of files/folders for project navigation."""
    def __init__(self, parent: QtWidgets.QMainWindow):
        super().__init__()
        self.parent = parent
        self.root_path = Path()
        self.setHeaderLabel('Project')

        self.itemClicked.connect(self.clicked_connection)

    def refresh_tree(self, path: Path):
        """
        Redraws the tree from the given path.

        Args:
            path: Which folder to recursively populate the tree from.
        """
        self.clear()
        self.root_path = path
        invis_root_node = self.invisibleRootItem()
        if path.is_dir():
            root_label = path.name
        else:
            root_label = path.parent.name
        root_node = QtWidgets.QTreeWidgetItem(invis_root_node, [root_label])
        root_node.setExpanded(True)
        self._refresh_tree(path, root_node)

    def _refresh_tree(self, path: Path, tree: QtWidgets.QTreeWidgetItem):
        """
        Recursively create a tree of QTreeWidgetItems to add to the tree widget.

        Args:
            path: The current folder/file to create a node from.

            tree: The new parent to add children to.
        """
        for i in os.listdir(path.as_posix()):
            new_path = Path(path, i)
            parent_item = QtWidgets.QTreeWidgetItem(tree, [new_path.name])

            if new_path.is_dir():
                parent_item.setIcon(0, QtGui.QIcon('SP_DirIcon'))
                self._refresh_tree(new_path, parent_item)
            else:
                parent_item.setIcon(0, QtGui.QIcon('SP_FileIcon'))

    def clicked_connection(self, item, _):
        """When an item is clicked, tell the main window to create a tab from it."""
        rel_path = self._build_item_path(item, Path())
        full_path = Path(self.root_path, rel_path)
        self.parent.open_file_in_tab(full_path)

    def _build_item_path(self, item: QtWidgets.QTreeWidgetItem, cur_path: Path) -> Path:
        t_path = Path(item.text(0), cur_path)
        if item.parent():
            next_path = self._build_item_path(item.parent(), t_path)
            return next_path
        else:
            return cur_path
