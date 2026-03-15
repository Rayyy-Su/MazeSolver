from pathlib import Path

import streamlit as st
from PIL import ImageDraw

from MazeModel import MazeModel


APP_DIR = Path(__file__).parent
SAMPLE_DIR = APP_DIR / "maze_graph"
SAMPLE_IMAGES = {
    path.name: path
    for path in sorted(SAMPLE_DIR.glob("*"))
    if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
}


def initialize_state():
    defaults = {
        "model": None,
        "source_id": None,
        "source_label": None,
        "display_image": None,
        "maze_image": None,
        "skeleton_image": None,
        "solved_image": None,
        "visited_image": None,
        "skeletonize_time": 0.0,
        "solve_time": 0.0,
        "path_found": None,
        "path_length": 0,
        "visited_count": 0,
        "start_x": 0,
        "start_y": 0,
        "end_x": 0,
        "end_y": 0,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def load_maze(source, source_id, label):
    model = MazeModel()
    success, display_image, maze_image = model.load_image(source)
    if not success:
        st.error("Unable to load this maze image.")
        return

    width, height = display_image.size
    margin = 20

    st.session_state.model = model
    st.session_state.source_id = source_id
    st.session_state.source_label = label
    st.session_state.display_image = display_image.copy()
    st.session_state.maze_image = maze_image.copy()
    st.session_state.skeleton_image = maze_image.copy()
    st.session_state.solved_image = None
    st.session_state.visited_image = None
    st.session_state.skeletonize_time = 0.0
    st.session_state.solve_time = 0.0
    st.session_state.path_found = None
    st.session_state.path_length = 0
    st.session_state.visited_count = 0
    st.session_state.start_x = min(margin, width - 1)
    st.session_state.start_y = min(margin, height - 1)
    st.session_state.end_x = max(width - margin, 0)
    st.session_state.end_y = max(height - margin, 0)


def ensure_points_applied():
    model = st.session_state.model
    if model is None:
        return False

    model.reset()
    model.set_point((st.session_state.start_x, st.session_state.start_y))
    model.set_point((st.session_state.end_x, st.session_state.end_y))
    skeleton_image, skeletonize_time = model.skeletonize()

    st.session_state.display_image = model.display_image.copy()
    st.session_state.skeleton_image = skeleton_image.copy() if skeleton_image else None
    st.session_state.skeletonize_time = skeletonize_time
    st.session_state.solved_image = None
    st.session_state.visited_image = None
    st.session_state.path_found = None
    st.session_state.path_length = 0
    st.session_state.visited_count = 0
    st.session_state.solve_time = 0.0
    return True


def solve_maze():
    model = st.session_state.model
    if model is None:
        return

    if not ensure_points_applied():
        return

    path, visited_nodes, solve_time = model.solve_maze()
    solved_image = model.display_image.copy()
    visited_image = model.maze_image.copy()

    visited_draw = ImageDraw.Draw(visited_image)
    for index, (row, col) in enumerate(visited_nodes):
        ratio = index / max(len(visited_nodes) - 1, 1)
        color = model._gradient(model.start_color, model.end_color, ratio)
        visited_draw.point((col, row), fill=color)

    if path:
        solved_draw = ImageDraw.Draw(solved_image)
        for index in range(len(path) - 1):
            start = (path[index][1], path[index][0])
            end = (path[index + 1][1], path[index + 1][0])
            solved_draw.line([start, end], fill="#00C853", width=5)

    st.session_state.solved_image = solved_image
    st.session_state.visited_image = visited_image
    st.session_state.solve_time = solve_time
    st.session_state.path_found = bool(path)
    st.session_state.path_length = len(path)
    st.session_state.visited_count = len(visited_nodes)


def main():
    st.set_page_config(
        page_title="MazeSolver",
        page_icon="🧩",
        layout="wide",
    )
    initialize_state()

    st.title("MazeSolver")
    st.caption("Upload a maze image, place start/end coordinates, and solve it in the browser.")

    with st.sidebar:
        st.header("Maze Input")
        uploaded_file = st.file_uploader(
            "Upload a maze image",
            type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"],
        )
        sample_name = st.selectbox(
            "Or use a sample maze",
            options=["None"] + list(SAMPLE_IMAGES.keys()),
        )

        should_load = st.button("Load Maze", use_container_width=True)
        if should_load:
            if uploaded_file is not None:
                uploaded_file.seek(0)
                load_maze(uploaded_file, f"upload:{uploaded_file.name}", uploaded_file.name)
            elif sample_name != "None":
                sample_path = SAMPLE_IMAGES[sample_name]
                load_maze(str(sample_path), f"sample:{sample_name}", sample_name)
            else:
                st.warning("Choose a sample maze or upload your own image first.")

    if st.session_state.model is None:
        st.info("Load a maze image from the sidebar to start the web demo.")
        return

    model = st.session_state.model
    width, height = model.display_image.size

    with st.sidebar:
        st.header("Control Panel")
        st.write(f"Current maze: `{st.session_state.source_label}`")
        st.number_input("Start X", min_value=0, max_value=width - 1, key="start_x")
        st.number_input("Start Y", min_value=0, max_value=height - 1, key="start_y")
        st.number_input("End X", min_value=0, max_value=width - 1, key="end_x")
        st.number_input("End Y", min_value=0, max_value=height - 1, key="end_y")

        if st.button("Apply Points", use_container_width=True):
            ensure_points_applied()

        if st.button("Solve Maze", type="primary", use_container_width=True):
            solve_maze()

    metrics = st.columns(4)
    metrics[0].metric("Image Size", f"{width} x {height}")
    metrics[1].metric("Skeletonize", f"{st.session_state.skeletonize_time:.4f}s")
    metrics[2].metric("Solve Time", f"{st.session_state.solve_time:.4f}s")
    status_text = (
        "Ready"
        if st.session_state.path_found is None
        else "Solved" if st.session_state.path_found else "No Path"
    )
    metrics[3].metric("Status", status_text)

    if st.session_state.path_found is not None:
        summary = st.columns(2)
        summary[0].metric("Visited Nodes", st.session_state.visited_count)
        summary[1].metric("Path Length", st.session_state.path_length)

    gallery = st.columns(3)
    gallery[0].image(
        st.session_state.display_image,
        caption="Original View",
        use_container_width=True,
    )
    gallery[1].image(
        st.session_state.skeleton_image or st.session_state.maze_image,
        caption="Processed / Skeletonized",
        use_container_width=True,
    )
    result_image = st.session_state.solved_image or st.session_state.visited_image
    if result_image is not None:
        gallery[2].image(
            result_image,
            caption="Solved Result",
            use_container_width=True,
        )
    else:
        gallery[2].info("Apply points and solve the maze to see the result here.")

    st.markdown(
        """
        ### How to use
        1. Load a sample maze or upload your own image.
        2. Enter start and end coordinates in the sidebar.
        3. Click `Apply Points` to preview the selected positions.
        4. Click `Solve Maze` to generate the path.
        """
    )


if __name__ == "__main__":
    main()
