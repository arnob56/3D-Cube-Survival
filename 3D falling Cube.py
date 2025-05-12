from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import time
import math
import os

# --- Game State Variables ---
player_pos = [0.0, 0.0]
falling_cubes = []
start_time = None
game_over = False
in_menu = True
survival_time = 0
high_score = 0
difficulty = 1.0
camera_angle = 45.0
cube_fall_speed = 0.07
spawn_rate = 0.02
platform_limit = 4.5
lives = 3

# --- Load/Save High Score ---
def load_high_score():
    global high_score
    try:
        with open("score.txt", "r") as f:
            high_score = int(f.read())
    except:
        high_score = 0

def save_high_score(score):
    global high_score
    if score > high_score:
        high_score = score
        with open("score.txt", "w") as f:
            f.write(str(high_score))

# --- 3D Object Draw ---
def draw_cube(x, y, z, size=1.0, color=(1, 0, 0)):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    glutSolidCube(size)
    glPopMatrix()

def draw_floor():
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.6, 0.2)  # Grass green
    glVertex3f(-5, -0.5, -5)
    glVertex3f(5, -0.5, -5)
    glColor3f(0.1, 0.4, 0.1)  # Darker green
    glVertex3f(5, -0.5, 5)
    glVertex3f(-5, -0.5, 5)
    glEnd()

def draw_sky_gradient():
    glDisable(GL_DEPTH_TEST)
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.8, 1.0)  # Light blue
    glVertex3f(-100, -1, -90)
    glVertex3f(100, -1, -90)
    glColor3f(0.1, 0.2, 0.6)  # Deep blue
    glVertex3f(100, 50, -90)
    glVertex3f(-100, 50, -90)
    glEnd()
    glEnable(GL_DEPTH_TEST)

def draw_text(x, y, text, color=(1, 1, 1)):
    glColor3f(*color)
    glWindowPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

# --- Game Logic ---
def spawn_cube():
    x = random.uniform(-4, 4)
    z = random.uniform(-4, 4)
    falling_cubes.append([x, 6.0, z])

def check_collision():
    global lives, game_over
    hit = False
    for cube in falling_cubes[:]:
        if abs(cube[0] - player_pos[0]) < 0.7 and abs(cube[2] - player_pos[1]) < 0.7 and cube[1] <= 0.5:
            hit = True
            falling_cubes.remove(cube)
    if hit:
        lives -= 1
        if lives <= 0:
            end_game()

def check_bounds():
    global lives, game_over
    if abs(player_pos[0]) > platform_limit or abs(player_pos[1]) > platform_limit:
        lives -= 1
        player_pos[0] = max(min(player_pos[0], platform_limit), -platform_limit)
        player_pos[1] = max(min(player_pos[1], platform_limit), -platform_limit)
        if lives <= 0:
            end_game()

def increase_difficulty():
    global difficulty, cube_fall_speed, spawn_rate
    elapsed = int(time.time() - start_time)
    if elapsed % 10 == 0:
        difficulty += 0.01
    cube_fall_speed = 0.07 * difficulty
    spawn_rate = min(0.15, 0.01 * difficulty)

def end_game():
    global game_over, survival_time
    game_over = True
    survival_time = int(time.time() - start_time)
    save_high_score(survival_time)

def reset_game():
    global falling_cubes, game_over, player_pos, start_time, difficulty, lives
    player_pos[:] = [0.0, 0.0]
    falling_cubes.clear()
    start_time = time.time()
    game_over = False
    difficulty = 1.0
    lives = 3

# --- Main Display Function ---
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Camera setup
    eye_x = 12 * math.sin(math.radians(camera_angle))
    eye_z = 12 * math.cos(math.radians(camera_angle))
    gluLookAt(eye_x, 8, eye_z, 0, 0, 0, 0, 1, 0)

    draw_sky_gradient()
    draw_floor()

    if in_menu:
        draw_text(270, 420, "🎮 3D Falling Cube Survival DX", (1, 1, 0))
        draw_text(300, 370, "Press ENTER to Start")
        draw_text(290, 340, "Move: W A S D | Rotate Cam: ← →")
        draw_text(300, 310, "ESC to Quit")
        draw_text(310, 280, f"High Score: {high_score}s")
    elif not game_over:
        draw_cube(player_pos[0], 0.0, player_pos[1], size=1, color=(0, 0, 1))  # Player blue
        for cube in falling_cubes:
            draw_cube(cube[0], cube[1], cube[2], size=1, color=(1, 0.2, 0.2))  # Enemy red
        elapsed = int(time.time() - start_time)
        draw_text(10, 580, f"Time: {elapsed}s", (1, 1, 1))
        draw_text(10, 550, f"Lives: {lives}", (0, 1, 0))
        draw_text(10, 520, f"High Score: {high_score}s", (1, 1, 0))
    else:
        draw_cube(player_pos[0], 0.0, player_pos[1], size=1, color=(0, 0, 1))
        for cube in falling_cubes:
            draw_cube(cube[0], cube[1], cube[2], size=1, color=(1, 0.2, 0.2))
        draw_text(270, 340, f"💥 GAME OVER - {survival_time}s", (1, 0.6, 0.2))
        draw_text(270, 310, f"Your Score: {survival_time}s", (1, 1, 1))
        draw_text(260, 270, "Press 'R' to Restart or ESC to Exit", (1, 1, 0))

    glutSwapBuffers()

# --- Timer for Updates ---
def update(value):
    if not game_over and not in_menu:
        for cube in falling_cubes:
            cube[1] -= cube_fall_speed
        if random.random() < spawn_rate:
            spawn_cube()
        check_collision()
        check_bounds()
        increase_difficulty()
    glutPostRedisplay()
    glutTimerFunc(30, update, 0)

# --- Keyboard Input ---
def keyboard(key, x, y):
    global in_menu
    step = 0.4
    if key == b'\x1b':
        exit()
    elif key == b'\r':
        if in_menu:
            in_menu = False
            reset_game()
    elif key == b'r':
        if game_over:
            reset_game()

    if game_over or in_menu:
        return

    if key == b'w':
        player_pos[1] -= step
    elif key == b's':
        player_pos[1] += step
    elif key == b'a':
        player_pos[0] -= step
    elif key == b'd':
        player_pos[0] += step

# --- Special Keys for Camera Rotation ---
def special_input(key, x, y):
    global camera_angle
    if key == GLUT_KEY_LEFT:
        camera_angle -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_angle += 5

# --- OpenGL Setup ---
def init():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w / h, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

# --- Run Game ---
def main():
    load_high_score()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"3D Falling Cube Survival DX")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_input)
    glutTimerFunc(30, update, 0)
    glutMainLoop()

if __name__ == '__main__':
    main()
