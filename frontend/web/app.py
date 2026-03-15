from pathlib import Path
import sys
import time

import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.maze_service import MazeService, SolveArtifacts
from backend.settings import SAMPLE_MAZES


@st.cache_data(show_spinner=False)
def solve_maze_cached(sample_key, start_pos, end_pos):
    sample = next(maze for maze in SAMPLE_MAZES if maze.key == sample_key)
    service = MazeService()
    service.load_maze(sample.path)
    service.begin_point_selection()
    service.handle_point_click(start_pos)
    service.handle_point_click(end_pos)
    artifacts = service.solve()

    return {
        "display_image": service.model.display_image.copy(),
        "maze_image": service.model.maze_image.copy(),
        "result_image": artifacts.solved_image if artifacts.solved else artifacts.visited_image,
        "solve_time": artifacts.solve_time,
        "total_time": artifacts.total_time,
        "path": artifacts.path,
        "visited_nodes": artifacts.visited_nodes,
        "solved": artifacts.solved,
    }


def initialize_state():
    defaults = {
        "service": MazeService(),
        "selected_maze_key": SAMPLE_MAZES[0].key,
        "display_image": None,
        "maze_image": None,
        "result_image": None,
        "status": "WAIT",
        "time_value": 0.0,
        "last_click": None,
        "point_mode": False,
        "animate_pending": False,
        "solve_artifacts": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def current_sample():
    return next(maze for maze in SAMPLE_MAZES if maze.key == st.session_state.selected_maze_key)


def handle_open():
    sample = current_sample()
    success, display_image, maze_image = st.session_state.service.load_maze(sample.path)
    if success:
        st.session_state.display_image = display_image
        st.session_state.maze_image = maze_image
        st.session_state.result_image = None
        st.session_state.time_value = 0.0
        st.session_state.status = "WAIT"
        st.session_state.point_mode = False
        st.session_state.last_click = None
        st.session_state.animate_pending = False
        st.session_state.solve_artifacts = None


def handle_set():
    display_image, maze_image = st.session_state.service.begin_point_selection()
    st.session_state.display_image = display_image
    st.session_state.maze_image = maze_image
    st.session_state.result_image = None
    st.session_state.status = "WAIT"
    st.session_state.time_value = 0.0
    st.session_state.point_mode = True
    st.session_state.last_click = None
    st.session_state.animate_pending = False
    st.session_state.solve_artifacts = None


def handle_reset():
    display_image, maze_image = st.session_state.service.reset()
    st.session_state.display_image = display_image
    st.session_state.maze_image = maze_image
    st.session_state.result_image = None
    st.session_state.status = "WAIT"
    st.session_state.time_value = 0.0
    st.session_state.point_mode = False
    st.session_state.last_click = None
    st.session_state.animate_pending = False
    st.session_state.solve_artifacts = None


def handle_start():
    start_pos = st.session_state.service.model.start_pos
    end_pos = st.session_state.service.model.end_pos
    if start_pos is None or end_pos is None:
        return

    cached_solution = solve_maze_cached(
        st.session_state.selected_maze_key,
        start_pos,
        end_pos,
    )

    artifacts = SolveArtifacts(
        path=cached_solution["path"],
        visited_nodes=cached_solution["visited_nodes"],
        solve_time=cached_solution["solve_time"],
        solved_image=cached_solution["result_image"] if cached_solution["solved"] else cached_solution["display_image"],
        visited_image=cached_solution["maze_image"],
        total_time=cached_solution["total_time"],
        solved=cached_solution["solved"],
    )

    st.session_state.solve_artifacts = artifacts
    st.session_state.display_image = cached_solution["display_image"]
    st.session_state.maze_image = cached_solution["maze_image"]
    st.session_state.result_image = None
    st.session_state.time_value = artifacts.solve_time
    st.session_state.status = "WAIT"
    st.session_state.animate_pending = True


def render_controls():
    selected_label = st.selectbox(
        "Maze Sample",
        options=[maze.label for maze in SAMPLE_MAZES],
        index=next(index for index, maze in enumerate(SAMPLE_MAZES) if maze.key == st.session_state.selected_maze_key),
    )
    st.session_state.selected_maze_key = next(maze.key for maze in SAMPLE_MAZES if maze.label == selected_label)

    cols = st.columns(4)
    if cols[0].button("Open", use_container_width=True):
        handle_open()
    if cols[1].button("Set", use_container_width=True):
        handle_set()
    if cols[2].button("Reset", use_container_width=True):
        handle_reset()
    if cols[3].button("Start", use_container_width=True, type="primary"):
        handle_start()


def render_status():
    metrics = st.columns(3)
    metrics[0].metric("Status", st.session_state.status)
    metrics[1].metric("Time(s)", f"{st.session_state.time_value:.4f}")
    metrics[2].metric("Point Mode", "ON" if st.session_state.point_mode else "OFF")


def render_canvas():
    left, right = st.columns(2)
    left_placeholder = left.empty()
    right_placeholder = right.empty()

    with left:
        st.subheader("Original Image")
        if st.session_state.display_image is None:
            st.info("Press Open to load one of the sample mazes.")
            return left_placeholder, right_placeholder

        if st.session_state.point_mode:
            with left_placeholder.container():
                click = streamlit_image_coordinates(
                    st.session_state.display_image,
                    key="maze-click-canvas",
                    width=st.session_state.display_image.width,
                )
            if click:
                point = (click["x"], click["y"])
                if point != st.session_state.last_click:
                    st.session_state.last_click = point
                    updated_image, maze_image, completed, elapsed_time = st.session_state.service.handle_point_click(point)
                    st.session_state.display_image = updated_image or st.session_state.display_image
                    if maze_image is not None:
                        st.session_state.maze_image = maze_image
                    if completed:
                        st.session_state.point_mode = False
                        st.session_state.time_value = elapsed_time
                    st.rerun()
        else:
            left_placeholder.image(st.session_state.display_image, use_container_width=False)

        st.caption("Click on the original image after pressing Set to place the start and end points.")

    with right:
        st.subheader("Processed / Result")
        if st.session_state.result_image is not None:
            right_placeholder.image(st.session_state.result_image, use_container_width=True)
        elif st.session_state.maze_image is not None:
            right_placeholder.image(st.session_state.maze_image, use_container_width=True)
        else:
            st.info("The processed maze will appear here.")

    return left_placeholder, right_placeholder


def animate_solution(left_placeholder, right_placeholder):
    artifacts = st.session_state.solve_artifacts
    if artifacts is None:
        return

    animated_display = st.session_state.service.model.display_image.copy()
    animated_maze = st.session_state.service.model.maze_image.copy()

    draw_maze = ImageDraw.Draw(animated_maze)
    chunk_size = 50
    for start_index in range(0, len(artifacts.visited_nodes), chunk_size):
        end_index = min(start_index + chunk_size, len(artifacts.visited_nodes))
        for index in range(start_index, end_index):
            row, col = artifacts.visited_nodes[index]
            ratio = index / (len(artifacts.visited_nodes) - 1) if len(artifacts.visited_nodes) > 1 else 0
            color = st.session_state.service.model.gradient(
                st.session_state.service.model.start_color,
                st.session_state.service.model.end_color,
                ratio,
            )
            draw_maze.point((col, row), fill=color)

        right_placeholder.image(animated_maze, use_container_width=True)
        time.sleep(0.03)

    if artifacts.solved:
        draw_display = ImageDraw.Draw(animated_display)
        for index in range(len(artifacts.path) - 1):
            start_point = (artifacts.path[index][1], artifacts.path[index][0])
            end_point = (artifacts.path[index + 1][1], artifacts.path[index + 1][0])
            draw_display.line([start_point, end_point], fill="#009900", width=5)
            left_placeholder.image(animated_display, use_container_width=False)
            time.sleep(0.001)

    st.session_state.display_image = animated_display
    st.session_state.maze_image = animated_maze
    st.session_state.result_image = animated_display if artifacts.solved else animated_maze
    st.session_state.time_value = artifacts.total_time
    st.session_state.status = "AC" if artifacts.solved else "WA"
    st.session_state.animate_pending = False
    st.session_state.solve_artifacts = None


def main():
    st.set_page_config(page_title="MazeSolver Live Demo", page_icon="🧩", layout="wide")
    initialize_state()

    st.title("MazeSolver Live Demo")
    st.caption("The web demo follows the same interaction flow as the local GUI: Open -> Set -> click start/end -> Start -> Reset.")

    render_controls()
    render_status()
    left_placeholder, right_placeholder = render_canvas()

    if st.session_state.animate_pending and st.session_state.display_image is not None:
        animate_solution(left_placeholder, right_placeholder)

    with st.expander("How to use"):
        st.write("1. Choose Maze 1 or Maze 2 and click Open.")
        st.write("2. Click Set.")
        st.write("3. Click once on the original image for the start point and once for the end point.")
        st.write("4. Click Start to watch the BFS exploration and final path animation.")
        st.write("5. Click Reset to clear the current maze state.")


if __name__ == "__main__":
    main()
