# MazeSolver

A tool that solves maze images using image preprocessing, skeletonization, and BFS.

## Description

This project preprocesses a maze image, extracts its skeleton, and applies Breadth-First Search (BFS) to quickly find the solution path.

## Features

- Image preprocessing using Otsu thresholding and boundary refinement to prevent paths from traversing outside the maze
- Skeletonization to simplify maze structure and improve path analysis
- BFS-based pathfinding for efficient and reliable route discovery
- Visualized exploration and final-path rendering for intuitive solution tracing

# Techique

## Otsu

### 1.Histogram

$$
p(i) = \frac{\text{number of pixels with intensity } i }{N}, \quad i = 0, 1, \dots, 255
$$

where $N$ is the total number of pixels.

---

### 2. Try all possible thresholds $t$

**compute probabilities (weights)**

$$
\omega_0(t) = \sum_{i=0}^{t} p(i),
\quad
\omega_1(t) = \sum_{i=t+1}^{L-1} p(i)
$$

**compute means**

$$
\mu_0(t) = \frac{1}{\omega_0(t)} \sum_{i=0}^{t} i \cdot p(i),
\quad
\mu_1(t) = \frac{1}{\omega_1(t)} \sum_{i=t+1}^{L-1} i \cdot p(i)
$$

**compute variances**

$$
\sigma_b^2(t) = \omega_0(t)\,\omega_1(t)\,\big(\mu_0(t) - \mu_1(t)\big)^2
$$

---

### 3. Find the optimal threshold

$$
t^* = \underset{t}{\arg\max}\ \sigma_b^2(t)
$$

---

### 4. Apply the thresholding

$$
dst(x, y) =
\begin{cases}
255 & \text{if } I(x, y) > t^* \\
0   & \text{if } I(x, y) \leq t^*
\end{cases}
$$

## Demo

![Demo](demo_images/demo1.png)
![Demo](demo_images/demo2.png)

## Project Structure

```text
MazeSolver/
├── backend/
│   ├── models/
│   │   └── maze_model.py
│   ├── services/
│   │   └── maze_service.py
│   └── settings.py
├── frontend/
│   ├── desktop/
│   │   ├── app.py
│   │   ├── dialogs.py
│   │   └── views.py
│   └── web/
│       └── app.py
├── icons/
├── maze_graph/
├── demo_images/
├── requirements.txt
└── README.md
```

- `frontend/desktop`: the local Tkinter GUI
- `frontend/web`: the Streamlit live demo for browser use
- `backend`: the shared maze-processing logic used by both frontends
- `maze_graph/` stores the built-in sample mazes.
- `icons/` stores the GUI button and status assets.

The desktop GUI and browser demo use the same interaction flow:

1. `Open`
2. `Set`
3. Click once for the start point
4. Click once for the end point
5. `Start`
6. `Reset`

## Local Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run The Desktop GUI

```bash
python -m frontend.desktop.app
```

## Run The Web Demo

```bash
streamlit run frontend/web/app.py
```
