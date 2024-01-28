"""
# JSon Syntax Highlighter

* Update History

    `2024-01-06` - Init.
"""


from PySide2 import QtCore
from PySide2 import QtGui


class HighlightRule(object):
    def __init__(self, pattern: str, char_format: QtGui.QTextCharFormat):
        self.pattern = pattern
        self.format = char_format


class JsonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None):
        """Initialize rules with expression pattern and text format."""
        super(JsonHighlighter, self).__init__(parent)

        self.rules = list()

        # numeric value
        char_format = QtGui.QTextCharFormat()
        char_format.setForeground(QtCore.Qt.blue)
        char_format.setFontWeight(QtGui.QFont.Bold)
        pattern = QtCore.QRegExp("([-0-9.]+)(?!([^\"]*\"[\\s]*\\:))")

        rule = HighlightRule(pattern, char_format)
        self.rules.append(rule)

        # key
        char_format = QtGui.QTextCharFormat()
        pattern = QtCore.QRegExp("(\"[^\"]*\")\\s*\\:")
        char_format.setFontWeight(QtGui.QFont.Bold)

        rule = HighlightRule(pattern, char_format)
        self.rules.append(rule)

        # value
        char_format = QtGui.QTextCharFormat()
        pattern = QtCore.QRegExp(":+(?:[: []*)(\"[^\"]*\")")
        char_format.setForeground(QtCore.Qt.darkGreen)

        rule = HighlightRule(pattern, char_format)
        self.rules.append(rule)

    def highlightBlock(self, text: str):
        """
        # Override
        Implementing virtual method of highlighting the text block

        Args:
            text(str): The text to perform a keyword highlighting check on.
        """
        for rule in self.rules:
            # create a regular expression from the retrieved pattern
            expression = QtCore.QRegExp(rule.pattern)

            # check what index that expression occurs at with the ENTIRE text
            index = expression.indexIn(text)
            while index >= 0:
                # get the length of how long the expression is
                # set format from the start to the length with the text format
                length = expression.matchedLength()
                self.setFormat(index, length, rule.format)

                # set index to where the expression ends in the text
                index = expression.indexIn(text, index + length)
