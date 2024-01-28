# Cypher utils


from pathlib import Path

from PySide2 import QtWidgets


def set_stylesheet(tool: QtWidgets.QWidget, qss_file: str = 'darkorange.css'):
    qss_input_name = Path(qss_file)
    qss_file_name = f'{qss_input_name.stem}.css'
    qss_path = Path(Path(__file__).parent, 'resources', qss_file_name)

    with open(qss_path, 'r') as f:
        stylesheet = f.read()
        tool.setStyleSheet(stylesheet)
