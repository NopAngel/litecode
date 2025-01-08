from PyQt5.QtWidgets import QFileDialog

def open_file(editor):
    options = QFileDialog.Options()
    filePath, _ = QFileDialog.getOpenFileName(editor, "Open File", "", "All Files (*);;Python Files (*.py);;C Files (*.c)", options=options)
    if filePath:
        with open(filePath, 'r') as file:
            editor.setPlainText(file.read())
        editor.currentFilePath = filePath
        print(f"File opened: {filePath}")
