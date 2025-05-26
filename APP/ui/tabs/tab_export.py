from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from core.exporter import export_to_excel

class ExportTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("📤 Export des données"))
        export_btn = QPushButton("Exporter vers Excel")
        export_btn.clicked.connect(export_to_excel)
        layout.addWidget(export_btn)

        self.setLayout(layout)
