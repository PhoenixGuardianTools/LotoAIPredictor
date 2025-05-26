import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from core.database import get_all_draws
import pandas as pd

class GraphicsTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        label = tk.Label(self, text="📈 Évolution de vos gains nets par période")
        label.pack(anchor="w", padx=5, pady=5)

        # Graphique
        self.figure = Figure(figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        self.plot()

    def plot(self):
        df = pd.DataFrame(get_all_draws(), columns=["date", "game", "prediction", "actual", "gain", "cost", "net"])
        if df.empty:
            return

        df["date"] = pd.to_datetime(df["date"])
        df.sort_values("date", inplace=True)

        ax = self.figure.add_subplot(111)
        ax.clear()

        for game in df["game"].unique():
            data = df[df["game"] == game]
            ax.plot(data["date"], data["net"].cumsum(), label=game.capitalize())

        ax.set_title("Gains nets cumulés")
        ax.set_xlabel("Date")
        ax.set_ylabel("Gain net (€)")
        ax.legend()
        self.canvas.draw()
