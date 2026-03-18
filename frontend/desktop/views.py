import tkinter as tk
from PIL import Image, ImageTk

from backend.settings import BACKGROUND, ICON_DIR


class MainView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=master["bg"])
        master.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        master.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        self.image_display_frame = ImageDisplayFrame(master)
        self.button_frame = ButtonFrame(master, controller)
        self.time_frame = TimeFrame(master)
        self.status_frame = StatusFrame(master)

        self.button_frame.grid(column=0, row=0, rowspan=4, padx=(0, 30), sticky="NSEW")
        self.image_display_frame.grid(column=1, row=0, columnspan=4, rowspan=4, padx=(30, 30), pady=(80, 20), sticky="NSEW")
        self.status_frame.grid(column=0, row=4, padx=(0, 30), sticky="NSEW")
        self.time_frame.grid(column=1, row=4, columnspan=2, padx=(30, 0), pady=(0, 20), sticky="NW")


class ImageDisplayFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BACKGROUND)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1, uniform="image-pane")

        original_frame = self._create_image_panel("Original Graph")
        result_frame = self._create_image_panel("Result Graph")

        original_frame.grid(row=0, column=0, padx=12, pady=5, sticky="N")
        result_frame.grid(row=0, column=1, padx=12, pady=5, sticky="N")

        self.image_label = self._create_image_label(original_frame)
        self.maze_image_label = self._create_image_label(result_frame)
        self.image_label.grid(row=1, column=0, padx=5, pady=(8, 5), sticky="N")
        self.maze_image_label.grid(row=1, column=0, padx=5, pady=(8, 5), sticky="N")

    def _create_image_panel(self, title):
        frame = tk.Frame(self, bg=BACKGROUND)
        frame.grid_columnconfigure(0, weight=1)
        tk.Label(
            frame,
            text=title,
            bg=BACKGROUND,
            fg="white",
            font=("Arial", 18, "bold"),
        ).grid(row=0, column=0, pady=(0, 4))
        return frame

    def _create_image_label(self, parent):
        return tk.Label(parent, image=ImageTk.PhotoImage(Image.new("RGB", (512, 512), "white")), width=512, height=512)

    def update_image(self, label_widget, pil_image):
        if pil_image is None:
            return
        tk_image = ImageTk.PhotoImage(pil_image)
        label_widget.config(image=tk_image, width=pil_image.width, height=pil_image.height)
        label_widget.image = tk_image


class ButtonFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=BACKGROUND)
        self.grid_columnconfigure(0, weight=1)
        self.grid(sticky="NESW")

        buttons = [
            ("button_open.png", controller.open_maze_dialog),
            ("button_set.png", controller.set_point_mode),
            ("button_reset.png", controller.reset_maze),
            ("button_start.png", controller.start_solving),
        ]
        for index, (icon, command) in enumerate(buttons):
            button = self._create_button(ICON_DIR / icon, command)
            pady = (150, 20) if index == 0 else 20
            button.grid(row=index, column=0, padx=10, pady=pady)

    def _create_button(self, file_path, command):
        img = ImageTk.PhotoImage(file=str(file_path))
        btn = tk.Button(self, image=img, bg=BACKGROUND, command=command, relief="flat", bd=0, activebackground=BACKGROUND)
        btn.image = img
        return btn


class TimeFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BACKGROUND)
        self.time_var = tk.StringVar(value="0.0000 s")
        tk.Label(self, text="Time(s):", bg=BACKGROUND, fg="white", font=("Arial", 22, "bold")).grid(row=0, column=0, padx=15, pady=15)
        tk.Label(self, textvariable=self.time_var, bg=BACKGROUND, fg="white", font=("Arial", 22, "bold")).grid(row=0, column=1, padx=15, pady=15)

    def set_time(self, seconds):
        self.time_var.set(f"{seconds:.4f} s")


class StatusFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BACKGROUND)
        self.grid_columnconfigure(0, weight=1)
        self.status_images = {
            "wait": ImageTk.PhotoImage(Image.open(ICON_DIR / "WAIT.png")),
            "ac": ImageTk.PhotoImage(Image.open(ICON_DIR / "AC.png")),
            "wa": ImageTk.PhotoImage(Image.open(ICON_DIR / "WA.png")),
        }
        self.label = tk.Label(self, image=self.status_images["wait"], bg=BACKGROUND)
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="NSEW")

    def set_status(self, status):
        if status in self.status_images:
            self.label.config(image=self.status_images[status])
            self.label.image = self.status_images[status]
