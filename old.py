import sys
import os
from PyQt5.QtWidgets import QApplication, QPlainTextEdit, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QDialog, QLabel, QListView, QSplitter, QMenu, QFileDialog
from PyQt5.QtGui import QColor, QFont, QPainter, QTextFormat, QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt, QRect, QSize

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        font = QFont()
        font.setFamily("assets/fonts/font.ttf")
        font.setPointSize(12)
        self.setFont(font)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #002b36;
                color: #839496;
                selection-background-color: #073642;
                border: none;
            }
            QScrollBar:vertical {
                background: #002b36;
                width: 10px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #586e75;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.highlighter = None
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)

        self.lineNumberArea = LineNumberArea(self)
        self.updateLineNumberAreaWidth()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth()

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            lineColor = QColor("#073642")
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_K:
            open_folder(self)
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_O:
            open_file(self)
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            save_file(self)
        else:
            super().keyPressEvent(event)
            self.highlightCurrentLine()

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#002b36"))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor("#586e75"))
                painter.drawText(0, top, self.lineNumberArea.width() - 5, self.fontMetrics().height(), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def setHighlighter(self, highlighter):
        self.highlighter = highlighter
        self.highlighter.setDocument(self.document())

class LanguageDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Language")
        self.setStyleSheet("""
            QDialog {
                background-color: #002b36;
            }
            QLabel {
                color: #839496;
            }
            QComboBox {
                background-color: #073642;
                color: #839496;
            }
            QPushButton {
                background-color: #586e75;
                color: #002b36;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #839496;
            }
        """)

        layout = QVBoxLayout()
        label = QLabel("Choose your language:")
        self.comboBox = QComboBox()
        languages = ["Python", "Lua", "C", "C++", "Bash", "Database (Oracle or PostgreSQL)", "Pascal", "React", "JSON", "CSV", "Astro.js"]
        self.comboBox.addItems(languages)
        button = QPushButton("Select")
        button.clicked.connect(self.accept)

        layout.addWidget(label)
        layout.addWidget(self.comboBox)
        layout.addWidget(button)
        self.setLayout(layout)

    def getSelectedLanguage(self):
        return self.comboBox.currentText()

class FileExplorer(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        
        layout = QVBoxLayout()
        
        self.listView = QListView()
        self.listView.setStyleSheet("""
            QListView {
                background-color: #001f26;
                color: #839496;
                border: none;
                padding: 5px;
            }
            QListView::item:selected {
                background-color: #073642;
                color: #839496;
            }
        """)
        
        self.model = QStandardItemModel()
        self.listView.setModel(self.model)
        
        self.listView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listView.customContextMenuRequested.connect(self.showContextMenu)
        self.listView.doubleClicked.connect(self.handleDoubleClick)

        self.current_folder_path = None
        self.folder_history = []

        openButton = QPushButton("Open Folder")
        openButton.setStyleSheet("background-color: #002b36; color: #839496; border: none; padding: 5px 10px; border-radius: 4px;")
        openButton.clicked.connect(self.open_folder)

        backButton = QPushButton("Back")
        backButton.setStyleSheet("background-color: #002b36; color: #839496; border: none; padding: 5px 10px; border-radius: 4px;")
        backButton.clicked.connect(self.go_back)
        
        layout.addWidget(self.listView)
        layout.addWidget(openButton)
        layout.addWidget(backButton)
        self.setLayout(layout)

    def handleDoubleClick(self, index):
        item = self.model.itemFromIndex(index)
        item_path = os.path.join(self.current_folder_path, item.text())
        if os.path.isdir(item_path):
            self.open_folder_with_item(item)
        elif os.path.isfile(item_path):
            self.open_file(item_path)

    def showContextMenu(self, position):
        indexes = self.listView.selectedIndexes()
        if indexes:
            index = indexes[0]
            item = self.model.itemFromIndex(index)
            menu = QMenu()
            openAction = menu.addAction("Open")
            action = menu.exec_(self.listView.viewport().mapToGlobal(position))

            if action == openAction and os.path.isdir(os.path.join(self.current_folder_path, item.text())):
                self.open_folder_with_item(item)

    def open_folder_with_item(self, item):
        folder_icon = QIcon("assets/icons/folders-open.png")
        item.setIcon(folder_icon)
        folder_path = os.path.join(self.current_folder_path, item.text())
        self.folder_history.append(self.current_folder_path)
        self.current_folder_path = folder_path
        self.populate_model(folder_path)

    def open_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            self.editor.setPlainText(content)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_history = []
            self.current_folder_path = folder_path
            self.populate_model(folder_path)

    def go_back(self):
        if self.folder_history:
            self.current_folder_path = self.folder_history.pop()
            self.populate_model(self.current_folder_path)

    def populate_model(self, folder_path):
        self.model.clear()
        folder_icon = QIcon("assets/icons/folder.png")
        file_icon = QIcon("assets/icons/file.png")

        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            icon = folder_icon if os.path.isdir(item_path) else file_icon
            standard_item = QStandardItem(icon, item)
            self.model.appendRow(standard_item)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.editor = CodeEditor()
        
        self.fileExplorer = FileExplorer(self.editor)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.fileExplorer)
        self.splitter.addWidget(self.editor)
        self.splitter.setSizes([200, 600])

        footer = QWidget()
        footerLayout = QHBoxLayout()
        footerLayout.addStretch()
        selectLanguageButton = QPushButton("Select Language")
        selectLanguageButton.setStyleSheet("background-color: #002026; color: #fff; border: none; padding: 5px 10px; border-radius: 4px;")
        selectLanguageButton.clicked.connect(self.showLanguageDialog)
        footerLayout.addWidget(selectLanguageButton)
        footer.setLayout(footerLayout)
        footer.setMaximumHeight(60)
        footer.setStyleSheet("background-color: #001f26; border: none;")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.splitter)
        mainLayout.addWidget(footer)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        container = QWidget()
        container.setLayout(mainLayout)
        container.setStyleSheet("background-color: #002b36; border: none;")
        self.setCentralWidget(container)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Editor de Código - Solarized Dark")

        self.editor.highlightCurrentLine()
        self.editor.updateLineNumberAreaWidth()
        
    def showLanguageDialog(self):
        dialog = LanguageDialog()

        if dialog.exec_() == QDialog.Accepted:
            selectedLanguage = dialog.getSelectedLanguage()
            highlighter = getHighlighter(selectedLanguage)  # Ensure you have this function defined
            self.editor.setHighlighter(highlighter)
            self.setWindowTitle(f"Editor de Código - {selectedLanguage}")
            print(f"Selected language: {selectedLanguage}")

app = QApplication(sys.argv)
window = MainWindow()  # Corrected this line
window.show()
sys.exit(app.exec_())
