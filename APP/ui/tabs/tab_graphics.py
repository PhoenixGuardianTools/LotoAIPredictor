from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from core.database import get_all_draws
import pandas as pd

class GraphicsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("📈 Évolution de vos gains nets par période")
        layout.addWidget(label)

        # Graphique
        self.canvas = FigureCanvas(Figure(figsize=(10, 4)))
        layout.addWidget(self.canvas)
        self.plot()

    def plot(self):
        df = pd.DataFrame(get_all_draws(), columns=["date", "game", "prediction", "actual", "gain", "cost", "net"])
        if df.empty:
            return

        df["date"] = pd.to_datetime(df["date"])
        df.sort_values("date", inplace=True)

        ax = self.canvas.figure.add_subplot(111)
        ax.clear()

        for game in df["game"].unique():
            data = df[df["game"] == game]
            ax.plot(data["date"], data["net"].cumsum(), label=game.capitalize())

        ax.set_title("Gains nets cumulés")
        ax.set_xlabel("Date")
        ax.set_ylabel("Gain net (€)")
        ax.legend()
        self.canvas.draw()
