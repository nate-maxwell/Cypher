"""
# Cypher Main Window

* Update History

    `2024-01-10` - Init.
"""

import sys
import contextlib
from io import StringIO

from PySide2 import QtWidgets
from PySide2 import QtCore

import cypher
import cypher.languages.python_syntax
from cypher.components import CodeEditor


class CypherIDE(QtWidgets.QMainWindow):
    def __init__(self):
        super(CypherIDE, self).__init__()

        self.setWindowTitle('Cypher Editor')
        self.resize(1024, 768)
        cypher.set_qss(self)

        self.tabs = list()
        self.tab_highlighters = list()
        self.current_index = 0
        self.old_index = 0

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.widget_main = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QVBoxLayout()

        # Action buttons
        self.hlayout_buttons = QtWidgets.QHBoxLayout()
        self.btn_run = QtWidgets.QPushButton('Run')

        # Tab manager
        self.tab_manager = QtWidgets.QTabWidget()
        self.insert_tab(0, 'main', '')
        self.insert_tab(-1, '+', '')

        # Output browser
        self.output_widget = QtWidgets.QWidget()
        self.vlayout_output = QtWidgets.QVBoxLayout()
        self.lbl_output = QtWidgets.QLabel('Output')
        self.lbl_output.setAlignment(QtCore.Qt.AlignLeft)
        self.tb_output = QtWidgets.QTextBrowser()

        # Splitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

    def create_layout(self):
        self.setCentralWidget(self.widget_main)
        self.widget_main.setLayout(self.layout_main)

        # Action buttons
        self.hlayout_buttons.addStretch()
        self.hlayout_buttons.addWidget(self.btn_run)

        # Output
        self.output_widget.setLayout(self.vlayout_output)
        self.vlayout_output.addWidget(self.lbl_output)
        self.vlayout_output.addWidget(self.tb_output)

        # Splitter
        self.splitter.addWidget(self.tab_manager)
        self.splitter.addWidget(self.output_widget)

        # Main
        self.layout_main.addLayout(self.hlayout_buttons)
        self.layout_main.addWidget(self.splitter)

    def create_connections(self):
        self.btn_run.clicked.connect(self.run_code)
        self.tab_manager.currentChanged.connect(self.new_tab_connection)

    def insert_tab(self, index: int, label: str, command: str = ''):
        tab = CodeEditor()
        tab.setPlainText(command)
        highlight = cypher.languages.python_syntax.PythonHighlighter(tab.document())

        self.tab_manager.insertTab(index, tab, label)
        self.tab_highlighters.append(highlight)
        self.tabs.append(tab)

        self.tab_manager.setCurrentIndex(index)

    def new_tab_connection(self, index: int):
        if index == self.tab_manager.count() - 1:
            name, ok = QtWidgets.QInputDialog.getText(self, 'New Tab', 'Name')
            if ok:
                self.insert_tab(index, name, '')
                self.old_index = self.current_index
                self.current_index = index
            else:
                self.tab_manager.setCurrentIndex(self.old_index)
        else:
            self.old_index = index
            self.current_index = index

    def run_code(self):
        """
        Runs the code typed in the self.te_text_editor by redirecting
        the stdout value to the self.te_output widget.
        """
        code = self.tab_manager.currentWidget().toPlainText()
        output_stream = StringIO()

        with contextlib.redirect_stdout(output_stream):
            try:
                exec(code)
            except Exception as e:
                print(e)

        output = output_stream.getvalue()
        self.tb_output.setPlainText(output)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CypherIDE()
    window.show()
    sys.exit(app.exec_())
