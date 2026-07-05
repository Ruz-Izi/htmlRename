# ENGLISH COMMENT EXPLAINING THE ENTIRE CODE:
# This script includes a robust 'logging' system to output all events and errors to 'app_debug.log'.
# It addresses the Flet FilePicker TimeoutException bug on macOS by introducing a native AppleScript fallback.
# If Flet's 'get_directory_path()' times out, the code catches the exception, logs it,
# and safely uses 'osascript' to open the Mac folder picker without freezing the main thread.
# Tkinter is entirely avoided to prevent UI deadlocks.

import flet as ft
import os
import re
import html
import asyncio
import logging
import subprocess

# --- 0. SETUP LOGGING SYSTEM ---
# This creates a file named 'app_debug.log' and records every single action.
logging.basicConfig(
    filename='app_debug.log',
    filemode='w',  # Overwrite log on each run
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("=== Application Started ===")

# --- 1. MACOS NATIVE FALLBACK ---


def mac_native_folder_picker():
    """Bypasses Flet's FilePicker and uses native macOS AppleScript to pick a folder safely."""
    try:
        logger.info("Launching AppleScript native folder picker...")
        # AppleScript command to select a folder and return its POSIX path
        script = 'return POSIX path of (choose folder with prompt "Select Folder containing HTML files")'
        result = subprocess.run(
            ['osascript', '-e', script], capture_output=True, text=True)

        if result.returncode == 0:
            selected_path = result.stdout.strip()
            logger.info(f"AppleScript returned path: {selected_path}")
            return selected_path
        else:
            logger.warning("AppleScript dialog cancelled by user.")
            return None
    except Exception as e:
        logger.error(f"AppleScript execution failed: {e}")
        return None

# --- 2. CORE LOGIC ---


def extract_first_heading_from_html(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as html_file:
            file_content = html_file.read()
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
        logger.error(f"Error reading file {file_path}: {e}")
    return None

# --- 3. FLET ASYNC UI LOGIC ---


async def main(page: ft.Page):
    logger.info("Flet UI initialization started.")

    # Setup Page Properties
    page.title = "HTML Auto Renamer"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.window.width = 600
    page.window.height = 700

    # UI Components
    title_text = ft.Text("HTML Renamer Tool", size=30,
                         weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    subtitle_text = ft.Text(
        "Select a folder to rename HTML files based on their <h1> tag.", color=ft.Colors.GREY_400)
    selected_path_text = ft.Text(
        "No folder selected.", italic=True, color=ft.Colors.GREY_500)

    # Log Container
    log_list = ft.ListView(expand=True, spacing=10,
                           padding=10, auto_scroll=True)
    log_container = ft.Container(
        content=log_list,
        border=ft.Border.all(1, ft.Colors.OUTLINE),
        border_radius=ft.BorderRadius.all(10),
        padding=10,
        expand=True,
    )

    def log_ui_message(msg: str, color: str = ft.Colors.WHITE):
        """Displays message on screen AND logs it to the file."""
        log_list.controls.append(ft.Text(msg, color=color))
        page.update()
        logger.debug(f"UI LOG: {msg}")

    # Start processing files
    async def start_processing(folder_path):
        logger.info(f"Processing folder: {folder_path}")
        selected_path_text.value = f"Selected: {folder_path}"
        page.update()

        log_list.controls.clear()
        log_ui_message(
            f"Starting process in: {folder_path}", ft.Colors.BLUE_200)

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
                        log_ui_message(
                            f"⏩ Skipped: '{filename}'", ft.Colors.GREY)
                        continue

                    if not os.path.exists(new_full_path):
                        try:
                            await asyncio.to_thread(os.rename, old_full_path, new_full_path)
                            log_ui_message(
                                f"✅ Success: '{filename}' -> '{new_filename}'", ft.Colors.GREEN_400)
                            logger.info(
                                f"Renamed: {filename} to {new_filename}")
                        except Exception as ex:
                            log_ui_message(
                                f"❌ Error renaming '{filename}': {ex}", ft.Colors.RED_400)
                            logger.error(f"Rename failed for {filename}: {ex}")
                    else:
                        log_ui_message(
                            f"⚠️ Warning: '{new_filename}' already exists.", ft.Colors.ORANGE_400)
                else:
                    log_ui_message(
                        f"ℹ️ Info: No <h1> found in '{filename}'.", ft.Colors.YELLOW_400)

            await asyncio.sleep(0)  # Keep UI responsive

        if not found_html:
            log_ui_message(
                "No .html files found in this folder.", ft.Colors.RED_400)

        log_ui_message("--- Process Finished ---", ft.Colors.BLUE_200)
        logger.info("Processing complete.")

    # FilePicker Handler
    async def on_dialog_result(e: ft.ControlEvent):
        logger.info("Flet FilePicker triggered on_result event.")
        if e.path:
            await start_processing(e.path)
        else:
            log_ui_message("Selection cancelled.", ft.Colors.RED_400)
            logger.info("User cancelled Flet FilePicker.")

    get_directory_dialog = ft.FilePicker()
    get_directory_dialog.on_result = on_dialog_result
    page.overlay.append(get_directory_dialog)

    # Main Button Click
    async def open_folder_picker(e):
        try:
            logger.info("Attempting to open Flet native FilePicker...")
            # We add a 0.1s wait just to make sure Flet has registered the overlay
            await asyncio.sleep(0.1)
            await get_directory_dialog.get_directory_path("Select Folder")
        except Exception as ex:
            # THIS CATCHES THE TIMEOUT ERROR!
            logger.error(f"Flet FilePicker Error (Timeout expected): {ex}")
            log_ui_message(
                "Flet Picker failed. Switching to Mac Native Picker...", ft.Colors.ORANGE_400)

            # Use AppleScript fallback running in a background thread to prevent GUI lock
            folder_path = await asyncio.to_thread(mac_native_folder_picker)
            if folder_path:
                await start_processing(folder_path)
            else:
                log_ui_message("Mac Native Picker cancelled.",
                               ft.Colors.RED_400)

    # Assemble the Page UI
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
        title_text, subtitle_text, ft.Divider(
            height=20, color=ft.Colors.TRANSPARENT),
        select_button, selected_path_text,
        ft.Text("Execution Logs:", weight=ft.FontWeight.W_500,
                color=ft.Colors.GREY_300),
        log_container
    )
    page.update()
    logger.info("UI Loaded Successfully.")

if __name__ == "__main__":
    try:
        ft.run(main)
    except Exception as fatal_e:
        logger.critical(f"FATAL CRASH: {fatal_e}", exc_info=True)
