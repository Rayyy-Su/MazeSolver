from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = PROJECT_ROOT / "icons"
MAZE_GRAPH_DIR = PROJECT_ROOT / "maze_graph"

WINDOW_TITLE = "Maze Solver"
WINDOW_GEOMETRY = "1520x780+0+0"

BACKGROUND = "#2c313c"
BORDER = "#383e4c"
DARK_COLOR = "#1c1d20"
BTN_COLOR = "#3430d1"


@dataclass(frozen=True)
class SampleMaze:
    key: str
    label: str
    description: str
    path: Path


SAMPLE_MAZES = (
    SampleMaze(
        key="maze1",
        label="Maze 1",
        description="Rectangular maze with a cleaner corridor layout.",
        path=MAZE_GRAPH_DIR / "maze1.jpg",
    ),
    SampleMaze(
        key="maze2",
        label="Maze 2",
        description="Circular maze with denser turns and a more complex route.",
        path=MAZE_GRAPH_DIR / "maze2.jpg",
    ),
)
