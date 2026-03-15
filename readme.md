# MazeSolver

MazeSolver is now organized into a clear `frontend / backend` structure:

- `frontend/desktop`: the local Tkinter GUI
- `frontend/web`: the Streamlit live demo for browser use
- `backend`: the shared maze-processing logic used by both frontends

The desktop GUI and browser demo use the same interaction flow:

1. `Open`
2. `Set`
3. Click once for the start point
4. Click once for the end point
5. `Start`
6. `Reset`

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

## Features

- Two built-in maze samples shared by desktop and web
- Otsu thresholding and edge barrier cleanup
- Skeletonization
- BFS pathfinding
- A live demo that follows the same `Open / Set / Start / Reset` workflow as the local GUI

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

Then open the local URL shown in the terminal, usually:

```text
http://127.0.0.1:8501
```

## Deploy The Live Demo

This project is ready for Streamlit Community Cloud.

1. Push the repository to GitHub.
2. Sign in to Streamlit Community Cloud.
3. Create a new app from your GitHub repository.
4. Choose the branch you want to deploy.
5. Set the main file path to `frontend/web/app.py`.
6. Deploy the app.
7. Copy the generated Streamlit URL.
8. Use that URL for the `Live demo` button in your personal portfolio website.

## How To Push This Repo To GitHub

If this folder is already connected to GitHub:

```bash
git status
git add .
git commit -m "Refactor MazeSolver into frontend/backend structure"
git push origin main
```

If your default branch is `master`, use:

```bash
git push origin master
```

If this folder is not connected to a GitHub repository yet:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Detailed GitHub Workflow

1. Go to GitHub and create a new empty repository.
2. Copy the repository URL from GitHub.
3. Open a terminal and go to the MazeSolver folder.
4. Run `git status` to check what will be committed.
5. Run `git add .` to stage the project files.
6. Run `git commit -m "Refactor MazeSolver into frontend/backend structure"`.
7. Run `git branch` to check your current branch name.
8. If needed, rename the branch with `git branch -M main`.
9. Run `git remote -v` to see whether a remote is already configured.
10. If no remote exists, run `git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git`.
11. Run `git push -u origin main`.
12. If GitHub rejects password login, generate a Personal Access Token in GitHub settings and use that token instead.
13. Refresh the GitHub repository page and confirm all files are visible.
14. Connect the same repo and branch in Streamlit Community Cloud.
15. After deployment, copy the Streamlit app URL into your website's `Live demo` button.

## Notes

- `maze_graph/` stores the built-in sample mazes.
- `icons/` stores the GUI button and status assets.
