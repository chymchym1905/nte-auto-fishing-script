# NTE Auto Fishing Script

Windows-only auto fishing helper for NTE. The script captures the game window, detects a few UI colors, and sends `F`, mouse click, `A`, and `D` input based on the current fishing state.

> This project is a personal automation tool and learning reference. Use it at your own risk and verify that your usage complies with the game's rules or terms of service.

## Current Script State

The current script is built around a simple state machine:

1. `STEP1_WAIT_START`
   Clicks the center of the game window, then presses `F` to start or interact.
2. `STEP2_TRIGGER`
   Waits for the blue hook prompt and presses `F` again when detected.
3. `STEP3_FIGHTING`
   Tracks the yellow marker and green safe zone in the fishing bar, then taps `A` or `D` to keep them aligned.
4. `STEP4_FINISH`
   Clicks once after the bar disappears, then resets to step 1.

Detection is based on:

- A blue ratio inside `HOOK_REGION` for the hook prompt.
- Yellow and green HSV masks inside `BAR_REGION` for the fishing bar.
- Resolution presets that are scaled to the actual captured client area.

## Features

- Activates the NTE game window before starting.
- Prefers windows from `HTGame.exe` by default when multiple matching titles exist.
- Supports built-in `2k` and `1080p` presets.
- Scales detection regions to the actual game client size.
- Optional debug frame dump with annotated regions.
- Safe stop with `F8`.

## Requirements

- Windows 10/11
- Python 3.10+
- NTE running in a visible, non-minimized window
- Dependencies from `requirements.txt`

## Install

```powershell
git clone https://github.com/kakko-jia/nte-auto-fishing-script.git
cd nte-auto-fishing-script
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

Default run:

```powershell
python nte_auto_fishing.py
```

Use the included batch file:

```powershell
run.bat
```

Current `run.bat` behavior:

- Requests administrator elevation.
- Uses `.venv\Scripts\python.exe`.
- Starts the script with `--preset 1080p`.

## Command Line Options

```powershell
python nte_auto_fishing.py --preset 1080p
python nte_auto_fishing.py --window-title "NTE"
python nte_auto_fishing.py --process-name "HTGame.exe"
python nte_auto_fishing.py --fps 30
python nte_auto_fishing.py --debug-frames
```

Available arguments:

- `--preset`: `2k` or `1080p`
- `--window-title`: title keyword used to find the game window
- `--process-name`: preferred process name when ranking matching windows
- `--fps`: target capture FPS
- `--debug-frames`: saves up to 200 annotated frames into `debug_frames/`

## Controls

| Key | Action |
| --- | --- |
| `F8` | Stop the script |
| `Ctrl+C` | Stop from terminal |

## Presets And Regions

The script uses reference layouts, then scales them to the actual window client area.

Current preset values:

```python
PRESETS = {
    "2k": {
        "reference_size": (2560, 1440),
        "bar_region": (800, 70, 1770, 130),
        "icon_region": (2560 - 750, 1440 - 220, 2560 - 100, 1440 - 40),
        "hook_region": (2560 - 280, 1440 - 220, 2560 - 100, 1440 - 40),
    },
    "1080p": {
        "reference_size": (1920, 1080),
        "bar_region": (600, 55, 1330, 95),
        "icon_region": (1920 - 562, 1080 - 165, 1920 - 75, 1080 - 30),
        "hook_region": (1920 - 210, 1080 - 165, 1920 - 75, 1080 - 30),
    },
}
```

If the script is looking in the wrong place, fix the preset regions first. Only tune color thresholds after the regions are correct.

## How To Tweak Color Threshold

The script currently uses these thresholds:

```python
YELLOW_LOWER = np.array([20, 80, 120])
YELLOW_UPPER = np.array([40, 255, 255])
GREEN_LOWER = np.array([45, 80, 80])
GREEN_UPPER = np.array([85, 255, 255])
STEP2_BLUE_THRESHOLD = 0.06
```

What they mean:

- `YELLOW_*`: finds the yellow moving marker in the fishing bar
- `GREEN_*`: finds the green safe zone in the fishing bar
- `STEP2_BLUE_THRESHOLD`: minimum blue-pixel ratio in `HOOK_REGION` before the script treats it as the hook prompt

Recommended tuning workflow:

1. Run with `--debug-frames`.
2. Trigger fishing in-game.
3. Open images from `debug_frames/` and confirm that `bar_region` and `hook_region` cover the correct UI.
4. If regions are wrong, edit `PRESETS` first.
5. If regions are correct but detection is unstable, adjust HSV bounds in small steps.

Practical tuning rules:

- If yellow is not detected, widen `YELLOW_LOWER[0]` downward or `YELLOW_UPPER[0]` upward a little.
- If too many non-yellow pixels are matched, raise saturation/value minimums such as `YELLOW_LOWER[1]` or `YELLOW_LOWER[2]`.
- If green is missed, widen the green hue range a little.
- If the hook step triggers too easily, increase `STEP2_BLUE_THRESHOLD`.
- If the hook step never triggers even though the blue prompt is visible, decrease `STEP2_BLUE_THRESHOLD`.

Example of a slightly wider yellow range:

```python
YELLOW_LOWER = np.array([18, 70, 110])
YELLOW_UPPER = np.array([44, 255, 255])
```

Example of a stricter blue prompt check:

```python
STEP2_BLUE_THRESHOLD = 0.08
```

Edit those constants in [nte_auto_fishing.py](/d:/Software/nte-auto-fishing-script/nte_auto_fishing.py).

## Troubleshooting

### Script cannot find the game window

Try a broader title match:

```powershell
python nte_auto_fishing.py --window-title "NTE"
```

If there are multiple matching windows, keep `--process-name "HTGame.exe"` or set the correct process name explicitly.

### Script starts but does nothing useful

- Make sure the game window is visible and not minimized.
- Run the terminal as administrator if the game blocks synthetic input.
- Check that your preset matches your layout.
- Use `--debug-frames` to verify the capture regions.

### Fishing bar control is inaccurate

- Confirm `BAR_REGION` is correct for your UI.
- Tune `YELLOW_*` and `GREEN_*` only after the region is correct.
- Lighting effects, post-processing, or UI changes can require new HSV bounds.

## Files

```text
.
|-- nte_auto_fishing.py
|-- requirements.txt
|-- run.bat
`-- README.md
```

## Disclaimer

This repository is not affiliated with, endorsed by, or sponsored by NTE or its publishers. You are responsible for how you use this script.
