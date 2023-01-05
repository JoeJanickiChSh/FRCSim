import pygame as pg
from pygame.locals import *
from math import atan2, degrees, pi, sin, cos, radians, sqrt
from vector3d.vector import Vector
from OpenGL.GL import *
from OpenGL.GLU import *
from shape import BOX_PONTS
from transform import rotate_vector, scale_vector
from camera import Camera
import pygame as pg
from loader import get_vec
from units import inches_to_meters


class Renderer:
    def __init__(self, sim_properties, window_size):
        pg.init()
        pg.display.set_caption(f'FRC Sim - {sim_properties["name"]}')
        pg.display.set_icon(pg.image.load("icon.png"))
        self.disp = pg.display.set_mode(window_size, DOUBLEBUF | OPENGL)

        self.camera = Camera(rotation=Vector(pi / 4, -0.1))

        gluPerspective(60, (window_size[0] / window_size[1]), 0.01, 100.0)
        glEnable(GL_DEPTH_TEST)

        self.clock = pg.time.Clock()
        self.ground = (
            inches_to_meters(get_vec(sim_properties["field"]["ground"]["size"])) * 0.5
        )
        self.zoom = 1.0

    def loop(self, robot, field, ball, target):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                quit()

            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_EQUALS:
                    self.zoom *= 1.1
                elif e.key == pg.K_MINUS:
                    self.zoom /= 1.1
                elif e.key == pg.K_RETURN:
                    pg.quit()
                    quit()

        rel_x, rel_y = pg.mouse.get_rel()
        mouse_down = pg.mouse.get_pressed()[0]

        if mouse_down:
            self.camera.rotation.y += rel_x / 50.0
            self.camera.rotation.x += rel_y / 50.0

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.5, 0.5, 0.5, 1.0)

        glPushMatrix()

        glTranslatef(0, 0, -2)

        glRotatef(degrees(self.camera.rotation.x), 1, 0, 0)
        glRotatef(degrees(self.camera.rotation.y), 0, 1, 0)

        glScalef(0.15 * self.zoom, 0.15 * self.zoom, 0.15 * self.zoom)

        self.draw(robot, field, ball, target)
        glPopMatrix()

        pg.display.flip()

        self.clock.tick(60)

        return pg.key.get_pressed()

    def draw_line(self, pos1, pos2, color):
        glColor3f(color.x, color.y, color.z)
        glVertex3f(pos1.x, pos1.y, pos1.z)
        glColor3f(color.x, color.y, color.z)
        glVertex3f(pos2.x, pos2.y, pos2.z)

    def draw_box(self, box):
        for face in BOX_PONTS:
            tri_face = [face[0], face[1], face[2], face[0], face[3], face[2]]
            for p in tri_face:
                rot_p = rotate_vector(scale_vector(p, box.size * 0.5), box.rotation)
                shade = (
                    min(1, max(0, (Vector(1, 1, 1) * rot_p.normalize())))
                ) * 0.5 + 0.5
                point = rot_p + box.position
                glColor3f(box.color.x * shade, box.color.y * shade, box.color.z * shade)
                glVertex3f(point.x, point.y, point.z)

    def draw(self, robot, field, ball, target):

        glBegin(GL_LINES)

        self.draw_line(target, target + Vector(2, 0, 0), Vector(1, 0, 0))
        self.draw_line(target, target + Vector(0, 2, 0), Vector(0, 1, 0))
        self.draw_line(target, target + Vector(0, 0, 2), Vector(0, 0, 1))

        x_rot = -sin(robot.rotation.y)
        z_rot = -cos(robot.rotation.y)

        y_rot = cos(robot.shoot_angle)
        xz_rot = sin(robot.shoot_angle)

        self.draw_line(
            robot.position,
            robot.position + Vector(x_rot * xz_rot, y_rot, z_rot * xz_rot),
            Vector(0, 1, 0),
        )

        for box in field.boxes:
            if box.show_dir:
                self.draw_line(
                    box.position,
                    box.position + rotate_vector(Vector(0, 0, 0.1), box.rotation),
                    Vector(0, 1, 0),
                )

        glEnd()

        glBegin(GL_TRIANGLES)

        for box in field.boxes:
            self.draw_box(box)

        self.draw_box(robot.get_box())

        self.draw_box(ball.get_box())

        glEnd()
