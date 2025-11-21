import ctypes
import tkinter as tk
import pyautogui
import keyboard
import random
import time
import math
import os
import pygame

pyautogui.FAILSAFE = False

# Define Windows API
# user32 = ctypes.WinDLL('user32', use_last_error=True)
'''
class RECT(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long),
    ]
'''

def load_music():
    file_list = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    music_folder = os.path.join(script_dir, 'music')
    if os.path.exists(music_folder):
        for filename in os.listdir(music_folder):
            if filename.lower().endswith('.mp3'):
                file_list.append(os.path.join(music_folder, filename))
    return file_list
'''
def clipCursor(rect):
    user32.ClipCursor(ctypes.byref(rect))

def releaseCursor():
    user32.ClipCursor(None)
'''

# --- MENU LOGIC ---
def show_menu():
    menu_root = tk.Tk()
    menu_root.attributes('-topmost', True)
    menu_root.overrideredirect(True)
    screenWidth = menu_root.winfo_screenwidth()
    screenHeight = menu_root.winfo_screenheight()
    menu_root.geometry(f"{screenWidth}x{screenHeight}+0+0")
    menu_root.attributes('-transparentcolor', 'white')
    menu_canvas = tk.Canvas(menu_root, width=screenWidth, height=screenHeight, bg='white', highlightthickness=0)
    menu_canvas.pack()

    centerX = screenWidth // 2
    centerY = screenHeight // 2

    # Draw title
    menu_canvas.create_text(
        centerX, centerY - 120,
        text="mouseGame.py",
        fill="red",
        font=("System", 52)
    )
    # Draw start button rectangle
    btn_width = 240
    btn_height = 80
    btn_x1 = centerX - btn_width // 2
    btn_y1 = centerY - btn_height // 2
    btn_x2 = centerX + btn_width // 2
    btn_y2 = centerY + btn_height // 2
    menu_canvas.create_rectangle(
        btn_x1, btn_y1, btn_x2, btn_y2,
        outline='red', width=4
    )
    # Draw "Start" text
    menu_canvas.create_text(
        centerX, centerY,
        text="Start",
        fill="red",
        font=("System", 32)
    )

    def on_menu_click(event):
        x, y = event.x, event.y
        if btn_x1 <= x <= btn_x2 and btn_y1 <= y <= btn_y2:
            menu_root.destroy()
            show_game()  # Start the game after menu closes

    menu_canvas.bind("<ButtonRelease-1>", on_menu_click)
    menu_canvas.focus_set()
    menu_root.mainloop()

# --- GAME LOGIC ---
def show_game():
    # Game window setup
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.overrideredirect(True)
    screenWidth = root.winfo_screenwidth()
    screenHeight = root.winfo_screenheight()
    root.geometry(f"{screenWidth}x{screenHeight}+0+0")
    root.attributes('-transparentcolor', 'white')
    canvas = tk.Canvas(root, width=screenWidth, height=screenHeight, bg='white', highlightthickness=0)
    canvas.pack()

    centerX = screenWidth // 2
    centerY = screenHeight // 2
    leeway = 300

    x1 = int(centerX - leeway)
    y1 = int(centerY - leeway)
    x2 = int(centerX + leeway)
    y2 = int(centerY + leeway)

    confineRect = RECT(left=x1, top=y1, right=x2, bottom=y2)

    # Level system variables
    level = 1
    circle_radius = 10
    circle_speed = 5
    circle_spawn_interval = 1000  # ms
    last_spawn_time = time.time()
    last_level_time = time.time()
    circles = []

    # Animation state for level text
    level_animating = False
    level_anim_start_time = 0
    level_anim_duration = 0.5  # seconds
    level_anim_wave_height = 24  # pixels
    level_anim_wave_length = 0.08  # seconds per char

    # --- MUSIC LOGIC ---
    music_files = load_music()
    music_index = [0]  # Mutable for nested function

    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.3)  # Set default volume to 30%
    music_volume = [0.3]  # Mutable for nested function

    def play_next_music():
        if not music_files:
            return
        try:
            pygame.mixer.music.load(music_files[music_index[0]])
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(music_volume[0])
        except Exception as e:
            print(f"Error playing music: {e}")
        music_index[0] = (music_index[0] + 1) % len(music_files)

    def check_music():
        if not pygame.mixer.music.get_busy():
            play_next_music()
        root.after(1000, check_music)  # Check every second

    play_next_music()
    check_music()

    def start_level_animation():
        nonlocal level_animating, level_anim_start_time
        level_animating = True
        level_anim_start_time = time.time()

    def spawn_circle():
        min_y = max(circle_radius, centerY - leeway)
        max_y = min(screenHeight - circle_radius, centerY + leeway)
        y = random.randint(min_y, max_y)
        circle = {'x': screenWidth + circle_radius, 'y': y}
        circles.append(circle)

    # --- REVERTED ANIMATION IMPLEMENTATION ---
    def draw_level_title(level):
        text = f"Level {level}"
        base_x = centerX
        base_y = y1 - 60
        font = ("System", 32)
        if level_animating:
            now = time.time()
            elapsed = now - level_anim_start_time
            total_wave = len(text) * level_anim_wave_length
            for i, char in enumerate(text):
                # Calculate wave offset for each character
                phase = elapsed - i * level_anim_wave_length
                if 0 <= phase < level_anim_duration:
                    offset = -abs(math.sin(phase * math.pi / level_anim_duration)) * level_anim_wave_height
                else:
                    offset = 0
                # Calculate x position for each char (monospaced for effect)
                char_x = (base_x - (len(text) * 10) // 2 + i * 20) - 20
                canvas.create_text(
                    char_x, base_y + offset,
                    text=char,
                    fill="red",
                    font=font
                )
        else:
            canvas.create_text(
                base_x, base_y,
                text=text,
                fill="red",
                font=font
            )

    def draw_game():
        canvas.delete("all")
        draw_level_title(level)
        canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=2)
        for c in circles:
            canvas.create_oval(
                c['x'] - circle_radius, c['y'] - circle_radius,
                c['x'] + circle_radius, c['y'] + circle_radius,
                fill='red', outline='black'
            )

    def move_circles():
        for c in circles:
            c['x'] -= circle_speed
        circles[:] = [c for c in circles if c['x'] + circle_radius > 0]

    def check_collision(mouse_x, mouse_y):
        for c in circles:
            dx = mouse_x - c['x']
            dy = mouse_y - c['y']
            if dx*dx + dy*dy <= circle_radius*circle_radius:
                return True
        return False

    def update_level():
        nonlocal level, circle_radius, circle_speed, circle_spawn_interval, last_level_time
        now = time.time()
        if now - last_level_time >= 5:
            level += 1
            last_level_time = now
            circle_spawn_interval = max(100, circle_spawn_interval - 100)
            if level % 5 == 0:
                circle_speed = min(20, circle_speed + 1)
            if level % 3 == 0:
                circle_radius = min(26, circle_radius + 2)
            start_level_animation()  # Trigger animation on level up

    def game_loop():
        nonlocal last_spawn_time, level_animating
        update_level()
        move_circles()
        now = time.time()
        if (now - last_spawn_time) * 1000 >= circle_spawn_interval:
            spawn_circle()
            last_spawn_time = now

        # --- VOLUME CONTROL ---
        if keyboard.is_pressed("up"):
            if music_volume[0] < 1.0:
                music_volume[0] = min(1.0, music_volume[0] + 0.1)
                pygame.mixer.music.set_volume(music_volume[0])
                print(f"Music volume: {int(music_volume[0]*100)}%")
                time.sleep(0.15)  # Prevent rapid repeat
        if keyboard.is_pressed("down"):
            if music_volume[0] > 0.0:
                music_volume[0] = max(0.0, music_volume[0] - 0.1)
                pygame.mixer.music.set_volume(music_volume[0])
                print(f"Music volume: {int(music_volume[0]*100)}%")
                time.sleep(0.15)  # Prevent rapid repeat

        # Stop animation after duration
        text = f"Level {level}"
        total_wave = len(text) * level_anim_wave_length
        if level_animating and (now - level_anim_start_time > level_anim_duration + total_wave):
            level_animating = False

        draw_game()
        x, y = pyautogui.position()
        if x < x1:
            pyautogui.moveTo(x1, y)
        elif x > x2:
            pyautogui.moveTo(x2, y)
        if y < y1:
            pyautogui.moveTo(x, y1)
        elif y > y2:
            pyautogui.moveTo(x, y2)
        if check_collision(x, y):
            print("Game Over!")
            releaseCursor()
            root.destroy()
            return
        if keyboard.is_pressed("ctrl"):
            releaseCursor()
            root.destroy()
            return
        root.after(16, game_loop)

    clipCursor(confineRect)
    game_loop()

    try:
        root.mainloop()
    finally:
        releaseCursor()
        pygame.mixer.quit()

# --- PROGRAM ENTRY POINT ---
if __name__ == "__main__":
    show_menu()