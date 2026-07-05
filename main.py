# ENGLISH COMMENT EXPLAINING THE ENTIRE CODE:
# This updated script handles messy, nested HTML tags inside the <h1> tag.
# Instead of blindly taking everything inside <h1>, it first extracts the block,
# then strips away any inner HTML tags (like <a> or <span>) using regex substitution.
# It also decodes HTML entities (like &amp; or &#39;) into normal text characters.
# Finally, it sanitizes the string for macOS file naming rules and limits the length.

import os
import re
import html  # New standard library module to clean up HTML entities

try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    tk = None
    filedialog = None


def open_mac_folder_selector():
    if filedialog is None:
        raise RuntimeError("tkinter is unavailable in this Python environment")

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder_path = filedialog.askdirectory(
        title="Select Folder containing HTML files")
    root.destroy()
    return folder_path or None


def extract_first_heading_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as html_file:
        file_content = html_file.read()

        # Step 1: Find the <h1> block
        search_result = re.search(
            r'<h1[^>]*>(.*?)</h1>', file_content, re.IGNORECASE | re.DOTALL)

        if search_result:
            # Get whatever is inside the <h1> block (including other tags like <a>)
            raw_heading = search_result.group(1)

            # Step 2: Remove all internal HTML tags using Regex
            # r'<[^>]+>' means "find anything that starts with '<', has chars other than '>', and ends with '>'"
            text_without_tags = re.sub(r'<[^>]+>', '', raw_heading)

            # Step 3: Decode HTML entities (e.g., changes "&amp;" to "&")
            decoded_text = html.unescape(text_without_tags)

            # Step 4: Clean up white spaces and new lines
            # Replace multiple spaces/newlines with a single space, then strip edges
            clean_text = " ".join(decoded_text.split())

            # Step 5: Remove characters that macOS does not allow in file names
            safe_filename = re.sub(r'[\\/*?:"<>|]', "", clean_text)

            # If the resulting string is empty after cleaning, return None
            if not safe_filename:
                return None

            return safe_filename[:60]

    return None


def rename_html_files_in_selected_folder():
    folder_path = open_mac_folder_selector()

    if not folder_path:
        print("No folder was selected. Exiting program.")
        return

    print(f"Searching in folder: {folder_path}")

    for filename in os.listdir(folder_path):
        if filename.endswith(".html"):
            old_full_path = os.path.join(folder_path, filename)
            extracted_title = extract_first_heading_from_html(old_full_path)

            if extracted_title:
                new_filename = f"{extracted_title}.html"
                new_full_path = os.path.join(folder_path, new_filename)

                # Check if the exact filename is already exactly the same (to avoid re-renaming)
                if filename == new_filename:
                    print(
                        f"INFO: File '{filename}' already has the correct name. Skipping.")
                    continue

                # Make sure the new name doesn't conflict with another existing file
                if not os.path.exists(new_full_path):
                    os.rename(old_full_path, new_full_path)
                    print(f"SUCCESS: Renamed '{filename}' to '{new_filename}'")
                else:
                    print(
                        f"WARNING: File '{new_filename}' already exists. Cannot rename '{filename}'.")
            else:
                print(
                    f"INFO: No valid text found in <h1> for '{filename}'. Skipping.")


if __name__ == "__main__":
    rename_html_files_in_selected_folder()
