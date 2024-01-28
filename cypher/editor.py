"""
# Cypher Main Window

* Update History

    `2024-01-27` - Init.
"""


import sys
import time
import contextlib
import webbrowser
from io import StringIO
from pathlib import Path

from PySide2 import QtWidgets
from PySide2 import QtCore

import cypher
from cypher.components import EditorTabWidget
from cypher.components import FolderTree


class CypherIDE(QtWidgets.QMainWindow):
    def __init__(self):
        super(CypherIDE, self).__init__()

        self.setWindowTitle('Cypher Editor')
        self.resize(1024, 768)
        cypher.set_qss(self)

        self._create_widgets()
        self._create_layout()
        self._create_menu_actions()
        self._create_menu_bar()
        self._create_connections()

    def _create_widgets(self):
        self.widget_main = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QVBoxLayout()

        # Action buttons
        self.hlayout_buttons = QtWidgets.QHBoxLayout()
        self.btn_run = QtWidgets.QPushButton('Run')

        # Tab manager
        self.tab_manager = EditorTabWidget()

        # File manager
        self.file_manager = FolderTree(self)
        self.file_manager.refresh_tree(Path(__file__).parent.parent)

        # Output browser
        self.output_widget = QtWidgets.QWidget()
        self.vlayout_output = QtWidgets.QVBoxLayout()
        self.lbl_output = QtWidgets.QLabel('Output')
        self.lbl_output.setAlignment(QtCore.Qt.AlignLeft)
        self.tb_output = QtWidgets.QTextBrowser()

        # Splitters
        self.code_output_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.file_editor_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

    def _create_layout(self):
        self.setCentralWidget(self.widget_main)
        self.widget_main.setLayout(self.layout_main)

        # Action buttons
        self.hlayout_buttons.addStretch()
        self.hlayout_buttons.addWidget(self.btn_run)

        # Output
        self.output_widget.setLayout(self.vlayout_output)
        self.vlayout_output.addWidget(self.lbl_output)
        self.vlayout_output.addWidget(self.tb_output)

        # Splitters
        self.code_output_splitter.addWidget(self.tab_manager)
        self.code_output_splitter.addWidget(self.output_widget)
        self.code_output_splitter.setSizes(
            [self.code_output_splitter.size().height() * .7, self.code_output_splitter.size().height() * .3])
        self.file_editor_splitter.addWidget(self.file_manager)
        self.file_editor_splitter.addWidget(self.code_output_splitter)
        self.file_editor_splitter.setSizes(
            [self.file_editor_splitter.size().width() * .2, self.file_editor_splitter.size().width() * .8])

        # Main
        self.layout_main.addLayout(self.hlayout_buttons)
        self.layout_main.addWidget(self.file_editor_splitter)

    def _create_menu_actions(self):
        self.action_open_folder = QtWidgets.QAction('Open Folder', self)
        self.action_save_files = QtWidgets.QAction('Save Files', self)
        self.action_about = QtWidgets.QAction('About', self)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = QtWidgets.QMenu('File', self)
        menu_bar.addMenu(file_menu)
        file_menu.addAction(self.action_open_folder)
        file_menu.addAction(self.action_save_files)

        help_menu = QtWidgets.QMenu('Help', self)
        menu_bar.addMenu(help_menu)
        help_menu.addAction(self.action_about)

    def _create_connections(self):
        self.btn_run.clicked.connect(self.run_code)
        self.action_open_folder.triggered.connect(self.open_project)
        self.action_save_files.triggered.connect(self.save_files)
        self.action_about.triggered.connect(self.open_about)

    def open_file_in_tab(self, path: Path):
        """
        When the user clicks a file in the folder tree widget, read
        the contents of the file, then tell the tab manager to insert
        a new tab with the contents of the file as the displayed command.

        Args:
            path: Path to the file to open.
        """
        if path.is_file():
            try:
                with open(path.as_posix(), 'r') as f:
                    contents = f.read()
                    self.tab_manager.insert_tab(self.tab_manager.count(), path, contents)
            except FileNotFoundError:
                print('File not found or inaccessible.')

    def open_project(self):
        """
        Closes the current tabs and opens the selected folder. A dialog prompting the user
        if they would like to save open tabs will determine if tabs get saved or not.
        """
        path = Path(str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory')))

        if self.tab_manager.tab_paths:
            save = QtWidgets.QMessageBox.question(self, 'Save Existing', 'Would you like to save opened files?',
                                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            if save == QtWidgets.QMessageBox.Yes:
                self.tab_manager.close_all_tabs(True)
            else:
                self.tab_manager.close_all_tabs(False)

        self.tab_manager.close_all_tabs()
        self.file_manager.refresh_tree(path)

    def save_files(self):
        self.tab_manager.save_files()

    @staticmethod
    def open_about():
        webbrowser.open('https://github.com/nate-maxwell/Cypher')

    def run_code(self):
        """
        Runs the code typed in the self.te_text_editor by redirecting
        the stdout value to the self.te_output widget.
        """
        code = self.tab_manager.currentWidget().toPlainText()
        output_stream = StringIO()

        start = time.perf_counter()
        with contextlib.redirect_stdout(output_stream):
            try:
                exec(code)
            except Exception as e:
                print(e)

        output = output_stream.getvalue()
        end = time.perf_counter() - start
        output_text = f'Executed in {end} seconds:\n\n{output}'
        self.tb_output.setPlainText(output_text)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = CypherIDE()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
