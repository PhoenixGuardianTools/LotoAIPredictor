from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QMessageBox, QLabel
from core.feedback_uploader import send_feedback

class FeedbackTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("💬 Envoyer un message à l'équipe"))

        self.subject = QLineEdit()
        self.subject.setPlaceholderText("Sujet")
        layout.addWidget(self.subject)

        self.message = QTextEdit()
        self.message.setPlaceholderText("Votre message...")
        layout.addWidget(self.message)

        send_btn = QPushButton("Envoyer")
        send_btn.clicked.connect(self.send)
        layout.addWidget(send_btn)

        self.setLayout(layout)

    def send(self):
        subject = self.subject.text()
        msg = self.message.toPlainText()
        if not msg:
            QMessageBox.warning(self, "Erreur", "Message vide.")
            return
        send_feedback(msg, subject)
        QMessageBox.information(self, "Envoyé", "Message transmis.")
        self.subject.clear()
        self.message.clear()
