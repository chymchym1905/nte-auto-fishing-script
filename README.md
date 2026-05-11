# NTE Auto Fishing Script

Windows-only auto fishing helper for NTE. The script captures the game window, detects a few UI colors, and sends `F`, mouse click, `A`, and `D` input based on the current fishing state.

> This project is a personal automation tool and learning reference. Use it at your own risk and verify that your usage complies with the game's rules or terms of service.

## &#20013;&#25991;&#35498;&#26126;

&#36889;&#26159;&#19968;&#20491;&#32102;&#12298;&#30064;&#29872;&#12299;&#65288;NTE&#65289;&#20351;&#29992;&#30340;&#33258;&#21205;&#37347;&#39770;&#36628;&#21161;&#31243;&#24335;&#12290;&#23427;&#26371;&#36879;&#36942;&#34722;&#24149;&#25847;&#21462;&#33287;&#38991;&#33394;&#36776;&#35672;&#65292;&#21028;&#26039;&#37347;&#39770;&#25552;&#31034;&#12289;&#25289;&#31487;&#26178;&#27231;&#33287;&#37347;&#39770;&#26781;&#29376;&#24907;&#65292;&#20877;&#33258;&#21205;&#36865;&#20986;&#28369;&#40736;&#40670;&#25802;&#33287;&#37749;&#30436;&#36664;&#20837;&#12290;

&#20027;&#35201;&#29305;&#40670;&#65306;

- &#33258;&#21205;&#20999;&#25563;&#21040;&#36938;&#25138;&#35222;&#31383;&#24460;&#38283;&#22987;&#25805;&#20316;&#12290;
- &#20381;&#29031;&#37347;&#39770;&#27969;&#31243;&#20998;&#25104;&#38283;&#22987;&#12289;&#25289;&#37390;&#12289;&#23565;&#25239;&#12289;&#25910;&#23614;&#22235;&#20491;&#38542;&#27573;&#12290;
- &#25903;&#25588;&#20839;&#24314; `1080p` &#33287; `2k` &#38928;&#35373;&#65292;&#26371;&#20808;&#33258;&#21205;&#20597;&#28204;&#36938;&#25138;&#35222;&#31383;&#35299;&#26512;&#24230;&#65292;&#20877;&#20381;&#29031;&#23526;&#38555;&#35222;&#31383;&#22823;&#23567;&#32302;&#25918;&#20597;&#28204;&#21312;&#22495;&#12290;
- &#21487;&#36664;&#20986;&#38500;&#37679;&#25130;&#22294;&#21040; `debug_frames/`&#65292;&#26041;&#20415;&#35519;&#25972;&#21312;&#22495;&#33287;&#38991;&#33394;&#38272;&#27385;&#12290;
- &#21487;&#36879;&#36942; `F8` &#23433;&#20840;&#20572;&#27490;&#12290;

&#23433;&#35037;&#26041;&#24335;&#65306;

```powershell
git clone https://github.com/chymchym1905/nte-auto-fishing-script.git
cd nte-auto-fishing-script
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

&#22519;&#34892;&#26041;&#24335;&#65306;

```powershell
python nte_auto_fishing.py
run.bat
```

&#22914;&#26524;&#35201;&#20351;&#29992;&#25171;&#21253;&#22909;&#30340;&#22519;&#34892;&#27284;&#65306;

```powershell
.\dist\autofish.exe
```

&#24120;&#29992;&#21443;&#25976;&#65306;

- &#40664;&#35469;&#26371;&#33258;&#21205;&#20381;&#35222;&#31383;&#35299;&#26512;&#24230;&#36984;&#25799;&#38928;&#35373;
- `--preset 1080p` &#25110; `-fhd`
- `--preset 2k` &#25110; `-2k`
- `--window-title "NTE"`
- `--process-name "HTGame.exe"`
- `--fps 30`
- `--debug-frames`

&#35519;&#25972;&#24314;&#35696;&#65306;

- &#22914;&#26524;&#20597;&#28204;&#20301;&#32622;&#19981;&#23565;&#65292;&#20808;&#20462;&#25913; `PRESETS` &#20839;&#30340; `bar_region`&#12289;`icon_region`&#12289;`hook_region`&#12290;
- &#22914;&#26524;&#20301;&#32622;&#27491;&#30906;&#20294;&#21028;&#26039;&#19981;&#31337;&#65292;&#20877;&#24494;&#35519; `YELLOW_*`&#12289;`GREEN_*` &#33287; `STEP2_BLUE_THRESHOLD`&#12290;
- &#36935;&#21040;&#36938;&#25138;&#35222;&#31383;&#25214;&#19981;&#21040;&#12289;&#36664;&#20837;&#27794;&#21453;&#25033;&#25110;&#25289;&#26781;&#19981;&#28310;&#65292;&#20778;&#20808;&#27298;&#26597;&#35222;&#31383;&#26159;&#21542;&#21487;&#35211;&#12289;&#35299;&#26512;&#24230;&#26159;&#21542;&#21512;&#36969;&#65292;&#20197;&#21450;&#38500;&#37679;&#25130;&#22294;&#35041;&#30340;&#20597;&#28204;&#26694;&#26159;&#21542;&#33995;&#21040;&#27491;&#30906; UI&#12290;

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
- Supports built-in `2k` and `1080p` presets with automatic selection based on the game client size.
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
git clone https://github.com/chymchym1905/nte-auto-fishing-script.git
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
- Starts the script with automatic preset detection.

## Build EXE

Install the build dependency and package the script:

```powershell
.\.venv\Scripts\python.exe -m pip install .[build]
.\build.ps1
```

Build output:

- `dist\autofish.exe`

The build script currently creates a single-file console EXE with PyInstaller.
It also converts `images\mlem.png` into the Windows icon used by `autofish.exe`.

## Run EXE

```powershell
.\dist\autofish.exe
```

Automatic preset selection:

- `<= 1920x1080`: uses the `1080p` preset
- `> 1920x1080` and `<= 2560x1440`: uses the `2k` preset
- `> 2560x1440`: falls back to the `2k` preset because it is the largest built-in preset

Manual preset shortcuts:

- `-fhd`: uses the `1080p` preset
- `-2k`: uses the `2k` preset

The original Python flags still work:

```powershell
python nte_auto_fishing.py --preset 1080p
python nte_auto_fishing.py --preset 2k
.\dist\autofish.exe --preset 1080p
.\dist\autofish.exe --preset 2k
```

## Command Line Options

```powershell
python nte_auto_fishing.py --preset 1080p
python nte_auto_fishing.py -fhd
python nte_auto_fishing.py -2k
python nte_auto_fishing.py --window-title "NTE"
python nte_auto_fishing.py --process-name "HTGame.exe"
python nte_auto_fishing.py --fps 30
python nte_auto_fishing.py --debug-frames
```

Available arguments:

- `--preset`: optional manual override, `2k` or `1080p`
- `-fhd`: shortcut for `--preset 1080p`
- `-2k`: shortcut for `--preset 2k`
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
