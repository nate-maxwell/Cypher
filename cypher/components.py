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
    def __init__(self, path: Path):
        super().__init__()
        self.file_path = path

        self.setTabStopDistance(QtGui.QFontMetricsF(self.font()).horizontalAdvance(' ') * 4)

        self.line_number_area = LineNumberArea(self)
        self.create_connections()
        self.update_line_number_area_width(0)

    def create_connections(self):
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

        painter.fillRect(event.rect(), QtCore.Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(QtCore.Qt.black)
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


class EditorTabWidget(QtWidgets.QTabWidget):
    """
    A tab handler for CodeEditor() tabs.
    Includes new tab functionality.

    Largely built following https://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
    """
    def __init__(self):
        super().__init__()

        self.tabs = list()
        self.tab_highlighters = list()
        self.current_index = 0
        self.old_index = 0

    def insert_tab(self, index: int, path: Path, command: str = ''):
        """
        Inserts a tab at the given index named after the given label.
        Can be given a command if loading text from a file.

        Args:
            index: The index to add the tab at.

            path: The path to the file to create the tab from.

            command: Any pre-written python code to add.
        """
        tab = CodeEditor(path)
        tab.setPlainText(command)
        highlight = cypher.languages.python_syntax.PythonHighlighter(tab.document())

        self.insertTab(index, tab, path.name)
        self.tab_highlighters.append(highlight)
        self.tabs.append(tab)

        self.setCurrentIndex(index)


class FolderTree(QtWidgets.QTreeWidget):
    """A tree of files/folders for project navigation."""
    def __init__(self, parent):
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
