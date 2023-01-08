import sys
import time
import pygame as pg
from pygame.locals import *
from math import atan2, degrees, sin, cos, radians, sqrt
from vector3d.vector import Vector
from OpenGL.GL import *
from OpenGL.GLU import *

from ball import Ball

from field import Field
from robot import Robot
import json
import easygui
from loader import get_vec, get_color
from units import inches_to_meters, meters_to_inches

from networktables import NetworkTables
from render import Renderer

sim_file = easygui.fileopenbox(
    default="sims/*.json", filetypes=["*.json", "*.*"])
if sim_file is None:
    quit()
with open(sim_file, "r") as fp:
    sim_properties = json.loads(fp.read())

field = Field(sim_properties["field"])
robot = Robot(sim_properties["robot"])


renderer = Renderer(sim_properties, (800, 600))


ball = Ball(
    Vector(),
    Vector(),
    inches_to_meters(sim_properties["ball"]["diameter"]),
    get_color(sim_properties["ball"]["color"]),
)

TARGET = inches_to_meters(get_vec(sim_properties["target"]))


GRAVITY = 9.81


def simulate_trajectory(point, angle):

    x_factor = sin(angle)
    y_factor = cos(angle)
    min_vel = 0
    max_vel = 100
    for _ in range(100):
        max_height = 0
        guess = 0.5 * (min_vel + max_vel)
        sim_pos = Vector()
        sim_vel = Vector(x_factor, y_factor) * guess
        while (sim_vel.y > 0) or (sim_pos.y > point.y):
            max_height = max(max_height, sim_pos.y)
            sim_pos += sim_vel * (1 / 60)
            sim_vel.y -= GRAVITY / 60
        if sim_pos.x > point.x:
            max_vel = guess
        else:
            min_vel = guess

    return guess, max_height


if sim_properties["networkTables"]:
    NetworkTables.initialize(server="10.1.66.2")
    sd = NetworkTables.getTable("SmartDashboard")

was_m = False
auto_path = []
auto_index = 0
playing_auto = False
while True:

    ball.position += ball.velocity * (1 / 60)
    ball.velocity.y -= GRAVITY / 60
    ball.rotation += 0.1
    keys = renderer.loop(robot, field, ball, TARGET)

    if keys[pg.K_SPACE]:
        ball.position = robot.position * 1
        x_rot = -sin(robot.rotation.y)
        z_rot = -cos(robot.rotation.y)

        y_rot = cos(robot.shoot_angle)
        xz_rot = sin(robot.shoot_angle)

        ball.velocity = (
            Vector(x_rot * xz_rot, y_rot, z_rot * xz_rot) * robot.shoot_speed
        )

    if keys[pg.K_w]:
        robot.velocity.z -= robot.acceleration / 60
    elif keys[pg.K_s]:
        robot.velocity.z += robot.acceleration / 60
    if keys[pg.K_a]:
        robot.velocity.x -= robot.acceleration / 60
    elif keys[pg.K_d]:
        robot.velocity.x += robot.acceleration / 60

    if keys[pg.K_LEFT]:
        robot.rot_vel += robot.rot_speed / 60
    elif keys[pg.K_RIGHT]:
        robot.rot_vel -= robot.rot_speed / 60

    if keys[pg.K_UP]:
        robot.shoot_angle -= radians(1)
    elif keys[pg.K_DOWN]:
        robot.shoot_angle += radians(1)

    if keys[pg.K_p]:
        playing_auto = True

    if playing_auto:
        kP = 0.02
        target_x, target_z, target_angle = auto_path[auto_index]
        error_x = target_x - robot.position.x
        error_z = target_z - robot.position.z
        error_angle = target_angle - robot.rotation.y
        robot.position.x += kP * error_x
        robot.position.z += kP * error_z
        robot.rotation.y += kP * error_angle

        if error_x*error_x + error_z*error_z + error_angle*error_angle < 0.1:
            auto_index += 1

        if auto_index >= len(auto_path):
            playing_auto = False
            auto_index = 0

    if keys[pg.K_k]:
        out_file = easygui.filesavebox(
            filetypes=['*.json', '*.*'], default='autos/*.json')
        if out_file is not None:
            with open(out_file, 'w') as fp:
                fp.write(json.dumps({'path': auto_path}, indent=2))
    if keys[pg.K_l]:
        in_file = easygui.fileopenbox(
            filetypes=['*.json', '*.*'], default='autos/*.json')
        if in_file is not None:
            with open(in_file, 'r') as fp:
                auto_path = json.loads(fp.read())['path']

    robot.position += robot.velocity * (1 / 60)

    robot.velocity *= robot.friction

    robot.rotation.y += robot.rot_vel / 60
    robot.rot_vel *= robot.friction

    if sim_properties["networkTables"]:
        try:
            poseX = sd.getNumber("robotX", 0)
            poseY = sd.getNumber("robotY", 0)
            poseAngle = sd.getNumber("robotAngle", 0)
            robot.position.x = -poseY
            robot.position.z = -poseX
            robot.rotation.y = poseAngle
        except Exception as e:
            print(e)

    if keys[pg.K_m]:
        was_m = True
    elif was_m:
        was_m = False

        auto_path.append([
            robot.position.x, robot.position.z, robot.rotation.y
        ])

        ball.position = robot.position * 1
        x_rot = -sin(robot.rotation.y)
        z_rot = -cos(robot.rotation.y)

        y_rot = cos(robot.shoot_angle)
        xz_rot = sin(robot.shoot_angle)

        ball.velocity = (
            Vector(x_rot * xz_rot, y_rot, z_rot * xz_rot) * robot.shoot_speed
        )
        robot_rot = atan2(
            robot.position.x - TARGET.x, robot.position.z - TARGET.z
        )

        xz_distance = sqrt(
            (robot.position.x - TARGET.x) ** 2 +
            (robot.position.z - TARGET.z) ** 2
        )
        y_distance = abs(robot.position.y - TARGET.y)

        new_velocity, max_height = simulate_trajectory(
            Vector(xz_distance, y_distance), robot.shoot_angle
        )
        max_height += robot.position.y
        ball.position = robot.position * 1
        x_rot = -sin(robot_rot)
        z_rot = -cos(robot_rot)
        y_rot = cos(robot.shoot_angle)
        xz_rot = sin(robot.shoot_angle)

        ball.velocity = Vector(x_rot * xz_rot, y_rot,
                               z_rot * xz_rot) * new_velocity

        distance_inches = meters_to_inches(xz_distance)
        distance_feet = distance_inches / 12
        speed_mps = new_velocity
        speed_ips = meters_to_inches(speed_mps)
        speed_fps = speed_ips / 12
        max_height_inches = meters_to_inches(max_height)
        max_height_feet = max_height_inches / 12

        sqrt_coef = speed_mps / sqrt(xz_distance)

        debug_text = f'Simulation for: {sim_properties["name"]}\n\n'
        debug_text += f"Shoot Angle: {round(degrees(robot.shoot_angle),2)} degrees\n"
        debug_text += f"Distance From Target: {round(xz_distance,2)}m, {round(distance_inches,2)}in, {round(distance_feet,2)}ft\n"
        debug_text += f"Initial Ball Speed: {round(speed_mps,2)}m/s, {round(speed_ips,2)}in/s, {round(speed_fps,2)}ft/s\n"
        debug_text += f"Max Ball Height: {round(max_height,2)}m, {round(max_height_inches,2)}in, {round(max_height_feet,2)}ft\n"
        debug_text += f"Distance to Shoot Speed Formula (m -> m/s): speed = {sqrt_coef} * sqrt(distance)\n"
        debug_text += f"Pose: ({round(meters_to_inches(robot.position.x),2)},{round(meters_to_inches(robot.position.z),2)}) in, {round(degrees(robot_rot),2)} degrees\n"

        if "nolog" not in sys.argv:
            with open(f"logs/simlog{int(time.time()*10)}.txt", "w") as fp:
                fp.write(debug_text)
