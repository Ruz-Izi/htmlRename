# ENGLISH COMMENT: This is the final runnable Flet app for macOS packaging.
# It removes tkinter entirely because tkinter is unavailable in packaged Flet apps.
# The app first tries Flet FilePicker, and if it fails, it falls back to native macOS AppleScript.
# This version is suitable for both development and macOS bundle packaging.

import flet as ft
import os
import re
import html
import asyncio
import logging
import subprocess

logging.basicConfig(
    filename="app_debug.log",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def mac_native_folder_picker():
    try:
        script = 'return POSIX path of (choose folder with prompt "Select Folder containing HTML files")'
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip() or None
        return None
    except Exception as error:
        logger.exception("AppleScript picker failed: %s", error)
        return None


def extract_first_heading_from_html(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as html_file:
            file_content = html_file.read()
            search_result = re.search(
                r"<h1[^>]*>(.*?)</h1>",
                file_content,
                re.IGNORECASE | re.DOTALL,
            )
            if search_result:
                raw_heading = search_result.group(1)
                text_without_tags = re.sub(r"<[^>]+>", "", raw_heading)
                decoded_text = html.unescape(text_without_tags)
                clean_text = " ".join(decoded_text.split())
                safe_filename = re.sub(r'[\\/*?:"<>|]', "", clean_text)
                if safe_filename:
                    return safe_filename[:60]
    except Exception as error:
        logger.exception("Failed reading file %s: %s", file_path, error)
    return None


async def main(page: ft.Page):
    page.title = "HTML Auto Renamer"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.window.width = 600
    page.window.height = 700
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    title_text = ft.Text(
        "HTML Renamer Tool",
        size=30,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_400,
    )
    subtitle_text = ft.Text(
        "Select a folder to rename HTML files based on their <h1> tag.",
        color=ft.Colors.GREY_400,
    )
    selected_path_text = ft.Text(
        "No folder selected.",
        italic=True,
        color=ft.Colors.GREY_500,
    )

    log_list = ft.ListView(expand=True, spacing=10,
                           padding=10, auto_scroll=True)
    log_container = ft.Container(
        content=log_list,
        border=ft.Border.all(1, ft.Colors.OUTLINE),
        border_radius=ft.BorderRadius.all(10),
        padding=10,
        expand=True,
    )

    def log_ui_message(message: str, color=ft.Colors.WHITE):
        log_list.controls.append(ft.Text(message, color=color))
        page.update()
        logger.info(message)

    async def start_processing(folder_path: str):
        selected_path_text.value = f"Selected: {folder_path}"
        page.update()

        log_list.controls.clear()
        log_ui_message(
            f"Starting process in: {folder_path}", ft.Colors.BLUE_200)

        found_html = False

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".html"):
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
                        await asyncio.sleep(0)
                        continue

                    if not os.path.exists(new_full_path):
                        try:
                            await asyncio.to_thread(os.rename, old_full_path, new_full_path)
                            log_ui_message(
                                f"✅ Success: '{filename}' -> '{new_filename}'",
                                ft.Colors.GREEN_400,
                            )
                        except Exception as error:
                            log_ui_message(
                                f"❌ Error renaming '{filename}': {error}",
                                ft.Colors.RED_400,
                            )
                    else:
                        log_ui_message(
                            f"⚠️ Warning: '{new_filename}' already exists.",
                            ft.Colors.ORANGE_400,
                        )
                else:
                    log_ui_message(
                        f"ℹ️ Info: No valid <h1> found in '{filename}'.",
                        ft.Colors.YELLOW_400,
                    )

            await asyncio.sleep(0)

        if not found_html:
            log_ui_message(
                "No .html files found in this folder.", ft.Colors.RED_400)

        log_ui_message("--- Process Finished ---", ft.Colors.BLUE_200)

    async def on_dialog_result(e: ft.ControlEvent):
        if e.path:
            await start_processing(e.path)
        else:
            log_ui_message("Selection cancelled.", ft.Colors.RED_400)

    file_picker = ft.FilePicker()
    file_picker.on_result = on_dialog_result
    page.overlay.append(file_picker)

    async def open_folder_picker(e):
        try:
            await file_picker.get_directory_path(dialog_title="Select Folder")
        except Exception as error:
            logger.exception("Flet picker failed: %s", error)
            log_ui_message(
                "Flet Picker failed. Switching to Mac Native Picker...",
                ft.Colors.ORANGE_400,
            )
            folder_path = await asyncio.to_thread(mac_native_folder_picker)
            if folder_path:
                await start_processing(folder_path)
            else:
                log_ui_message("Mac Native Picker cancelled.",
                               ft.Colors.RED_400)

    select_button = ft.Button(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.FOLDER_OPEN, color=ft.Colors.WHITE),
                ft.Text("Select Folder & Start", color=ft.Colors.WHITE),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        on_click=open_folder_picker,
        bgcolor=ft.Colors.BLUE_700,
    )

    page.add(
        title_text,
        subtitle_text,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        select_button,
        selected_path_text,
        ft.Text(
            "Execution Logs:",
            weight=ft.FontWeight.W_500,
            color=ft.Colors.GREY_300,
        ),
        log_container,
    )
    page.update()


if __name__ == "__main__":
    ft.run(main)
