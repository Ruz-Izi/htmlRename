# ENGLISH COMMENT: This command sequence installs CocoaPods on macOS, verifies it,
# refreshes Flutter doctor, and then retries the Flet macOS build in a clean way.

brew install cocoapods
pod --version
flutter doctor
cd /Users/ruzmac16/Downloads/HtmlRename
flet build macos --verbose
