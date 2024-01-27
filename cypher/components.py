"""
# Cypher UI Component Classes

* Update History

    `2024-01-06` - Init.
"""


from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore


class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, code_editor):
        super().__init__(code_editor)
        self.editor = code_editor

    def sizeHint(self):
        return QtCore.QSize(self.editor.line_number_area_width, 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QtWidgets.QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setTabStopDistance(QtGui.QFontMetricsF(self.font()).horizontalAdvance(' ') * 4)

        self.line_number_area = LineNumberArea(self)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.update_line_number_area_width(0)

    def create_widgets(self):
        # Main
        pass

    def create_layout(self):
        # Main
        pass

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
        space = 3 + self.fontMetrics().width('9') * digits
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
                painter.drawText(0, top, self.line_number_area.width(), height, QtCore.Qt.AlignRight, number)

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
            # selection.format.setProperty(selection.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)
