# Foundry Monitor Mirror

**FR :** Cet outil est principalement destiné à être utilisé pour Foundry VTT lors de sessions en personne, particulièrement lorsque vous utilisez une télévision comme table de jeu et que vous êtes positionné de manière inversée ou latérale par rapport à l'écran. Il permet de mirrorer un second moniteur dans une fenêtre tout en gardant le contrôle de la souris, facilitant ainsi la gestion de l'affichage pour le MJ et les joueurs.

A high-performance Windows utility to mirror a second monitor into a window and control it with your mouse. Designed for low-latency interactions using DXGI Desktop Duplication.

## Features

- **High-Performance Capture**: Uses `DXCAM` (DXGI) for near-zero latency and 60 FPS support.
- **Auto-Fallback**: Automatically switches to `MSS` if hardware-accelerated capture is unavailable.
- **Mouse Control**: Pass clicks, right-clicks, and drags to the target monitor.
- **Cursor Mirroring**: See your real-time mouse position in the mirror window.
- **Debug Logs**: Built-in console logging and FPS counter for performance monitoring.

## Setup Instructions

### 1. Prerequisites
- Windows 10 or 11.
- Python 3.10 or higher.
- A GPU that supports DXGI (most modern Intel/NVIDIA/AMD GPUs).

### 2. Install Dependencies
Open your terminal and run:
```bash
pip install -r requirements.txt
```

### 3. Run from Source
```bash
python monitor_mirror.py
```

### 4. Build Executable
To create a standalone `.exe` (found in the `dist` folder):
```bash
python build_exe.py
```

## Troubleshooting

- **Admin Privileges**: If you need to control applications running as Administrator (like Task Manager), you must run `MonitorMirror.exe` as Administrator.
- **Black Screen / Initialize Stuck**: Check the console for logs. The app will attempt to iterate through available GPU devices (0, 1, 2). If all fail, it will fall back to `MSS (Compatibility Mode)`.
- **Performance**: If you aren't hitting 60 FPS, check if you are in "DXCAM" mode in the window title.
