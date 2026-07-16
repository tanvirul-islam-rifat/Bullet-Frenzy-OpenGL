# ============================================================
#  Bullet Frenzy
#  A 3D OpenGL shooting game demonstrating perspective
#  projection, 3D transformations, camera modes, and
#  composite character models built from primitives.
#
#  Course  : CSE423 — Computer Graphics
#  Author  : Md. Tanvirul Islam Rifat (22101311)
#  BRAC University
# ============================================================
#
#  Controls:
#    W / S          — move player forward / backward
#    A / D          — rotate gun left / right
#    LEFT CLICK     — fire bullet
#    RIGHT CLICK    — toggle first-person / third-person camera
#    UP / DOWN      — camera height
#    LEFT / RIGHT   — orbit camera angle
#    C              — toggle cheat mode (auto-aim + auto-fire)
#    V              — toggle cheat vision (camera follows gun)
#    R              — restart game
# ============================================================

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Window & World
fovY        = 120
GRID_LENGTH = 600

# Game State
player_pos   = [0, 0, 0]
manual_angle = 90
gun_angle    = 90
life         = 5
score        = 0
missed       = 0
game_over    = False

bullets  = []
enemies  = []

# Camera
camera_mode = "third"
cam_angle   = -90
cam_height  = 300

# Cheat
cheat_mode     = False
cheat_vision   = False
cheat_cooldown = 0

# OpenGL Quadric
quadric = None


def spawn_far():
    angle = random.uniform(0, 2 * math.pi)
    dist  = random.uniform(300, GRID_LENGTH)
    return [player_pos[0] + math.cos(angle) * dist,
            player_pos[1] + math.sin(angle) * dist, 15]


def spawn_enemy():
    angle = random.uniform(0, 2 * math.pi)
    dist  = random.uniform(300, GRID_LENGTH)
    enemies.append({
        'pos':       [math.cos(angle) * dist, math.sin(angle) * dist, 15],
        'scale':     1.0,
        'scale_dir': 0.01,
    })


for _ in range(5):
    spawn_enemy()


def reset_game():
    global player_pos, manual_angle, gun_angle, life, score, missed, game_over
    global bullets, enemies, cheat_mode, cheat_vision, cam_angle, cam_height, camera_mode
    player_pos = [0, 0, 0]; manual_angle = 90; gun_angle = 90
    life = 5; score = 0; missed = 0; game_over = False
    bullets.clear(); enemies.clear()
    for _ in range(5): spawn_enemy()
    camera_mode = "third"; cam_angle = -90; cam_height = 300
    cheat_mode = False; cheat_vision = False
    print("\n--- Game Restarted ---")


def fire_bullet():
    bx = player_pos[0] + math.cos(math.radians(gun_angle)) * 30
    by = player_pos[1] + math.sin(math.radians(gun_angle)) * 30
    bullets.append({'pos': [bx, by, 25], 'angle': gun_angle})
    print("Bullet Fired!")


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text: glutBitmapCharacter(font, ord(ch))
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    if game_over:
        glRotatef(90, 1, 0, 0); glTranslatef(0, 0, -20)
    glRotatef(gun_angle, 0, 0, 1)
    glScalef(1.3, 1.3, 1.3)
    # Body
    glPushMatrix(); glColor3f(0.3, 0.5, 0.2)
    glTranslatef(0, 0, 20); glScalef(0.8, 1.2, 1.6); glutSolidCube(15); glPopMatrix()
    # Head
    glPushMatrix(); glColor3f(0, 0, 0)
    glTranslatef(0, 0, 36); gluSphere(quadric, 8, 20, 20); glPopMatrix()
    # Arms
    for side in [1, -1]:
        glPushMatrix(); glColor3f(1.0, 0.85, 0.7)
        glTranslatef(8, 10*side, 24); glScalef(2.5, 0.8, 0.8)
        gluSphere(quadric, 5, 15, 15); glPopMatrix()
    # Legs
    for side in [1, -1]:
        glPushMatrix(); glColor3f(0, 0, 0.8)
        glTranslatef(0, 5*side, 10); glRotatef(180, 1, 0, 0)
        gluCylinder(quadric, 4, 2.5, 10, 15, 15); glPopMatrix()
    # Backpack
    glPushMatrix(); glColor3f(0.6, 0.6, 0.6)
    glTranslatef(-6, 0, 20); glScalef(0.5, 0.8, 1.2)
    gluSphere(quadric, 8, 15, 15); glPopMatrix()
    # Gun
    glPushMatrix(); glColor3f(0.8, 0.8, 0.8)
    glTranslatef(15, -8, 22); glScalef(3.0, 0.4, 0.6); glutSolidCube(10); glPopMatrix()
    glPopMatrix()


def draw_enemies():
    for enemy in enemies:
        glPushMatrix()
        glTranslatef(enemy['pos'][0], enemy['pos'][1], enemy['pos'][2])
        glScalef(enemy['scale'], enemy['scale'], enemy['scale'])
        glColor3f(1, 0, 0); gluSphere(quadric, 15, 20, 20)
        glTranslatef(0, 0, 14); glColor3f(0, 0, 0); gluSphere(quadric, 8, 20, 20)
        glPopMatrix()


def draw_bullets():
    glColor3f(1, 1, 0)
    for b in bullets:
        glPushMatrix(); glTranslatef(b['pos'][0], b['pos'][1], b['pos'][2])
        glScalef(0.5, 0.5, 0.5); glutSolidCube(10); glPopMatrix()


def draw_grid():
    glBegin(GL_QUADS)
    step = 50
    for x in range(-GRID_LENGTH, GRID_LENGTH, step):
        for y in range(-GRID_LENGTH, GRID_LENGTH, step):
            glColor3f(1,1,1) if ((x//step)+(y//step))%2==0 else glColor3f(0.7,0.5,0.95)
            glVertex3f(x,y,0); glVertex3f(x+step,y,0)
            glVertex3f(x+step,y+step,0); glVertex3f(x,y+step,0)
    wh = 50
    for col, x1, y1, x2, y2 in [
        ((0,1,1), -GRID_LENGTH, GRID_LENGTH,  GRID_LENGTH,  GRID_LENGTH),
        ((0,1,0), -GRID_LENGTH,-GRID_LENGTH,  GRID_LENGTH, -GRID_LENGTH),
        ((0,0,1), -GRID_LENGTH,-GRID_LENGTH, -GRID_LENGTH,  GRID_LENGTH),
        ((0,1,1),  GRID_LENGTH,-GRID_LENGTH,  GRID_LENGTH,  GRID_LENGTH),
    ]:
        glColor3f(*col)
        glVertex3f(x1,y1,0); glVertex3f(x2,y2,0)
        glVertex3f(x2,y2,wh); glVertex3f(x1,y1,wh)
    glEnd()


def setup_camera():
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    if camera_mode == "third":
        cx = player_pos[0] + math.cos(math.radians(cam_angle)) * 300
        cy = player_pos[1] + math.sin(math.radians(cam_angle)) * 300
        gluLookAt(cx, cy, cam_height,
                  player_pos[0], player_pos[1], player_pos[2], 0, 0, 1)
    else:
        la = manual_angle if (cheat_mode and not cheat_vision) else gun_angle
        cx = player_pos[0] - math.cos(math.radians(la)) * 10
        cy = player_pos[1] - math.sin(math.radians(la)) * 10
        cz = player_pos[2] + 80
        gluLookAt(cx, cy, cz,
                  cx + math.cos(math.radians(la))*100,
                  cy + math.sin(math.radians(la))*100,
                  cz - 20, 0, 0, 1)


def show_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity(); glViewport(0, 0, 1000, 800)
    setup_camera()
    draw_grid(); draw_player(); draw_enemies(); draw_bullets()
    draw_text(10, 770, f"Player Life Remaining: {life}")
    draw_text(10, 740, f"Game Score: {score}")
    draw_text(10, 710, f"Player Bullet Missed: {missed}")
    if game_over:
        draw_text(350, 400, "GAME OVER!  Press R to Restart")
    if cheat_mode:
        draw_text(800, 770, "CHEAT MODE: ON")
        if cheat_vision and camera_mode == "first":
            draw_text(800, 740, "AUTO-CAM: ON")
    glutSwapBuffers()


def idle():
    global gun_angle, cheat_cooldown, missed, score, life, game_over
    if not game_over:
        if cheat_mode:
            gun_angle = (gun_angle + 5) % 360
            cheat_cooldown -= 1
            if cheat_cooldown <= 0:
                for enemy in enemies:
                    dx = enemy['pos'][0] - player_pos[0]
                    dy = enemy['pos'][1] - player_pos[1]
                    diff = (math.degrees(math.atan2(dy, dx)) - gun_angle) % 360
                    if diff > 180: diff -= 360
                    if abs(diff) < 15:
                        fire_bullet(); cheat_cooldown = 20; break

        surviving = []
        for b in bullets:
            b['pos'][0] += math.cos(math.radians(b['angle'])) * 15
            b['pos'][1] += math.sin(math.radians(b['angle'])) * 15
            if abs(b['pos'][0]) > GRID_LENGTH or abs(b['pos'][1]) > GRID_LENGTH:
                missed += 1; print(f"Bullet missed: {missed}")
            else:
                surviving.append(b)
        bullets[:] = surviving

        for enemy in enemies:
            enemy['scale'] += enemy['scale_dir']
            if enemy['scale'] > 1.3 or enemy['scale'] < 0.7: enemy['scale_dir'] *= -1
            dx = player_pos[0]-enemy['pos'][0]; dy = player_pos[1]-enemy['pos'][1]
            dist = math.sqrt(dx**2+dy**2)
            if dist > 0:
                enemy['pos'][0] += (dx/dist); enemy['pos'][1] += (dy/dist)
            if dist < 20:
                life -= 1; print(f"Remaining Player Life: {life}")
                enemy['pos'] = spawn_far()

        hit = []
        for b in bullets:
            for enemy in enemies:
                dx = b['pos'][0]-enemy['pos'][0]; dy = b['pos'][1]-enemy['pos'][1]
                if math.sqrt(dx**2+dy**2) < 25:
                    score += 10; enemy['pos'] = spawn_far(); hit.append(b); break
        for hb in hit:
            if hb in bullets: bullets.remove(hb)

        if life <= 0 or missed >= 10: game_over = True
    glutPostRedisplay()


def keyboard_listener(key, x, y):
    global player_pos, manual_angle, gun_angle, cheat_mode, cheat_vision
    if game_over:
        if key in (b'r', b'R'): reset_game()
        return
    speed = 10; rad = math.radians(manual_angle)
    if key in (b'w',b'W'): player_pos[0]+=math.cos(rad)*speed; player_pos[1]+=math.sin(rad)*speed
    if key in (b's',b'S'): player_pos[0]-=math.cos(rad)*speed; player_pos[1]-=math.sin(rad)*speed
    if key in (b'a',b'A'):
        manual_angle += 5
        if not cheat_mode: gun_angle = manual_angle
    if key in (b'd',b'D'):
        manual_angle -= 5
        if not cheat_mode: gun_angle = manual_angle
    if key in (b'c',b'C'):
        cheat_mode = not cheat_mode
        if not cheat_mode: gun_angle = manual_angle
    if key in (b'v',b'V'): cheat_vision = not cheat_vision
    if key in (b'r',b'R'): reset_game()


def special_key_listener(key, x, y):
    global cam_angle, cam_height
    if key == GLUT_KEY_UP:    cam_height += 10
    if key == GLUT_KEY_DOWN:  cam_height -= 10
    if key == GLUT_KEY_LEFT:  cam_angle  -= 5
    if key == GLUT_KEY_RIGHT: cam_angle  += 5


def mouse_listener(button, state, x, y):
    global camera_mode
    if game_over: return
    if button == GLUT_LEFT_BUTTON  and state == GLUT_DOWN: fire_bullet()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = "first" if camera_mode == "third" else "third"


def main():
    global quadric
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy")
    glEnable(GL_DEPTH_TEST)
    quadric = gluNewQuadric()
    glutDisplayFunc(show_screen)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()