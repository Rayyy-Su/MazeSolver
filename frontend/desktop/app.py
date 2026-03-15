import tkinter as tk

from PIL import Image, ImageDraw, ImageTk

from backend.services.maze_service import MazeService
from backend.settings import DARK_COLOR, ICON_DIR, WINDOW_GEOMETRY, WINDOW_TITLE
from frontend.desktop.dialogs import SampleMazeDialog
from frontend.desktop.views import MainView


class DesktopMazeController:
    def __init__(self, app):
        self.app = app
        self.service = MazeService()
        self.view = MainView(app, self)
        self.anim_display_img = None
        self.anim_maze_img = None
        self.total_solve_time = 0.0
        self.view.image_display_frame.image_label.bind("<Button-1>", self.on_image_click)

    def open_maze_dialog(self):
        SampleMazeDialog(self.app, self.load_maze)

    def load_maze(self, path):
        success, display_img, maze_img = self.service.load_maze(path)
        if success:
            self.view.image_display_frame.update_image(self.view.image_display_frame.image_label, display_img)
            self.view.image_display_frame.update_image(self.view.image_display_frame.maze_image_label, maze_img)
            self.reset_ui_state()

    def set_point_mode(self):
        display_img, maze_img = self.service.begin_point_selection()
        self.app.config(cursor="crosshair")
        if display_img:
            self.view.image_display_frame.update_image(self.view.image_display_frame.image_label, display_img)
        if maze_img:
            self.view.image_display_frame.update_image(self.view.image_display_frame.maze_image_label, maze_img)

    def on_image_click(self, event):
        updated_image, maze_image, completed, elapsed_time = self.service.handle_point_click((event.x, event.y))
        if updated_image:
            self.view.image_display_frame.update_image(self.view.image_display_frame.image_label, updated_image)
        if completed:
            self.app.config(cursor="")
            self.view.image_display_frame.update_image(self.view.image_display_frame.maze_image_label, maze_image)
            self.view.time_frame.set_time(elapsed_time)

    def reset_maze(self):
        display_img, maze_img = self.service.reset()
        if display_img:
            self.view.image_display_frame.update_image(self.view.image_display_frame.image_label, display_img)
            self.view.image_display_frame.update_image(self.view.image_display_frame.maze_image_label, maze_img)
        self.reset_ui_state()

    def start_solving(self):
        if self.service.model.start_pos is None or self.service.model.end_pos is None:
            return

        self.view.status_frame.set_status("wait")
        self.app.update_idletasks()

        artifacts = self.service.solve()
        self.view.time_frame.set_time(artifacts.solve_time)
        self.app.update_idletasks()
        if not artifacts.solved:
            self.view.status_frame.set_status("wa")
            self.view.time_frame.set_time(artifacts.total_time)
            return

        self.anim_display_img = self.service.model.display_image.copy()
        self.anim_maze_img = self.service.model.maze_image.copy()
        self.total_solve_time = artifacts.solve_time
        self._animate_search(artifacts.visited_nodes, artifacts.path)

    def _animate_search(self, visited_nodes, final_path, index=0, chunk_size=50):
        draw_maze = ImageDraw.Draw(self.anim_maze_img)
        end_index = min(index + chunk_size, len(visited_nodes))
        for current_index in range(index, end_index):
            row, col = visited_nodes[current_index]
            ratio = current_index / (len(visited_nodes) - 1) if len(visited_nodes) > 1 else 0
            color = self.service.model.gradient(self.service.model.start_color, self.service.model.end_color, ratio)
            draw_maze.point((col, row), fill=color)

        self.view.image_display_frame.update_image(self.view.image_display_frame.maze_image_label, self.anim_maze_img)
        if end_index < len(visited_nodes):
            self.app.after(30, self._animate_search, visited_nodes, final_path, end_index, chunk_size)
        else:
            self._animate_path(final_path)

    def _animate_path(self, path, index=0):
        if index >= len(path) - 1:
            self.view.status_frame.set_status("ac")
            self.view.time_frame.set_time(self.service.skeletonize_time + self.total_solve_time)
            return

        draw_display = ImageDraw.Draw(self.anim_display_img)
        start_point = (path[index][1], path[index][0])
        end_point = (path[index + 1][1], path[index + 1][0])
        draw_display.line([start_point, end_point], fill="#009900", width=5)
        self.view.image_display_frame.update_image(self.view.image_display_frame.image_label, self.anim_display_img)
        self.app.after(1, self._animate_path, path, index + 1)

    def reset_ui_state(self):
        self.app.config(cursor="")
        self.view.time_frame.set_time(0.0)
        self.view.status_frame.set_status("wait")


class MazeDesktopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_GEOMETRY)
        self.configure(bg=DARK_COLOR)
        self.icon = ImageTk.PhotoImage(Image.open(ICON_DIR / "maze_icon.png"))
        self.wm_iconphoto(False, self.icon)
        self.controller = DesktopMazeController(self)


def main():
    app = MazeDesktopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
