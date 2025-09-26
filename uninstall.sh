#!/usr/bin/env bash

if [[ -n "$PREFIX" ]] && command -v pkg &>/dev/null; then
	INSTALL_DIR="$PREFIX/bin"
else
	INSTALL_DIR="/usr/local/bin"
fi

TARGET_COMMAND="ccg"
TARGET_PATH="$INSTALL_DIR/$TARGET_COMMAND"

echo "Uninstalling '$TARGET_COMMAND' from $INSTALL_DIR..."

if [[ -f "$TARGET_PATH" ]]; then
	if [[ ! -w "$TARGET_PATH" ]]; then
		echo "Administrator privileges are required to remove the command from $INSTALL_DIR."
		sudo rm "$TARGET_PATH"
	else
		rm "$TARGET_PATH"
	fi

	if [[ $? -eq 0 ]]; then
		echo "Uninstallation of '$TARGET_COMMAND' script from $INSTALL_DIR completed successfully!"
		echo "Note: This script does not uninstall dependencies (e.g., Python, Docker)."
		echo "Please remove them manually if they are no longer needed."
	else
		echo "Error: Failed to remove '$TARGET_COMMAND'. Please check permissions."
	fi
else
	echo "'$TARGET_COMMAND' is not installed in $INSTALL_DIR."
fi
