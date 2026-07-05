# ENGLISH COMMENT EXPLAINING THE ENTIRE CODE:
# This is the 100% native Flet application for renaming HTML files.
# The freezing issue was caused by mixing 'tkinter' (for folder selection) with Flet on macOS.
# Both libraries fight for the Main GUI Thread (NSApplication), causing a permanent deadlock
# after the dialog closes.
# We have completely removed 'tkinter' and implemented Flet's native 'ft.FilePicker'.
# The execution flow uses Python's 'asyncio' architecture perfectly to keep the UI fluid and responsive.

import flet as ft
import os
import re
import html
import asyncio

# --- CORE LOGIC (منطق اصلی) ---


def extract_first_heading_from_html(file_path):
    """Reads HTML file, finds first <h1>, cleans it, and returns safe string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as html_file:
            file_content = html_file.read()
            # Search for the <h1> tag and capture its content
            search_result = re.search(
                r'<h1[^>]*>(.*?)</h1>', file_content, re.IGNORECASE | re.DOTALL)

            if search_result:
                raw_heading = search_result.group(1)
                text_without_tags = re.sub(r'<[^>]+>', '', raw_heading)
                decoded_text = html.unescape(text_without_tags)
                clean_text = " ".join(decoded_text.split())
                safe_filename = re.sub(r'[\\/*?:"<>|]', "", clean_text)

                if safe_filename:
                    return safe_filename[:60]
    except Exception as e:
        return None
    return None


# --- FLET ASYNC UI LOGIC (رابط کاربری ناهمگام) ---
async def main(page: ft.Page):
    # 1. Setup Page Properties
    page.title = "HTML Auto Renamer"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.window.width = 600
    page.window.height = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 2. UI Components
    title_text = ft.Text("HTML Renamer Tool", size=30,
                         weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    subtitle_text = ft.Text(
        "Select a folder to automatically rename HTML files based on their <h1> tag.", color=ft.Colors.GREY_400)
    selected_path_text = ft.Text(
        "No folder selected.", italic=True, color=ft.Colors.GREY_500)

    # Log container
    log_list = ft.ListView(expand=True, spacing=10,
                           padding=10, auto_scroll=True)
    log_container = ft.Container(
        content=log_list,
        border=ft.Border.all(1, ft.Colors.OUTLINE),
        border_radius=ft.BorderRadius.all(10),
        padding=10,
        expand=True,
    )

    def log_message(msg: str, color: str = ft.Colors.WHITE):
        log_list.controls.append(ft.Text(msg, color=color))
        page.update()

    # 3. File Picker Handler (استفاده از سیستم بومی فلت به جای تکینتر)
    async def on_dialog_result(e: ft.ControlEvent):
        # e.path contains the path if the user selected a folder
        if e.path:
            folder_path = e.path
            selected_path_text.value = f"Selected: {folder_path}"
            page.update()

            log_list.controls.clear()
            log_message(
                f"Starting process in: {folder_path}", ft.Colors.BLUE_200)

            # Start the renaming logic
            await process_folder(folder_path)
        else:
            log_message("Selection cancelled.", ft.Colors.RED_400)

    # Creating the Flet FilePicker natively
    get_directory_dialog = ft.FilePicker()
    get_directory_dialog.on_result = on_dialog_result
    page.overlay.append(get_directory_dialog)
    page.update()

    # The button click triggers this function
    async def open_folder_picker(e):
        # We await the native Flet coroutine to open the Mac folder window safely
        await get_directory_dialog.get_directory_path("Select Folder containing HTML files")

    # 4. Main Processing Function
    async def process_folder(folder_path):
        found_html = False
        for filename in os.listdir(folder_path):
            if filename.endswith(".html"):
                found_html = True
                old_full_path = os.path.join(folder_path, filename)
                extracted_title = extract_first_heading_from_html(
                    old_full_path)

                if extracted_title:
                    new_filename = f"{extracted_title}.html"
                    new_full_path = os.path.join(folder_path, new_filename)

                    if filename == new_filename:
                        log_message(f"⏩ Skipped: '{filename}'", ft.Colors.GREY)
                        continue

                    if not os.path.exists(new_full_path):
                        try:
                            # Safely run file system operations in a background thread
                            await asyncio.to_thread(os.rename, old_full_path, new_full_path)
                            log_message(
                                f"✅ Success: '{filename}' -> '{new_filename}'", ft.Colors.GREEN_400)
                        except Exception as ex:
                            log_message(
                                f"❌ Error renaming: {ex}", ft.Colors.RED_400)
                    else:
                        log_message(
                            f"⚠️ Warning: '{new_filename}' exists.", ft.Colors.ORANGE_400)
                else:
                    log_message(
                        f"ℹ️ Info: No <h1> found in '{filename}'.", ft.Colors.YELLOW_400)

            # Yield control back to Flet so the UI doesn't freeze during heavy loops
            await asyncio.sleep(0)

        if not found_html:
            log_message("No .html files found in this folder.",
                        ft.Colors.RED_400)

        log_message("--- Process Finished ---", ft.Colors.BLUE_200)

    # 5. Assemble the Page UI
    select_button = ft.Button(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.FOLDER_OPEN, color=ft.Colors.WHITE),
                ft.Text("Select Folder & Start", color=ft.Colors.WHITE)
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        on_click=open_folder_picker,
        bgcolor=ft.Colors.BLUE_700
    )

    page.add(
        title_text,
        subtitle_text,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        select_button,
        selected_path_text,
        ft.Text("Execution Logs:", weight=ft.FontWeight.W_500,
                color=ft.Colors.GREY_300),
        log_container
    )
    page.update()

if __name__ == "__main__":
    ft.run(main)
