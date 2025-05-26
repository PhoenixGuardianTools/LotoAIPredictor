from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from core.database import get_draw_results

class ResultsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📅 Derniers résultats des tirages"))

        self.results_view = QTextEdit()
        self.results_view.setReadOnly(True)
        layout.addWidget(self.results_view)

        self.setLayout(layout)
        self.load_results()

    def load_results(self):
        results = get_draw_results()
        text = "\n".join(results)
        self.results_view.setText(text)
