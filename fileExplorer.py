from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeView, QFileSystemModel, QSplitter
from PyQt5.QtCore import Qt, QModelIndex

class FileExplorer(QWidget):
    def __init__(self, directory):
        super().__init__()
        self.setStyleSheet("""
            QTreeView {
                background-color: #002b36;
                color: #839496;
            }
            QTreeView::item {
                height: 30px;
            }
            QTreeView::item:selected {
                background-color: #073642;
                color: #fff;
            }
        """)

        self.layout = QVBoxLayout(self)

        self.model = QFileSystemModel()
        self.model.setRootPath(directory)
        self.model.setFilter(Qt.QDir.NoDotAndDotDot | Qt.QDir.AllDirs | Qt.QDir.Files)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(directory))
        self.tree.setHeaderHidden(True)

        self.tree.setStyleSheet("""
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings  {
                border-image: none;
                image: url(assets/icons/folder.png);
            }
            QTreeView::branch:closed:has-children:!has-siblings,
            QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(assets/icons/folder.png);
            }
        """)

        self.layout.addWidget(self.tree)
        self.setLayout(self.layout)
        self.directory = directory
        self.toggle_explorer = True

    def toggle_visibility(self):
        self.setVisible(self.toggle_explorer)
        self.toggle_explorer = not self.toggle_explorer
