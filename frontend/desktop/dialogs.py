import tkinter as tk
from PIL import Image, ImageTk

from backend.settings import DARK_COLOR, SAMPLE_MAZES


class SampleMazeDialog(tk.Toplevel):
    def __init__(self, master, on_select):
        super().__init__(master)
        self.on_select = on_select
        self.preview_images = []

        self.title("Choose a Maze")
        self.geometry("760x430")
        self.configure(bg=DARK_COLOR)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.grid_columnconfigure((0, 1), weight=1)

        tk.Label(self, text="Choose a sample maze", bg=DARK_COLOR, fg="white", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=(22, 8))
        tk.Label(self, text="Pick the maze style you want to solve.", bg=DARK_COLOR, fg="#cbd5e1", font=("Arial", 11)).grid(row=1, column=0, columnspan=2, pady=(0, 18))

        for index, maze in enumerate(SAMPLE_MAZES):
            self._build_maze_card(index, maze)

    def _build_maze_card(self, index, maze):
        preview = Image.open(maze.path).convert("RGB")
        preview.thumbnail((280, 210), Image.Resampling.LANCZOS)
        preview_image = ImageTk.PhotoImage(preview)
        self.preview_images.append(preview_image)

        card = tk.Frame(self, bg="#2c313c", highlightbackground="#4b5563", highlightthickness=1, cursor="hand2")
        card.grid(row=2, column=index, padx=20, pady=(0, 20), sticky="nsew")

        image_label = tk.Label(card, image=preview_image, bg="#2c313c", cursor="hand2")
        image_label.pack(padx=14, pady=(14, 10))
        title_label = tk.Label(card, text=maze.label, bg="#2c313c", fg="white", font=("Arial", 14, "bold"), cursor="hand2")
        title_label.pack(pady=(0, 6))
        desc_label = tk.Label(card, text=maze.description, bg="#2c313c", fg="#cbd5e1", font=("Arial", 10), wraplength=250, justify="center", cursor="hand2")
        desc_label.pack(padx=16, pady=(0, 16))

        for widget in (card, image_label, title_label, desc_label):
            widget.bind("<Button-1>", lambda _event, path=maze.path: self._select(path))

    def _select(self, maze_path):
        self.destroy()
        self.on_select(maze_path)
