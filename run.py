import sys
import os


# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Get the parent directory of the current file
parent_directory = os.path.dirname(current_file_path)

# Create the relative path to app.py
app_file_path = os.path.join(parent_directory, 'app', 'app.py')

# Run the app.py script using the relative path
os.system(f'python {app_file_path}')
