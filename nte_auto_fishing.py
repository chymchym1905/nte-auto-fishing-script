import argparse
import ctypes
import time
from pathlib import Path

import cv2
import dxcam
import numpy as np
import pydirectinput
import pygetwindow as gw
from pygetwindow import PyGetWindowException


# Detection presets are reference layouts that get scaled to the capture size.
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

ACTIVE_PRESET = "2k"
REFERENCE_W, REFERENCE_H = PRESETS[ACTIVE_PRESET]["reference_size"]

SCREEN_W = REFERENCE_W
SCREEN_H = REFERENCE_H

BAR_REGION_REF = PRESETS[ACTIVE_PRESET]["bar_region"]
ICON_REGION_REF = PRESETS[ACTIVE_PRESET]["icon_region"]
HOOK_REGION_REF = PRESETS[ACTIVE_PRESET]["hook_region"]

BAR_REGION = BAR_REGION_REF
ICON_REGION = ICON_REGION_REF
HOOK_REGION = HOOK_REGION_REF

YELLOW_LOWER = np.array([20, 80, 120])
YELLOW_UPPER = np.array([40, 255, 255])
GREEN_LOWER = np.array([80, 140, 120])
GREEN_UPPER = np.array([92, 255, 255])

STEP2_BLUE_THRESHOLD = 0.06

TIMEOUT = {
    "STEP1_WAIT_START": 10,
    "STEP2_WAIT_HOOK": 30,
    "STEP3_FIGHTING": 60,
}

SLEEP = {
    "STEP1_WAIT_START": 0.3,
    "STEP2_WAIT_HOOK": 0.1,
    "STEP2_TRIGGER": 0.1,
    "STEP3_FIGHTING": 0.02,
    "STEP4_FINISH": 0.1,
}

REENTER_CURRENT_STATE = "__REENTER_CURRENT_STATE__"
STOP_KEY = 0x77  # F8
DEFAULT_PROCESS_NAME = "HTGame.exe"

CAPTURE_LEFT = 0
CAPTURE_TOP = 0
DEBUG_FRAME_DIR = Path("debug_frames")
DEBUG_FRAME_LIMIT = 200


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


SW_RESTORE = 9
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def scale_region(region, width, height):
    x1, y1, x2, y2 = region
    sx = width / REFERENCE_W
    sy = height / REFERENCE_H
    return (
        int(round(x1 * sx)),
        int(round(y1 * sy)),
        int(round(x2 * sx)),
        int(round(y2 * sy)),
    )


def configure_preset(name):
    global ACTIVE_PRESET, REFERENCE_W, REFERENCE_H, BAR_REGION_REF, ICON_REGION_REF, HOOK_REGION_REF

    preset = PRESETS[name]
    ACTIVE_PRESET = name
    REFERENCE_W, REFERENCE_H = preset["reference_size"]
    BAR_REGION_REF = preset["bar_region"]
    ICON_REGION_REF = preset["icon_region"]
    HOOK_REGION_REF = preset["hook_region"]

    print(f"Using preset: {ACTIVE_PRESET} ({REFERENCE_W}x{REFERENCE_H})")


def detect_preset(width, height):
    fhd_width, fhd_height = PRESETS["1080p"]["reference_size"]
    two_k_width, two_k_height = PRESETS["2k"]["reference_size"]
    if width <= fhd_width and height <= fhd_height:
        return "1080p"
    if width <= two_k_width and height <= two_k_height:
        return "2k"
    return "2k"


def configure_screen(width, height):
    global SCREEN_W, SCREEN_H, BAR_REGION, ICON_REGION, HOOK_REGION

    SCREEN_W = width
    SCREEN_H = height
    BAR_REGION = scale_region(BAR_REGION_REF, width, height)
    ICON_REGION = scale_region(ICON_REGION_REF, width, height)
    HOOK_REGION = scale_region(HOOK_REGION_REF, width, height)

    print(f"Detected capture size: {SCREEN_W}x{SCREEN_H}")
    print(f"BAR_REGION={BAR_REGION}")
    print(f"ICON_REGION={ICON_REGION}")
    print(f"HOOK_REGION={HOOK_REGION}")


def configure_capture_origin(left, top):
    global CAPTURE_LEFT, CAPTURE_TOP

    CAPTURE_LEFT = left
    CAPTURE_TOP = top

    print(f"Capture origin: ({CAPTURE_LEFT}, {CAPTURE_TOP})")


def get_window_client_region(window):
    hwnd = window._hWnd
    rect = RECT()
    if not ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect)):
        raise ctypes.WinError()

    top_left = POINT(rect.left, rect.top)
    bottom_right = POINT(rect.right, rect.bottom)
    if not ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(top_left)):
        raise ctypes.WinError()
    if not ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(bottom_right)):
        raise ctypes.WinError()

    return (
        top_left.x,
        top_left.y,
        bottom_right.x,
        bottom_right.y,
    )


def get_window_capture_region(window):
    return get_window_client_region(window)


def get_window_process_name(window):
    pid = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(window._hWnd, ctypes.byref(pid))
    if not pid.value:
        return None

    handle = ctypes.windll.kernel32.OpenProcess(
        PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value
    )
    if not handle:
        return None

    try:
        size = ctypes.c_ulong(260)
        buffer = ctypes.create_unicode_buffer(size.value)
        ok = ctypes.windll.kernel32.QueryFullProcessImageNameW(
            handle, 0, buffer, ctypes.byref(size)
        )
        if not ok:
            return None
        return Path(buffer.value).name
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


def find_game_window(title="NTE", process_name=DEFAULT_PROCESS_NAME):
    normalized_title = title.casefold()
    normalized_process_name = process_name.casefold() if process_name else None
    candidates = []
    for window in gw.getAllWindows():
        window_title = (window.title or "").strip()
        if not window_title or normalized_title not in window_title.casefold():
            continue
        if window.width <= 0 or window.height <= 0 or window.isMinimized:
            continue

        lowered = window_title.casefold()
        if lowered == normalized_title:
            match_rank = 3
        elif lowered.startswith(normalized_title):
            match_rank = 2
        else:
            match_rank = 1

        process_rank = 0
        process_label = get_window_process_name(window)
        if normalized_process_name and process_label:
            process_rank = int(process_label.casefold() == normalized_process_name)

        area = window.width * window.height
        candidates.append(((process_rank, match_rank, area), window))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def activate_game_window(title="NTE", process_name=DEFAULT_PROCESS_NAME):
    window = find_game_window(title, process_name=process_name)
    if not window:
        raise RuntimeError(
            f"Could not find a visible window matching title {title!r}"
            f" and process {process_name!r}."
        )

    hwnd = window._hWnd
    if window.isMinimized:
        ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
        time.sleep(0.5)

    try:
        window.activate()
    except PyGetWindowException:
        ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
        ctypes.windll.user32.BringWindowToTop(hwnd)
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        ctypes.windll.user32.SetActiveWindow(hwnd)
        ctypes.windll.user32.SetFocus(hwnd)

    print(f"Activated window: {window.title}")
    time.sleep(1)
    return window


def press_f():
    pydirectinput.keyDown("f")
    time.sleep(0.05)
    pydirectinput.keyUp("f")
    print(">>> Press F")


def should_stop():
    return ctypes.windll.user32.GetAsyncKeyState(STOP_KEY) & 0x8000


def release_keys():
    for key in ("a", "d", "f"):
        pydirectinput.keyUp(key)


def tap_fight_key(key):
    pydirectinput.keyDown(key)
    time.sleep(0.01)
    pydirectinput.keyUp(key)


def click_screen():
    pydirectinput.click(CAPTURE_LEFT + SCREEN_W // 2, CAPTURE_TOP + SCREEN_H // 2)
    print(">>> Click center")


def draw_region(image, label, region, color):
    x1, y1, x2, y2 = region
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
    cv2.putText(
        image,
        label,
        (x1, max(24, y1 - 8)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2,
        cv2.LINE_AA,
    )


def log_debug_frame(frame, state, frame_index):
    annotated = frame.copy()
    draw_region(annotated, "bar_region", BAR_REGION, (0, 255, 255))
    draw_region(annotated, "icon_region", ICON_REGION, (0, 255, 0))
    draw_region(annotated, "hook_region", HOOK_REGION, (255, 200, 0))
    green_ratio = get_green_ratio(frame)
    yellow_ratio = get_yellow_ratio(frame)
    cv2.putText(
        annotated,
        f"state={state}",
        (20, 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        annotated,
        f"green_ratio={green_ratio:.4f} | yellow_ratio={yellow_ratio:.4f}",
        (20, 68),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    DEBUG_FRAME_DIR.mkdir(exist_ok=True)
    output_path = DEBUG_FRAME_DIR / f"{frame_index:04d}_{state}.png"
    cv2.imwrite(str(output_path), annotated)


def crop_region(frame, region):
    x1, y1, x2, y2 = region
    return frame[y1:y2, x1:x2]


def get_color_ratio(frame, region, lower, upper):
    area = crop_region(frame, region)
    if area.size == 0:
        return 0

    hsv = cv2.cvtColor(area, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    return cv2.countNonZero(mask) / (area.shape[0] * area.shape[1])


def get_blue_ratio(frame):
    return get_color_ratio(
        frame,
        HOOK_REGION,
        np.array([100, 120, 120]),
        np.array([130, 255, 255]),
    )


def has_step2_prompt(frame):
    return get_blue_ratio(frame) > STEP2_BLUE_THRESHOLD


def get_yellow_ratio(frame):
    return get_color_ratio(frame, BAR_REGION, YELLOW_LOWER, YELLOW_UPPER)


def get_green_ratio(frame):
    return get_color_ratio(frame, BAR_REGION, GREEN_LOWER, GREEN_UPPER)


def has_step3_bar(frame):
    green_ratio = get_green_ratio(frame)    
    yellow_ratio = get_yellow_ratio(frame)
    return green_ratio > 0.03 or (green_ratio > 0.015 and yellow_ratio > 0.001)


def find_yellow_x(frame):
    bar = crop_region(frame, BAR_REGION)
    hsv = cv2.cvtColor(bar, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, YELLOW_LOWER, YELLOW_UPPER)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    x, _, w, _ = cv2.boundingRect(max(contours, key=cv2.contourArea))
    return x + w // 2


def find_green_center_x(frame):
    bar = crop_region(frame, BAR_REGION)
    hsv = cv2.cvtColor(bar, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)
    _, xs = np.where(mask > 0)
    if len(xs) == 0:
        return None

    return (int(xs.min()) + int(xs.max())) // 2


def on_enter(state):
    print(f"\n{'=' * 50}")
    print(f"Enter state: {state}")
    print(f"{'=' * 50}")

    if state == "STEP1_WAIT_START":
        time.sleep(0.3)
        click_screen()
        time.sleep(0.2)
        press_f()
    elif state == "STEP2_TRIGGER":
        press_f()
    elif state == "STEP4_FINISH":
        time.sleep(0.5)
        click_screen()


def run_step1(frame, state_start):
    if time.time() - state_start > TIMEOUT["STEP1_WAIT_START"]:
        print("STEP1 timeout, retry")
        return REENTER_CURRENT_STATE

    if has_step2_prompt(frame):
        return "STEP2_TRIGGER"

    if has_step3_bar(frame):
        return "STEP3_FIGHTING"

    return "STEP1_WAIT_START"

def run_step2_wait(frame, state_start):
    if time.time() - state_start > TIMEOUT["STEP2_WAIT_HOOK"]:
        print("STEP2 timeout, back to STEP1")
        return "STEP1_WAIT_START"

    if has_step2_prompt(frame):
        return "STEP2_TRIGGER"

    if has_step3_bar(frame):
        return "STEP3_FIGHTING"

    return "STEP2_WAIT_HOOK"

def run_step2_trigger(frame, state_start):
    if has_step3_bar(frame):
        return "STEP3_FIGHTING"

    if time.time() - state_start > 3:
        print("STEP2_TRIGGER timeout")
        return "STEP1_WAIT_START"

    return "STEP2_TRIGGER"


def run_step3(frame, state_start):
    if time.time() - state_start > TIMEOUT["STEP3_FIGHTING"]:
        print("STEP3 timeout, back to STEP1")
        return "STEP1_WAIT_START"

    if get_green_ratio(frame) < 0.02:
        print("Fishing bar disappeared, finish")
        return "STEP4_FINISH"

    yellow_x = find_yellow_x(frame)
    green_x = find_green_center_x(frame)

    if yellow_x is not None and green_x is not None:
        diff = yellow_x - green_x
        print(f"yellow={yellow_x} | green={green_x} | diff={diff}")
        if diff < -10:
            tap_fight_key("d")
        elif diff > 10:
            tap_fight_key("a")

    return "STEP3_FIGHTING"


def run_step4(frame, state_start):
    if time.time() - state_start > 1.0:
        return "STEP1_WAIT_START"

    return "STEP4_FINISH"


def run_bot(
    window_title="NTE",
    target_fps=60,
    preset=None,
    debug_frames=False,
    process_name=DEFAULT_PROCESS_NAME,
):
    window = activate_game_window(window_title, process_name=process_name)

    left, top, right, bottom = get_window_capture_region(window)
    width = right - left
    height = bottom - top

    selected_preset = preset or detect_preset(width, height)
    if preset is None:
        print(f"Auto-selected preset: {selected_preset} for client size {width}x{height}")
    else:
        print(f"Using manual preset override: {selected_preset}")

    configure_preset(selected_preset)
    configure_capture_origin(left, top)
    configure_screen(width, height)

    camera = dxcam.create(
        device_idx=0,
        output_idx=0,
        region=(left, top, right, bottom),
        output_color="BGR",
    )
    camera.start(target_fps=target_fps)

    print("Auto fishing started. Press F8 or Ctrl+C to stop.")
    print("-" * 50)

    current_state = "STEP1_WAIT_START"
    state_start = time.time()
    first_frame_seen = False
    debug_frame_count = 0
    on_enter(current_state)

    try:
        while True:
            if should_stop():
                print("F8 pressed, stopping")
                break

            frame = camera.get_latest_frame()
            if frame is None:
                continue

            if not first_frame_seen:
                frame_h, frame_w = frame.shape[:2]
                if frame_w != SCREEN_W or frame_h != SCREEN_H:
                    configure_screen(frame_w, frame_h)
                first_frame_seen = True
                if debug_frames:
                    print(f"Debug frames will be written to: {DEBUG_FRAME_DIR.resolve()}")

            if debug_frames and first_frame_seen and debug_frame_count < DEBUG_FRAME_LIMIT:
                log_debug_frame(frame, current_state, debug_frame_count)
                debug_frame_count += 1

            if current_state == "STEP1_WAIT_START":
                next_state = run_step1(frame, state_start)
            elif current_state == "STEP2_WAIT_HOOK":
                next_state = run_step2_wait(frame, state_start)
            elif current_state == "STEP2_TRIGGER":
                next_state = run_step2_trigger(frame, state_start)
            elif current_state == "STEP3_FIGHTING":
                next_state = run_step3(frame, state_start)
            elif current_state == "STEP4_FINISH":
                next_state = run_step4(frame, state_start)
            else:
                next_state = "STEP1_WAIT_START"

            if next_state == REENTER_CURRENT_STATE:
                state_start = time.time()
                on_enter(current_state)
            elif next_state != current_state:
                current_state = next_state
                state_start = time.time()
                on_enter(current_state)

            time.sleep(SLEEP.get(current_state, 0.1))

    finally:
        release_keys()
        camera.stop()
        print("Stopped")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Auto fishing helper for NTE using screen capture and keyboard input."
    )
    preset_group = parser.add_mutually_exclusive_group()
    preset_group.add_argument(
        "--preset",
        choices=sorted(PRESETS),
        help="Detection preset to use. Default: auto-detect from the game client size.",
    )
    preset_group.add_argument(
        "-fhd",
        action="store_true",
        help="Shortcut for --preset 1080p.",
    )
    preset_group.add_argument(
        "-2k",
        dest="is_2k",
        action="store_true",
        help="Shortcut for --preset 2k.",
    )
    parser.add_argument(
        "--window-title",
        default="NTE",
        help="Game window title keyword to activate before starting. Default: NTE",
    )
    parser.add_argument(
        "--process-name",
        default=DEFAULT_PROCESS_NAME,
        help=f"Process name to prefer when matching the game window. Default: {DEFAULT_PROCESS_NAME}",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=60,
        help="Screen capture target FPS. Default: 60",
    )
    parser.add_argument(
        "--debug-frames",
        action="store_true",
        help=f"Write up to {DEBUG_FRAME_LIMIT} annotated debug frames to {DEBUG_FRAME_DIR}.",
    )
    args = parser.parse_args()

    if args.fhd:
        args.preset = "1080p"
    elif args.is_2k:
        args.preset = "2k"
    del args.fhd
    del args.is_2k
    return args


if __name__ == "__main__":
    args = parse_args()
    run_bot(
        window_title=args.window_title,
        target_fps=args.fps,
        preset=args.preset,
        debug_frames=args.debug_frames,
        process_name=args.process_name,
    )
