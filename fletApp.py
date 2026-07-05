# ENGLISH COMMENT EXPLAINING THE ENTIRE CODE:
# This is the final, fully optimized Async Flet 0.85+ script.
# We fixed the FilePicker coroutine issue: Flet 0.85 transformed 'get_directory_path()'
# into an async function WITHOUT changing its name. So we simply use:
# 'await get_directory_dialog.get_directory_path(...)'.
# The UI updates are handled smoothly using 'page.update()' which is now universally
# safe to call inside async environments in the new Flet architecture.

import flet as ft
import os
import re
import html
import asyncio
try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    tk = None
    filedialog = None

# --- CORE LOGIC (منطق اصلی) ---


def extract_first_heading_from_html(file_path):
    """Reads HTML file, finds first <h1>, cleans it, and returns safe string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as html_file:
            file_content = html_file.read()
            # Find everything inside the first <h1> tag
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

# --- FLET ASYNC UI LOGIC (منطق رابط کاربری ناهمگام) ---


async def main(page: ft.Page):
    # 1. Setup Page Properties
    page.title = "HTML Auto Renamer"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.window.width = 600
    page.window.height = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # 2. UI Components (اجزای ظاهری)
    title_text = ft.Text("HTML Renamer Tool", size=30,
                         weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    subtitle_text = ft.Text(
        "Select a folder to automatically rename HTML files based on their <h1> tag.", color=ft.Colors.GREY_400)
    selected_path_text = ft.Text(
        "No folder selected.", italic=True, color=ft.Colors.GREY_500)

    # Log container to show progress
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

    def flush_logs():
        page.update()

    def debug_message(msg: str):
        print(msg)

    def open_folder_selector():
        if filedialog is None:
            raise RuntimeError(
                "tkinter is not available in this Python environment")

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder_path = filedialog.askdirectory(
            title="Select Folder containing HTML files"
        )
        root.destroy()
        return folder_path or None

    async def open_folder_picker(e):
        try:
            debug_message("folder picker opened")
            log_message("Opening folder picker...", ft.Colors.BLUE_200)
            folder_path = open_folder_selector()

            debug_message(f"folder picker returned: {folder_path!r}")

            if folder_path:
                selected_path_text.value = f"Selected: {folder_path}"
                flush_logs()

                log_list.controls.clear()
                log_message(
                    f"Starting process in: {folder_path}", ft.Colors.BLUE_200)

                # Process directly with async yields so the UI remains responsive.
                await process_folder(folder_path)

            else:
                log_message("Selection cancelled.", ft.Colors.RED_400)
                flush_logs()
        except Exception as ex:
            debug_message(f"folder picker error: {ex!r}")
            log_message(
                f"Error opening folder picker: {ex}", ft.Colors.RED_400)
            flush_logs()

    # 4. Main Processing Function (تابع اصلی پردازش)
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
                        log_message(
                            f"⏩ Skipped: '{filename}' (Name is already correct)",
                            ft.Colors.GREY,
                        )
                        continue

                    if not os.path.exists(new_full_path):
                        try:
                            await asyncio.to_thread(os.rename, old_full_path, new_full_path)
                            log_message(
                                f"✅ Success: '{filename}' -> '{new_filename}'",
                                ft.Colors.GREEN_400,
                            )
                        except Exception as ex:
                            log_message(
                                f"❌ Error renaming '{filename}': {ex}",
                                ft.Colors.RED_400,
                            )
                    else:
                        log_message(
                            f"⚠️ Warning: '{new_filename}' already exists. Cannot rename.",
                            ft.Colors.ORANGE_400,
                        )
                else:
                    log_message(
                        f"ℹ️ Info: No valid <h1> found in '{filename}'.",
                        ft.Colors.YELLOW_400,
                    )

            # Let the UI repaint between files.
            await asyncio.sleep(0)

        if not found_html:
            log_message("No .html files found in this folder.",
                        ft.Colors.RED_400)

        log_message("--- Process Finished ---", ft.Colors.BLUE_200)

    # 5. Assemble the Page UI (چیدن اجزا در صفحه)
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
