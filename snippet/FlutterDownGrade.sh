# ENGLISH COMMENT EXPLAINING THE ENTIRE SCRIPT:
# Flet 0.85.3 strictly requires Flutter SDK version 3.41.7 for API compatibility.
# Your local Flutter SDK is version 3.44.1, which caused Flet to reject it.
# Since the Flutter SDK is a Git repository, we can efficiently "time travel"
# (downgrade) to the exact required version using the 'git checkout' command.
# This prevents downloading the entire SDK again.

# Step 1: Navigate inside your installed Flutter directory
cd /Users/ruzmac16/PackegesInstalled/flutter

# Step 2: Tell Git to switch the files to version 3.41.7
git checkout 3.41.7

# Step 3: Run flutter version command so it syncs its internal Dart SDK to the new version
flutter --version

# Step 4: Navigate back to your Python project directory
cd /Users/ruzmac16/Downloads/HtmlRename

# Step 5: Run the Flet build command again. It will now accept your local Flutter SDK!
flet build macos
