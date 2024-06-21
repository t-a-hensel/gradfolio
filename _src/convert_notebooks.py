import os
import subprocess
import shutil

# Step 1: Find the GitHub repository root
def find_git_root(path):
    while not os.path.exists(os.path.join(path, '.git')):
        parent = os.path.dirname(path)
        if parent == path:
            raise Exception("No .git directory found in this or any parent directory.")
        path = parent
    return path

# Step 2: Convert Jupyter notebooks to Markdown (with execution)
def convert_notebooks_to_markdown(notebook_dir, converted_notebooks_dir):
    if not os.path.exists(converted_notebooks_dir):
        os.makedirs(converted_notebooks_dir)
    
    notebooks = [f for f in os.listdir(notebook_dir) if f.endswith('.ipynb')]
    for notebook in notebooks:
        notebook_path = os.path.join(notebook_dir, notebook)
        subprocess.run([
            "jupyter", "nbconvert", "--to", "markdown", "--execute", 
            notebook_path, "--output-dir", converted_notebooks_dir
        ])

# Step 3: Move all files from converted_notebooks to _posts directory
def move_converted_files(converted_notebooks_dir, posts_dir):
    if not os.path.exists(posts_dir):
        os.makedirs(posts_dir)
    
    for item in os.listdir(converted_notebooks_dir):
        source = os.path.join(converted_notebooks_dir, item)
        destination = os.path.join(posts_dir, item)
        shutil.move(source, destination)

# Step 4: Commit and push changes to GitHub Pages repository
def update_github_pages_repo(github_repo_dir):
    subprocess.run(["git", "add", "."], cwd=github_repo_dir)
    subprocess.run(["git", "commit", "-m", "Add converted Jupyter notebooks as markdown"], cwd=github_repo_dir)
    subprocess.run(["git", "push", "origin", "main"], cwd=github_repo_dir)

# Main script
current_dir = os.getcwd()
github_repo_dir = find_git_root(current_dir)
notebook_dir = os.path.join(github_repo_dir, "_src/notebooks")  # Adjust as needed
converted_notebooks_dir = os.path.join(github_repo_dir, "_src/notebooks/converted")

markdown_dir = os.path.join(github_repo_dir, "_posts")

convert_notebooks_to_markdown(notebook_dir,converted_notebooks_dir)
move_converted_files(converted_notebooks_dir, markdown_dir)
update_github_pages_repo(github_repo_dir)
