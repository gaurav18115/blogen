import subprocess

def open_file_with_default_app(filepath):
    try:
        subprocess.run(["subl .", filepath], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while opening the file: {e}")
    except FileNotFoundError:
        print("The 'open' command is not available on this system (non-macOS).")
