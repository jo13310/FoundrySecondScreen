import PyInstaller.__main__
import os

# Define the script to bundle
script_path = "monitor_mirror.py"

# Run PyInstaller
PyInstaller.__main__.run([
    script_path,
    '--onefile',
    '--console',
    '--name=MonitorMirror',
    '--clean'
])
