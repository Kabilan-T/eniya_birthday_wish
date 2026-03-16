#!/bin/bash
# Package animate.py into a standalone Windows executable via PyInstaller
# Run this on a Windows machine or via Wine/cross-compile setup

pyinstaller --onefile --noconsole animate.py
