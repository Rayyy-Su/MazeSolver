# MazeSolver

MazeSolver is a maze image solver that preprocesses uploaded maze images, skeletonizes valid paths, and applies Breadth-First Search (BFS) to find a solution route.

The project now includes:

- A desktop GUI built with Tkinter
- A browser-based Streamlit app for deployment and public demos

## Features

- Upload your own maze image or try bundled sample mazes
- Otsu thresholding and boundary cleanup for preprocessing
- Skeletonization to simplify valid maze paths
- BFS pathfinding with visited-node visualization
- Side-by-side views of original, processed, and solved maze images

## Demo Images

![Demo 1](demo_images/demo1.png)
![Demo 2](demo_images/demo2.png)

## Local Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Web App

```bash
streamlit run streamlit_app.py
```

Then open the local URL shown by Streamlit in your browser.

## Run the Desktop App

```bash
python MazeApp.py
```

The desktop version expects the icon assets to be available through your local environment configuration.

## How to Use the Web App

1. Load a sample maze or upload your own image.
2. Set the start and end coordinates in the sidebar.
3. Click `Apply Points` to preview the selected positions.
4. Click `Solve Maze` to generate the path.

## Deployment

This project is ready for Streamlit Community Cloud deployment.

1. Push this repository to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app from your GitHub repository.
4. Set the main file path to `streamlit_app.py`.
5. Deploy.

## Core Technique

### Otsu Thresholding

For grayscale intensity histogram:

$$
p(i) = \frac{\text{number of pixels with intensity } i}{N}, \quad i = 0, 1, \dots, 255
$$

For each threshold $t$, compute:

$$
\omega_0(t) = \sum_{i=0}^{t} p(i),
\quad
\omega_1(t) = \sum_{i=t+1}^{L-1} p(i)
$$

$$
\mu_0(t) = \frac{1}{\omega_0(t)} \sum_{i=0}^{t} i \cdot p(i),
\quad
\mu_1(t) = \frac{1}{\omega_1(t)} \sum_{i=t+1}^{L-1} i \cdot p(i)
$$

The best threshold maximizes between-class variance:

$$
t^* = \underset{t}{\arg\max}\ \sigma_b^2(t)
$$

Then the binary image is computed by:

$$
dst(x, y) =
\begin{cases}
255 & \text{if } I(x, y) > t^* \\
0   & \text{if } I(x, y) \leq t^*
\end{cases}
$$
