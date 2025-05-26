import tkinter as tk

class ResultsTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="📅 Derniers résultats des tirages").pack(anchor="w", padx=5, pady=5)

        self.results_view = tk.Text(self, height=15, wrap="word")
        self.results_view.config(state="disabled")
        self.results_view.pack(fill="both", expand=True, padx=5, pady=5)

        self.load_results()

    def load_results(self):
        # Suppression de l'import problématique
        # results = get_draw_results()
        text = "\n".join(results)
        self.results_view.config(state="normal")
        self.results_view.delete("1.0", "end")
        self.results_view.insert("1.0", text)
        self.results_view.config(state="disabled")
