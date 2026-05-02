# NTE Auto Fishing Script

Windows-only auto fishing helper for NTE. It uses screen capture plus simple color detection to identify the fishing prompt/bar, then sends keyboard and mouse input.

> This project is intended as a personal automation template and learning reference. Use it responsibly and check the rules or terms of service for any game or service you use it with.

## Features

- Automatically activates the game window by title.
- Detects the fishing prompt and fishing bar from the screen.
- Scales detection regions from the original `2560x1440` tuning to your current capture size.
- Press `F8` to stop safely.
- Configurable window title and capture FPS from the command line.

## Requirements

- Windows 10/11
- Python 3.10 or newer
- NTE running in a visible window
- Dependencies listed in `requirements.txt`

## Quick Start

```powershell
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python fishing_bot_release_v2.py
```

If your game window title is different:

```powershell
python fishing_bot_release_v2.py --window-title "NTE"
```

Lower capture FPS if your computer is under heavy load:

```powershell
python fishing_bot_release_v2.py --fps 30
```

## Controls

| Key | Action |
| --- | --- |
| `F8` | Stop the script |
| `Ctrl+C` | Stop from the terminal |

## Tuning

The default regions were tuned from a `2560x1440` layout:

- `BAR_REGION_REF`: fishing progress bar area
- `ICON_REGION_REF`: prompt/icon area
- `HOOK_REGION_REF`: hook prompt area

If detection is unreliable on your UI layout, adjust these constants in `fishing_bot_release_v2.py`:

```python
BAR_REGION_REF = (800, 70, 1770, 130)
ICON_REGION_REF = (REFERENCE_W - 750, REFERENCE_H - 220, REFERENCE_W - 100, REFERENCE_H - 40)
HOOK_REGION_REF = (REFERENCE_W - 280, REFERENCE_H - 220, REFERENCE_W - 100, REFERENCE_H - 40)
```

Color thresholds can also be tuned:

```python
YELLOW_LOWER = np.array([20, 80, 120])
YELLOW_UPPER = np.array([40, 255, 255])
GREEN_LOWER = np.array([45, 80, 80])
GREEN_UPPER = np.array([85, 255, 255])
STEP2_BLUE_THRESHOLD = 0.06
```

## Troubleshooting

### The script cannot find the game window

Run the script with the exact or partial window title:

```powershell
python fishing_bot_release_v2.py --window-title "Your Window Title"
```

### Nothing happens after starting

- Make sure the game window is visible and not minimized.
- Run PowerShell or your terminal as administrator if input is blocked.
- Check that your display scaling and game resolution are close to the expected UI layout.

### Detection is wrong on my resolution

The script scales from the reference `2560x1440` layout, but game UI position can still differ. Adjust the region constants listed in the tuning section.

## Project Structure

```text
.
├── fishing_bot_release_v2.py
├── requirements.txt
├── pyproject.toml
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
└── .gitignore
```

## Disclaimer

This repository is not affiliated with, endorsed by, or sponsored by NTE or its publishers. You are responsible for how you use this script.
