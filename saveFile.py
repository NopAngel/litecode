from PyQt5.QtWidgets import QFileDialog

def save_file(editor):
    if hasattr(editor, 'currentFilePath'):
        with open(editor.currentFilePath, 'w', encoding='utf-8') as file:
            file.write(editor.toPlainText())
        print(f"File saved: {editor.currentFilePath}")
    else:
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(editor, "Save File", "", "All Files (*);;Python Files (*.py);;C Files (*.c)", options=options)
        if filePath:
            with open(filePath, 'w', encoding='utf-8') as file:
                file.write(editor.toPlainText())
            editor.currentFilePath = filePath
            print(f"File saved: {filePath}")
