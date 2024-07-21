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
def get_changed_notebooks():
    # Get the list of files changed since the last commit
    result = subprocess.run(['git', 'diff', '--name-only', 'HEAD'], stdout=subprocess.PIPE)
    changed_files = result.stdout.decode('utf-8').splitlines()
    
    # Filter to include only Jupyter notebooks
    changed_notebooks = [f for f in changed_files if f.endswith('.ipynb')]
    return changed_notebooks

def convert_notebooks_to_markdown(notebook_dir, converted_notebooks_dir):
    if not os.path.exists(converted_notebooks_dir):
        os.makedirs(converted_notebooks_dir)
    
    # Get the changed notebooks
    changed_notebooks = get_changed_notebooks()
    
    for notebook in changed_notebooks:
        relative_path = os.path.relpath(notebook, notebook_dir)
        notebook_path = os.path.join(notebook_dir, relative_path)
        if os.path.exists(notebook_path):
            subprocess.run([
                "jupyter", "nbconvert", "--to", "markdown", "--execute", 
                notebook_path, "--output-dir", converted_notebooks_dir
            ])
        else:
            print(f'Notebook {notebook} does not exist in {notebook_dir}.')

# Step 3: Move all files from converted_notebooks to _posts directory
def move_converted_files(converted_notebooks_dir, posts_dir):
    if not os.path.exists(posts_dir):
        os.makedirs(posts_dir)
    
    for item in os.listdir(converted_notebooks_dir):
        source = os.path.join(converted_notebooks_dir, item)
        destination = os.path.join(posts_dir, item)
        if os.path.exists(destination):
            if os.path.isdir(destination):
                shutil.rmtree(destination)
            elif os.path.isfile(destination):
                os.remove(destination)
        shutil.move(source, destination)

# Step 4: Commit and push changes to GitHub Pages repository
def update_github_pages_repo(github_repo_dir):
    subprocess.run(["git", "add", "."], cwd=github_repo_dir)
    subprocess.run(["git", "commit", "-m", "Add converted Jupyter notebooks as markdown"], cwd=github_repo_dir)

# Main script
current_dir = os.getcwd()
github_repo_dir = find_git_root(current_dir)
notebook_dir = os.path.join(github_repo_dir, "_src/notebooks")  # Adjust as needed
converted_notebooks_dir = os.path.join(github_repo_dir, "_src/notebooks/converted")

markdown_dir = os.path.join(github_repo_dir, "_posts")

convert_notebooks_to_markdown(notebook_dir,converted_notebooks_dir)
move_converted_files(converted_notebooks_dir, markdown_dir)
update_github_pages_repo(github_repo_dir)