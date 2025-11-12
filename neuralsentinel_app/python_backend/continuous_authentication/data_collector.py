import argparse
import time
import threading
import csv
import signal
import sys
from pynput import mouse, keyboard
import os
import math

def get_client_dimensions(width_arg, height_arg, offset_x_arg, offset_y_arg, scale_arg):
    """
    Returns the client area dimensions in physical pixels and its top-left offset.
    The width and height passed from Electron (via getContentBounds) are in logical pixels.
    We multiply them by the scale factor to get physical pixels.
    """
    if width_arg and height_arg and offset_x_arg and offset_y_arg and scale_arg:
        scale = float(scale_arg)
        return float(width_arg) * scale, float(height_arg) * scale, float(offset_x_arg), float(offset_y_arg), scale
    # Default values if arguments are not provided
    return 1200.0, 800.0, 0.0, 0.0, 1.0

def track_features(interval, stats, csv_filename, username, width_arg, height_arg, offset_x_arg, offset_y_arg, scale_arg):
    """
    Tracks user input events (mouse movements, clicks, and keyboard presses)
    and saves the data to a CSV file periodically.
    """
    GRID_SIZE = 4
    # Calculate client area dimensions in physical pixels
    client_width, client_height, base_offset_x, base_offset_y, scale = get_client_dimensions(width_arg, height_arg, offset_x_arg, offset_y_arg, scale_arg)

    # Variables to track user behavior
    prev_x, prev_y = 0, 0
    prev_time = time.time()
    speeds = []
    left_clicks = 0
    right_clicks = 0
    left_double_clicks = 0
    right_double_clicks = 0
    last_left_click_time = 0
    last_right_click_time = 0
    double_click_threshold = 0.3
    movement_times = []
    click_times = []
    key_press_times = []
    key_intervals = []
    key_press_durations = []
    active_keys = {}
    special_keys = {
        "backspace": 0, "enter": 0, "shift": 0, "ctrl": 0,
        "alt": 0, "caps_lock": 0, "tab": 0, "esc": 0, "space": 0,
    }
    running = True

    # Initialize heatmap cell counts (cells 0..15)
    heatmap_cells = [0] * (GRID_SIZE * GRID_SIZE)

    def calculate_speed(x, y):
        """
        Calculates the speed of the mouse movement by computing the distance 
        between the current and previous mouse position, divided by the time elapsed.
        """
        nonlocal prev_x, prev_y, prev_time
        current_time = time.time()
        dt = current_time - prev_time
        dist = math.sqrt((x - prev_x)**2 + (y - prev_y)**2)
        spd = dist / dt if dt > 0 else 0
        prev_x, prev_y, prev_time = x, y, current_time
        return spd

    def on_move(x, y):
        """
        Tracks mouse movement and updates the movement speed and timestamps.
        """
        nonlocal movement_times
        norm_x = (x - base_offset_x) / client_width
        norm_y = (y - base_offset_y) / client_height
        speed = calculate_speed(norm_x, norm_y)
        speeds.append(speed)
        movement_times.append(time.time())

    def get_heatmap_cell(x, y, client_width, client_height, base_offset_x, base_offset_y, GRID_SIZE=4):
        """
        Converts screen coordinates into client-relative coordinates and 
        calculates which cell in the heatmap grid the click belongs to.
        """
        rel_x = x - base_offset_x
        rel_y = y - base_offset_y

        if rel_x < 0 or rel_y < 0:  # Ignore clicks outside the client area
            return None

        # Clamp coordinates to ensure they are within the client area
        if rel_x >= client_width:
            rel_x = client_width - 1e-6
        if rel_y >= client_height:
            rel_y = client_height - 1e-6

        # Calculate the size of each cell and find the corresponding row and column
        cell_width = client_width / GRID_SIZE
        cell_height = client_height / GRID_SIZE

        col = int(rel_x // cell_width)
        row = int(rel_y // cell_height)

        # Ensure the cell coordinates are within the grid bounds
        col = min(col, GRID_SIZE - 1)
        row = min(row, GRID_SIZE - 1)

        return row * GRID_SIZE + col

    def on_click(x, y, button, pressed):
        """
        Tracks mouse clicks, including double clicks, and updates the heatmap.
        """
        nonlocal left_clicks, right_clicks, left_double_clicks, right_double_clicks
        nonlocal last_left_click_time, last_right_click_time, click_times

        if pressed:
            current_time = time.time()
            click_times.append(current_time)
            cell_id = get_heatmap_cell(x, y, client_width, client_height, base_offset_x, base_offset_y, GRID_SIZE)
            if cell_id is not None:
                heatmap_cells[cell_id] += 1

            if button == mouse.Button.left:
                left_clicks += 1
                if current_time - last_left_click_time < double_click_threshold:
                    left_double_clicks += 1
                last_left_click_time = current_time
            elif button == mouse.Button.right:
                right_clicks += 1
                if current_time - last_right_click_time < double_click_threshold:
                    right_double_clicks += 1
                last_right_click_time = current_time

    def on_key_press(key):
        """
        Tracks key presses and calculates key intervals and durations.
        """
        nonlocal key_press_times, key_intervals, active_keys, special_keys
        ct = time.time()
        if key_press_times:
            key_intervals.append(ct - key_press_times[-1])
        key_press_times.append(ct)
        active_keys[key] = ct

        # Track special keys
        if key == keyboard.Key.backspace:
            special_keys["backspace"] += 1
        elif key == keyboard.Key.enter:
            special_keys["enter"] += 1
        elif key == keyboard.Key.shift:
            special_keys["shift"] += 1
        elif key == keyboard.Key.ctrl:
            special_keys["ctrl"] += 1
        elif key == keyboard.Key.alt:
            special_keys["alt"] += 1
        elif key == keyboard.Key.caps_lock:
            special_keys["caps_lock"] += 1
        elif key == keyboard.Key.tab:
            special_keys["tab"] += 1
        elif key == keyboard.Key.esc:
            special_keys["esc"] += 1
        elif key == keyboard.Key.space:
            special_keys["space"] += 1

    def on_key_release(key):
        """
        Tracks key release times to calculate key durations.
        """
        nonlocal key_press_durations, active_keys
        if key in active_keys:
            pt = active_keys[key]
            rt = time.time()
            key_press_durations.append(rt - pt)
            del active_keys[key]

    def calculate_movement_to_click_time():
        """
        Calculates the time difference between the first mouse movement and the first click.
        """
        if not movement_times or not click_times:
            return 0
        return click_times[0] - movement_times[0]

    def calculate_avg_key_interval():
        """
        Calculates the average interval between key presses.
        """
        return sum(key_intervals) / len(key_intervals) if key_intervals else 0

    def calculate_avg_key_duration():
        """
        Calculates the average duration of key presses.
        """
        return sum(key_press_durations) / len(key_press_durations) if key_press_durations else 0

    def save_stats_to_csv():
        """
        Saves the collected statistics (clicks, key presses, etc.) to a CSV file.
        """
        nonlocal left_clicks, right_clicks, left_double_clicks, right_double_clicks
        nonlocal speeds, movement_times, click_times, key_intervals, key_press_durations, special_keys, running
        nonlocal heatmap_cells

        with open(csv_filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            while running:
                time.sleep(interval)
                ct = int(time.time())
                avg_speed = sum(speeds) / len(speeds) if speeds else 0
                m_to_click = calculate_movement_to_click_time()
                avg_kint = calculate_avg_key_interval()
                avg_kdur = calculate_avg_key_duration()
                heatmap_str = ",".join(str(val) for val in heatmap_cells)
                row = [
                    ct,
                    username,
                    avg_speed,
                    left_clicks,
                    right_clicks,
                    left_double_clicks,
                    right_double_clicks,
                    m_to_click,
                    avg_kint,
                    avg_kdur,
                    special_keys["backspace"],
                    special_keys["enter"],
                    special_keys["shift"],
                    special_keys["ctrl"],
                    special_keys["alt"],
                    special_keys["caps_lock"],
                    special_keys["tab"],
                    special_keys["esc"],
                    special_keys["space"],
                    heatmap_str
                ]
                writer.writerow(row)
                file.flush()
                speeds.clear()
                movement_times.clear()
                click_times.clear()
                key_intervals.clear()
                key_press_durations.clear()
                left_clicks = right_clicks = left_double_clicks = right_double_clicks = 0
                for key in special_keys:
                    special_keys[key] = 0
                heatmap_cells = [0] * (GRID_SIZE * GRID_SIZE)

    def signal_handler(sig, frame):
        """
        Handles the termination signal (Ctrl+C) to stop the data collection process gracefully.
        """
        nonlocal running
        print("\nStopping the program...")
        running = False
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    threading.Thread(target=save_stats_to_csv, daemon=True).start()

    # Start listening for mouse and keyboard events
    with mouse.Listener(on_move=on_move, on_click=on_click) as ml, \
         keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as kl:
        ml.join()
        kl.join()

def main():
    """
    The main function to set up the data collection process. It sets the CSV output file path and starts tracking features.
    """
    parser = argparse.ArgumentParser(description="Collect user behavior data.")
    parser.add_argument('--user', default='UnknownUser', help="Username to label in CSV.")
    parser.add_argument('--width', default=None, help="Client area width for grid calculations.")
    parser.add_argument('--height', default=None, help="Client area height for grid calculations.")
    parser.add_argument('--offset_x', default=None, help="Client area X offset for grid calculations.")
    parser.add_argument('--offset_y', default=None, help="Client area Y offset for grid calculations.")
    parser.add_argument('--scale', default=1.0, help="Scale factor (default 1.0) for converting logical to physical pixels.")
    args = parser.parse_args()

    interval = 5
    timestamp = int(time.time())
    appdata = os.getenv('APPDATA')

    # ➤ write each user's CSVs in their own folder
    output_dir = os.path.join(
        appdata,
        'neuralsentinel-electron',
        'user_behavior',
        args.user
    )
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    csv_filename = os.path.join(output_dir, f"mouse_keyboard_stats_{timestamp}.csv")

    # Create the CSV file with headers
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp",
            "user",
            "cursor_speed",
            "left_clicks",
            "right_clicks",
            "left_double_clicks",
            "right_double_clicks",
            "movement_to_click_time",
            "avg_key_interval",
            "avg_key_duration",
            "backspace",
            "enter",
            "shift",
            "ctrl",
            "alt",
            "caps_lock",
            "tab",
            "esc",
            "space",
            "heatmap_cells"
        ])

    # Start tracking user behavior
    track_features(interval, {}, csv_filename, args.user, args.width, args.height, args.offset_x, args.offset_y, args.scale)

if __name__ == "__main__":
    main()