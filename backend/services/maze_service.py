from dataclasses import dataclass

from PIL import ImageDraw

from backend.models.maze_model import MazeModel


@dataclass
class SolveArtifacts:
    path: list
    visited_nodes: list
    solve_time: float
    solved_image: object
    visited_image: object
    total_time: float
    solved: bool


class MazeService:
    def __init__(self):
        self.model = MazeModel()
        self.is_setting_points = False
        self.skeletonize_time = 0.0

    def load_maze(self, file_path):
        success, display_image, maze_image = self.model.load_image(file_path)
        if success:
            self.is_setting_points = False
            self.skeletonize_time = 0.0
        return success, display_image, maze_image

    def begin_point_selection(self):
        self.is_setting_points = True
        self.model.reset_points()
        if self.model.original_image:
            self.model.display_image = self.model.original_image.copy()
        if self.model.processed_maze_backup:
            self.model.maze_image = self.model.processed_maze_backup.copy()
        return self.model.display_image, self.model.maze_image

    def handle_point_click(self, pos):
        if not self.is_setting_points:
            return None, None, False, 0.0

        updated_image = self.model.set_point(pos)
        skeleton_complete = False
        maze_image = self.model.maze_image

        if self.model.end_pos is not None:
            self.is_setting_points = False
            maze_image, elapsed_time = self.model.skeletonize()
            self.skeletonize_time = elapsed_time
            skeleton_complete = True
            return updated_image, maze_image, skeleton_complete, elapsed_time

        return updated_image, maze_image, skeleton_complete, 0.0

    def reset(self):
        self.is_setting_points = False
        self.skeletonize_time = 0.0
        return self.model.reset()

    def solve(self):
        path, visited_nodes, solve_time = self.model.solve_maze()
        solved_image = self.model.display_image.copy()
        visited_image = self.model.maze_image.copy()

        visited_draw = ImageDraw.Draw(visited_image)
        for index, (row, col) in enumerate(visited_nodes):
            ratio = index / max(len(visited_nodes) - 1, 1)
            color = self.model.gradient(self.model.start_color, self.model.end_color, ratio)
            visited_draw.point((col, row), fill=color)

        if path:
            solved_draw = ImageDraw.Draw(solved_image)
            for index in range(len(path) - 1):
                start = (path[index][1], path[index][0])
                end = (path[index + 1][1], path[index + 1][0])
                solved_draw.line([start, end], fill="#009900", width=5)

        total_time = self.skeletonize_time + solve_time
        return SolveArtifacts(
            path=path,
            visited_nodes=visited_nodes,
            solve_time=solve_time,
            solved_image=solved_image,
            visited_image=visited_image,
            total_time=total_time,
            solved=bool(path),
        )
