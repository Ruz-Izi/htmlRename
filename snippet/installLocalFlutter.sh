# ENGLISH COMMENT EXPLAINING THE SCRIPT:
# This sets the global PATH to include your local Flutter SDK so 'flet' doesn't try to download it.
# It also uses the FLET_CLI_SKIP_FLUTTER_DOCTOR environment variable to prevent Flet
# from failing if 'flutter doctor' encounters network timeouts or complains about missing tools.

# 1. Add your local Flutter SDK to the system PATH.
# REPLACE '/Users/ruzmac16/Downloads/flutter' with the actual path where you extracted Flutter!
export PATH="/Users/ruzmac16/PackegesInstalled/flutter/bin:$PATH"

# 2. Tell Flet to skip the aggressive 'flutter doctor' diagnostic checks,
# which usually fail without a perfect internet connection.
export FLET_CLI_SKIP_FLUTTER_DOCTOR=true
