import datetime
import os
import sys

from tools.logger import log_info

project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Add the project root directory to the Python path
sys.path.append(project_root)


def get_ordinal_suffix(number):
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return suffix


def append_content_to_file(filename, new_content, st=None):
    if st:
        st.write(new_content)

    with open(filename, "a") as file:
        # Add a newline before writing the new content
        file.write("\n\n" + new_content)


def create_file_with_keyword(keyword, directory="_blogs", extension="md"):
    if not os.path.exists(directory):
        os.makedirs(directory)

    title = '_'.join(keyword.split(' '))
    subdirectory = os.path.join(directory, title)
    if not os.path.exists(subdirectory):
        os.makedirs(subdirectory)

    # Find the number of files starting with the same keyword
    num_files_with_same_keyword = sum(1 for file in os.listdir(subdirectory) if file.startswith(title))
    if num_files_with_same_keyword > 0:
        ordinal_suffix = get_ordinal_suffix(num_files_with_same_keyword + 1)
        filename = f"{title}-{num_files_with_same_keyword + 1}{ordinal_suffix}.{extension}"
    else:
        filename = f"{title}.{extension}"

    filepath = os.path.join(subdirectory, filename)

    # Create the new file
    with open(filepath, "w") as file:
        file.write(f"Runtime: {datetime.datetime.now()}")

    return filepath
