from PyQt5.QtWidgets import QFileDialog

def open_folder(editor):
    options = QFileDialog.Options()
    options |= QFileDialog.ShowDirsOnly
    directory = QFileDialog.getExistingDirectory(editor, "Select Directory", "", options=options)
    if directory:
        print(f"Selected directory: {directory}")
