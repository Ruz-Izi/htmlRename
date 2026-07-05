# ENGLISH COMMENT EXPLAINING THE ENTIRE SCRIPT:
# This script contains the native 'flet build' commands to package your Python application
# for various operating systems and platforms (macOS, Web, Android, iOS, Windows, Linux).
# Flet uses the Flutter SDK under the hood to compile the application natively.
# Make sure you are in the same directory as your 'fletApp.py' before running these.

# 1. Build for macOS (Creates an Apple Application Bundle: .app)
# This will output a folder in 'build/macos/' containing your native Mac app.
flet build macos

# 2. Build for Web (Creates a Static Website: HTML, CSS, JS, WebAssembly)
# This outputs a 'build/web/' folder that you can host on GitHub Pages or any web server.
flet build web

# 3. Build for Android (Creates an Android Package Kit: .apk or .aab)
# Note: Requires Android Studio and Android SDK (Software Development Kit) to be installed.
flet build apk

# 4. Build for iOS (Creates an iOS App Store Package: .ipa)
# Note: Requires macOS and Apple's Xcode installed on your machine.
flet build ipa

# 5. Build for Windows (Creates a Windows Executable: .exe)
# Note: It is highly recommended to run this command ON a Windows computer.
# Cross-compiling Windows apps on a Mac can be very complex.
flet build windows

# 6. Build for Linux (Creates a Linux executable binary)
# Note: Best executed on a Linux machine (like Ubuntu).
flet build linux
