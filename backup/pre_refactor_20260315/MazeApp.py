# main.py
import tkinter as tk
from PIL import Image, ImageTk,  ImageDraw
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


from MazeModel import MazeModel
from MainView import MainView


class MazeApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.model = MazeModel()
        self.view = MainView(self, self) 
        self.sample_dir = Path(__file__).parent / "maze_graph"
        self.sample_mazes = [
            {
                "label": "Maze 1",
                "description": "Rectangular maze with a cleaner corridor layout.",
                "path": self.sample_dir / "maze1.jpg",
            },
            {
                "label": "Maze 2",
                "description": "Circular maze with denser turns and a more complex route.",
                "path": self.sample_dir / "maze2.jpg",
            },
        ]

        self.title("Maze Solver (Refactored)")
        self.geometry("1520x780+0+0")
        self.configure(bg='#1c1d20')
        icon_path = os.getenv("ICON_PATH")
        self.icon = ImageTk.PhotoImage(Image.open(os.path.join(icon_path, 'maze_icon.png')))
        self.wm_iconphoto(False, self.icon)

        self.is_setting_points = False
        self.skeletonize_time = 0.0

        self.view.image_display_frame.image_label.bind("<Button-1>", self.on_image_click)

    def open_file(self):
        selector = tk.Toplevel(self)
        selector.title("Choose a Maze")
        selector.geometry("760x430")
        selector.configure(bg="#1c1d20")
        selector.resizable(False, False)
        selector.transient(self)
        selector.grab_set()
        selector.grid_columnconfigure((0, 1), weight=1)

        tk.Label(
            selector,
            text="Choose a sample maze",
            bg="#1c1d20",
            fg="white",
            font=("Arial", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(22, 8))

        tk.Label(
            selector,
            text="Pick the maze style you want to solve.",
            bg="#1c1d20",
            fg="#cbd5e1",
            font=("Arial", 11),
        ).grid(row=1, column=0, columnspan=2, pady=(0, 18))

        selector.preview_images = []
        for index, maze in enumerate(self.sample_mazes):
            preview = Image.open(maze["path"]).convert("RGB")
            preview.thumbnail((280, 210), Image.Resampling.LANCZOS)
            preview_image = ImageTk.PhotoImage(preview)
            selector.preview_images.append(preview_image)

            card = tk.Frame(
                selector,
                bg="#2c313c",
                highlightbackground="#4b5563",
                highlightthickness=1,
                cursor="hand2",
            )
            card.grid(row=2, column=index, padx=20, pady=(0, 20), sticky="nsew")

            image_label = tk.Label(
                card,
                image=preview_image,
                bg="#2c313c",
                cursor="hand2",
            )
            image_label.pack(padx=14, pady=(14, 10))

            title_label = tk.Label(
                card,
                text=maze["label"],
                bg="#2c313c",
                fg="white",
                font=("Arial", 14, "bold"),
                cursor="hand2",
            )
            title_label.pack(pady=(0, 6))

            desc_label = tk.Label(
                card,
                text=maze["description"],
                bg="#2c313c",
                fg="#cbd5e1",
                font=("Arial", 10),
                wraplength=250,
                justify="center",
                cursor="hand2",
            )
            desc_label.pack(padx=16, pady=(0, 16))

            widgets = (card, image_label, title_label, desc_label)
            for widget in widgets:
                widget.bind(
                    "<Button-1>",
                    lambda _event, maze_path=maze["path"], dialog=selector: self._load_sample_maze(maze_path, dialog),
                )

    def _load_sample_maze(self, file_path, dialog):
        if dialog is not None:
            dialog.destroy()

        success, display_img, maze_img = self.model.load_image(file_path)
        if success:
            self.view.image_display_frame.update_image(
                self.view.image_display_frame.image_label, display_img
            )
            self.view.image_display_frame.update_image(
                self.view.image_display_frame.maze_image_label, maze_img
            )
            self.reset_ui_state()

    def set_point_mode(self):
        self.is_setting_points = True
        self.config(cursor="crosshair")
        self.model.reset_points()
        if self.model.original_image:
             self.view.image_display_frame.update_image(
                self.view.image_display_frame.image_label, self.model.original_image
            )

    def on_image_click(self, event):
        if not self.is_setting_points:
            return
        
        updated_image = self.model.set_point((event.x, event.y))
        
        if updated_image:
            self.view.image_display_frame.update_image(
                self.view.image_display_frame.image_label, updated_image
            )
        
        if self.model.end_pos is not None:
            self.is_setting_points = False
            self.config(cursor="")
            maze_img, elapsed_time = self.model.skeletonize()
            if maze_img:
                self.view.image_display_frame.update_image(
                    self.view.image_display_frame.maze_image_label, maze_img
                )
                self.skeletonize_time = elapsed_time
                self.view.time_frame.set_time(self.skeletonize_time)

    def reset_maze(self):
        display_img, maze_img = self.model.reset()
        if display_img:
            self.view.image_display_frame.update_image(
                self.view.image_display_frame.image_label, display_img
            )
            self.view.image_display_frame.update_image(
                self.view.image_display_frame.maze_image_label, maze_img
            )
        self.reset_ui_state()

    def start_solving(self):
        if self.model.start_pos is None or self.model.end_pos is None:
            print("Error: Start and end points must be set.")
            return

        self.view.status_frame.set_status('wait')
        self.update_idletasks()

        path, visited_nodes, solve_time = self.model.solve_maze()
        self.view.time_frame.set_time(solve_time)
        self.update_idletasks()
        if not path:
            self.view.status_frame.set_status('wa')
            total_time = self.skeletonize_time + solve_time
            self.view.time_frame.set_time(total_time)
            self.update_idletasks()
            return
        
        self.anim_display_img = self.model.display_image.copy()
        self.anim_maze_img = self.model.maze_image.copy()

        self.total_solve_time = solve_time
        self._animate_search(visited_nodes, path)

    def _animate_search(self, visited_nodes, final_path, index=0, chunk_size=50):
        draw_maze = ImageDraw.Draw(self.anim_maze_img)
        
        end_index = min(index + chunk_size, len(visited_nodes))
        
        for i in range(index, end_index):
            r, c = visited_nodes[i]
            t = i / (len(visited_nodes) - 1) if len(visited_nodes) > 1 else 0
            color = self.model._gradient(self.model.start_color, self.model.end_color, t)
            draw_maze.point((c, r), fill=color)

        self.view.image_display_frame.update_image(
            self.view.image_display_frame.maze_image_label, self.anim_maze_img
        )

        if end_index < len(visited_nodes):
            self.after(30, self._animate_search, visited_nodes, final_path, end_index, chunk_size)
        else:
            self._animate_path(final_path)

    def _animate_path(self, path, index=0):
        if index >= len(path) - 1:
            self.view.status_frame.set_status('ac')
            total_time = self.skeletonize_time + self.total_solve_time
            self.view.time_frame.set_time(total_time)
            self.update_idletasks()
            return

        draw_display = ImageDraw.Draw(self.anim_display_img)

        start_point = (path[index][1], path[index][0])
        end_point = (path[index + 1][1], path[index + 1][0])
        draw_display.line([start_point, end_point], fill="#009900", width=5)
        
        self.view.image_display_frame.update_image(
            self.view.image_display_frame.image_label, self.anim_display_img
        )
        self.after(1, self._animate_path, path, index + 1)

    def reset_ui_state(self):
        self.is_setting_points = False
        self.config(cursor="")
        self.skeletonize_time = 0.0
        self.view.time_frame.set_time(0.0)
        self.view.status_frame.set_status('wait')

if __name__ == "__main__":
    app = MazeApp()
    app.mainloop()
