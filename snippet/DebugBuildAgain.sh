# ENGLISH COMMENT EXPLAINING THE SCRIPT:
# This script diagnoses and resolves the silent hang during "Building macOS bundle...".
# First, it auto-accepts the Apple Xcode license, which is a common cause for silent hangs
# when CLI tools wait for user input that is hidden by Flet's loading spinner.
# Then, we run the Flet build command with the '--verbose' flag.
# This flag disables the spinner and prints the raw, underlying Flutter and Xcode compilation logs
# directly to the terminal, allowing us to see exactly where and why the build is pausing.

# Step 1: Force accept the Apple Xcode developer license (requires Mac password)
sudo xcodebuild -license accept

# Step 2: Make sure you are in your project directory
cd /Users/ruzmac16/Downloads/HtmlRename

# Step 3: Run the build command in VERBOSE mode to see all hidden logs
flet build macos --verbose
