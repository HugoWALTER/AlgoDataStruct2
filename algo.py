import tkinter as tk
import numpy as np
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import time
import copy
import math
import os
import random
import sys

import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.abspath(__file__)) +
                "./RRTStarReedsShepp/")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) +
                "./ProbabilisticRoadMap/")

try:
    import RRTStarReedsShepp
    import ProbabilisticRoadMap
    from rrt_star_reeds_shepp import RRTStarReedsShepp
    from probabilistic_road_map import PRM_planning
except ImportError:
    raise

show_animation = True


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def display_vector(self):
        print(str(self.x)+';'+str(self.y))


class Window(tk.Frame):
    MAP_SIZE_X = 1350
    MAP_SIZE_Y = 980
    ROBOT_SIZE = 45
    CIRCLE_SIZE = 22

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        menu = tk.Menu(self.master)
        master.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        config_menu = tk.Menu(menu, tearoff=0)

        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Map", command=self.open_file_map)
        file_menu.add_command(label="Exit", command=self.quit)

        menu.add_cascade(label="ConfigSpace", menu=config_menu)
        config_menu.add_command(label="Cobs", command=self.draw_cobs)

        self.canvas = tk.Canvas(self)
        self.canvas.bind("<Button-1>", self.detect_left_click)
        self.canvas.bind("<Button-3>", self.detect_right_click)
        self.canvas.bind("<Motion>", self.circle_cursor_placement)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.circle = None
        self.goal_circle = None
        self.blue_circle = None
        self.path_line = None
        self.rectangle_robot_hitbox = None
        self.image_map = None
        self.image_robot = None
        self.render_map = None
        self.render_robot = None
        self.stored_map = None
        self.stored_robot = None
        self.rgb_img = None
        self.hitbox_robot = None
        self.hitbox_cursor_circle = None
        self.start_coordinate = None
        self.goal_coordinate = None
        self.start_point_defined = False
        self.goal_point_defined = False
        self.game_started = False
        self.can_be_placed = False
        self.charge_default_map()
        self.charge_default_robot()
        self.solutionPath = []
        self.currentPos = (0, 0)
        self.store_cobs_coords = []
        self.number_algo = None
        self.finish_algo = True
        self.nb_samples_sprm = 0
        self.nb_edges_sprm = 0
        self.sprm_form_canv = None
        self.sprm_form_root = None
        self.sprm_ox = []
        self.sprm_oy = []

    def reset_game(self):
        self.circle = None
        self.goal_circle = None
        self.blue_circle = None
        self.path_line = None
        self.rectangle_robot_hitbox = None
        self.image_map = None
        self.image_robot = None
        self.render_map = None
        self.render_robot = None
        self.stored_map = None
        self.stored_robot = None
        self.rgb_img = None
        self.hitbox_robot = None
        self.hitbox_cursor_circle = None
        self.start_coordinate = None
        self.goal_coordinate = None
        self.start_point_defined = False
        self.goal_point_defined = False
        self.game_started = False
        self.can_be_placed = False
        self.solutionPath = []
        self.currentPos = (0, 0)
        self.store_cobs_coords = []
        self.canvas.delete("all")
        self.canvas.bind("<Motion>", self.circle_cursor_placement)
        self.number_algo = None
        self.finish_algo = True
        self.nb_samples_sprm = 0
        self.nb_edges_sprm = 0
        self.sprm_form_canv = None
        self.sprm_form_root = None
        self.sprm_ox = []
        self.sprm_oy = []

    def charge_default_map(self):
        self.stored_map = Image.open("Room_BW.bmp", "r")
        self.stored_map = self.stored_map.resize(
            (Window.MAP_SIZE_X, Window.MAP_SIZE_Y), Image.ANTIALIAS)
        w, h = self.stored_map.size
        self.render_map = ImageTk.PhotoImage(
            self.stored_map)
        self.rgb_img = self.stored_map.convert('RGB')

        if self.image_map is not None:
            self.canvas.delete(self.image_map)

        self.image_map = self.canvas.create_image(
            (w / 2, h / 2), image=self.render_map)

        root.geometry("%dx%d" % (w, h))

    def charge_default_robot(self):
        self.stored_robot = Image.open("robot_BW.bmp", "r")
        self.stored_robot = self.stored_robot.resize(
            (Window.ROBOT_SIZE, Window.ROBOT_SIZE), Image.ANTIALIAS)
        w, h = self.stored_robot.size
        self.render_robot = ImageTk.PhotoImage(
            self.stored_robot)
        if self.image_robot is not None:
            self.canvas.delete(self.image_robot)

    def open_file_map(self):
        self.reset_game()
        filename = filedialog.askopenfilename(initialdir=os.getcwd(
        ), title="Select MAP File", filetypes=[("BMP Files", "*.bmp")])
        if not filename:
            return

        self.stored_map = Image.open(filename)
        self.stored_map = self.stored_map.resize(
            (Window.MAP_SIZE_X, Window.MAP_SIZE_Y), Image.ANTIALIAS)
        w, h = self.stored_map.size
        self.render_map = ImageTk.PhotoImage(
            self.stored_map)
        self.rgb_img = self.stored_map.convert('RGB')

        if self.image_map is not None:
            self.canvas.delete(self.image_map)

        self.image_map = self.canvas.create_image(
            (w / 2, h / 2), image=self.render_map)

        root.geometry("%dx%d" % (w, h))
        self.open_file_robot()

    def open_file_robot(self):
        if self.game_started == False and self.image_robot is None:
            filename = filedialog.askopenfilename(initialdir=os.getcwd(
            ), title="Select ROBOT File", filetypes=[("BMP Files", "*.bmp")])
            if not filename:
                return

            self.stored_robot = Image.open(filename)
            self.stored_robot = self.stored_robot.resize(
                (Window.ROBOT_SIZE, Window.ROBOT_SIZE), Image.ANTIALIAS)
            w, h = self.stored_robot.size
            self.render_robot = ImageTk.PhotoImage(
                self.stored_robot)
            if self.image_robot is not None:
                self.canvas.delete(self.image_robot)

    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    tk.Canvas.create_circle = _create_circle

    def get_color_pixel_at_pos(self, x, y):
        r, g, b = self.rgb_img.getpixel((x, y))
        # print(r, g, b, flush=True)
        return r, g, b

    def is_robot_cursor_collide(self):
        # TODO: define if circle cursor hit a black pixel in range
        # if yes then user can't place the robot
        # if no then user CAN place the robot // same for the endpoint
        # print(self.hitbox_cursor_circle, flush=True)
        if self.hitbox_cursor_circle is not None:
            x1 = self.hitbox_cursor_circle[0]
            y1 = self.hitbox_cursor_circle[1]
            x2 = self.hitbox_cursor_circle[2]
            y2 = self.hitbox_cursor_circle[3]
            # print("hitbox: X1", self.hitbox_cursor_circle[0], flush=True)
            # print("hitbox: X2", self.hitbox_cursor_circle[2], flush=True)
            # print("hitbox: Y1", self.hitbox_cursor_circle[1], flush=True)
            # print("hitbox: Y2", self.hitbox_cursor_circle[3], flush=True)
            for x in range(x1, x2):
                if self.is_pixel_white(x, y1) is False:
                    return True
            for x in range(x1, x2):
                if self.is_pixel_white(x, y2) is False:
                    return True
            for y in range(y1, y2):
                if self.is_pixel_white(x1, y) is False:
                    return True
            for y in range(y1, y2):
                if self.is_pixel_white(x2, y) is False:
                    return True
            return False
        return True

    def is_pixel_white(self, x, y):
        if (0 < x < Window.MAP_SIZE_X) and (0 < y < Window.MAP_SIZE_Y):
            r, g, b = self.get_color_pixel_at_pos(x, y)
            if r == 255 and g == 255 and b == 255:
                # print("WHITE PIXEL")
                return True
            else:
                # print("BLACK PIXEL")
                return False

    def is_robot_cursor_free(self, x, y):
        if self.is_pixel_white(x, y) == True and self.is_robot_cursor_collide() == False:
            return True
        else:
            return False

    def display_color_cursor(self, event):
        if self.is_robot_cursor_free(event.x, event.y) == True:
            self.circle = self.canvas.create_circle(
                event.x, event.y, Window.CIRCLE_SIZE, fill="green", width=1)
            self.hitbox_cursor_circle = self.canvas.bbox(self.circle)
            self.can_be_placed = True
        else:
            self.circle = self.canvas.create_circle(
                event.x, event.y, Window.CIRCLE_SIZE, fill="red", width=1)
            self.hitbox_cursor_circle = self.canvas.bbox(self.circle)
            self.can_be_placed = False

    def circle_cursor_placement(self, event):
        self.canvas.delete(self.circle)
        self.display_color_cursor(event)

    def remove_circle_cursor(self):
        self.canvas.delete(self.circle)
        self.canvas.unbind('<Motion>')

    def define_robot_hitbox(self):
        self.hitbox_robot = self.canvas.bbox(self.image_robot)
        print("hitbox:", self.hitbox_robot)
        print("hitbox: X1", self.hitbox_robot[0])
        print("hitbox: Y1", self.hitbox_robot[1])
        print("hitbox: X2", self.hitbox_robot[2])
        print("hitbox: Y2", self.hitbox_robot[3])
        # TODO: move hitbox when robot is moving
        self.rectangle_robot_hitbox = self.canvas.create_rectangle(
            self.hitbox_robot, outline="red", width=2)

    def update_robot_hitbox(self):
        self.canvas.delete(self.rectangle_robot_hitbox)
        self.hitbox_robot = self.canvas.bbox(self.image_robot)
        print("hitbox:", self.hitbox_robot)
        print("hitbox: X1", self.hitbox_robot[0])
        print("hitbox: Y1", self.hitbox_robot[1])
        print("hitbox: X2", self.hitbox_robot[2])
        print("hitbox: Y2", self.hitbox_robot[3])
        # TODO: move hitbox when robot is moving
        self.rectangle_robot_hitbox = self.canvas.create_rectangle(
            self.hitbox_robot, outline="red", width=2)

    def detect_left_click(self, event):
        print("left clicked at", event.x, event.y)
        self.is_robot_cursor_free(event.x, event.y)
        if self.render_map is not None and self.render_robot is not None and self.start_point_defined == False and self.can_be_placed == True:
            self.image_robot = self.canvas.create_image(
                (event.x, event.y), image=self.render_robot)
            self.start_coordinate = Vector(event.x, event.y)
            Vector.display_vector(self.start_coordinate)
            self.define_robot_hitbox()
            self.start_point_defined = True

    def detect_right_click(self, event):
        print("right clicked at", event.x, event.y)
        self.is_robot_cursor_free(event.x, event.y)
        if self.start_point_defined == True and self.goal_point_defined == False and self.can_be_placed == True:
            self.goal_circle = self.canvas.create_circle(
                event.x, event.y, Window.CIRCLE_SIZE, fill="yellow", width=1)
            self.goal_coordinate = Vector(event.x, event.y)
            Vector.display_vector(self.goal_coordinate)
            self.remove_circle_cursor()
            self.goal_point_defined = True
            self.launch_game()

    def move(self):
        calc = Vector(self.start_coordinate.x, self.start_coordinate.y)
        calc.x = self.start_coordinate.x + 0  # + or - depend on direction
        calc.y = self.start_coordinate.y + 0  # + or - depend on direction
        self.canvas.coords(self.image_robot, calc.x, calc.y)
        self.update_robot_hitbox()
        print("New pos X:", calc.x)
        print("New pos Y:", calc.y)
        # loop in this function

    def move_robot_on_path_current_pos(self, index):
        self.currentPos = self.solutionPath[index]
        self.canvas.coords(
            self.image_robot, self.currentPos[0], self.currentPos[1])
        self.canvas.update()
        time.sleep(0.01)

    def set_init_solution_path(self):
        resolution = max(abs(
            self.start_coordinate.x - self.goal_coordinate.y), abs(self.start_coordinate.y - self.goal_coordinate.y))

        self.solutionPath.append(self.start_coordinate)
        for i in range(1, resolution):
            deltaX = round(
                i*float(self.goal_coordinate.x - self.start_coordinate.x)/float(resolution))
            deltaY = round(
                i*float(self.goal_coordinate.y - self.start_coordinate.y)/float(resolution))
            newX = self.start_coordinate.x + deltaX
            newY = self.start_coordinate.y + deltaY
            self.solutionPath.append((newX, newY))
        self.solutionPath.append(self.goal_coordinate)

    def draw_path(self):
        start_x = self.start_coordinate.x
        start_y = self.start_coordinate.y
        self.blue_circle = self.canvas.create_circle(
            self.start_coordinate.x, self.start_coordinate.y, Window.CIRCLE_SIZE, fill="blue", width=1)
        self.path_line = self.canvas.create_line(self.start_coordinate.x, self.start_coordinate.y,
                                                 self.goal_coordinate.x, self.goal_coordinate.y, fill='red', arrow='last')
        self.canvas.delete(self.rectangle_robot_hitbox)

    def calc_path(self):
        self.set_init_solution_path()
        self.solutionPath = list(dict.fromkeys(self.solutionPath))

    def draw_robot_following_path(self):
        for i in range(1, (len(self.solutionPath) - 1)):
            self.move_robot_on_path_current_pos(int(i))
        self.canvas.delete(self.goal_circle)
        self.canvas.update()
        time.sleep(1)

    def reset_before_path(self):
        self.canvas.coords(
            self.image_robot, self.start_coordinate.x, self.start_coordinate.y)
        self.update_robot_hitbox()
        self.canvas.update()
        self.canvas.delete(self.blue_circle)
        self.canvas.delete(self.path_line)
        self.goal_circle = self.canvas.create_circle(
            self.goal_coordinate.x, self.goal_coordinate.y, Window.CIRCLE_SIZE, fill="yellow", width=1)

    def open_dialog_path(self):
        MsgBox = tk.messagebox.askquestion(
            'Show Path', 'Do you want to show the path?', icon='info')
        if MsgBox == 'yes':
            self.draw_path()
            self.calc_path()
            self.draw_robot_following_path()
            self.reset_before_path()

    def create_configspace(self):
        self.configspace_top = tk.Toplevel(self.master)
        self.cfg_canvas = tk.Canvas(
            self.configspace_top, width=Window.MAP_SIZE_X, height=Window.MAP_SIZE_Y)
        self.cfg_canvas.pack()

    def draw_configspace_init(self):
        self.cfg_canvas.create_circle(
            self.start_coordinate.x, self.start_coordinate.y, Window.CIRCLE_SIZE / 3, fill="blue", width=1)
        self.cfg_canvas.create_circle(
            self.goal_coordinate.x, self.goal_coordinate.y, Window.CIRCLE_SIZE / 3, fill="yellow", width=1)
        self.cfg_canvas.create_line(self.start_coordinate.x, self.start_coordinate.y,
                                    self.goal_coordinate.x, self.goal_coordinate.y, fill='red', arrow='last')

    def is_pixel_approx_white(self, colors, threshold):
        for color in colors:
            if not (255 >= color >= 255 - threshold):
                return "black"
        return "white"

    def compute_map_configspace(self):
        array = np.asarray(self.rgb_img)
        coords = []
        for x in range(1, Window.MAP_SIZE_X - 1):
            for y in range(1, Window.MAP_SIZE_Y - 1):
                if (self.is_pixel_approx_white(array[y][x], 30) != "white" and ((self.is_pixel_approx_white(array[y+1][x-1], 30) == 'white')
                                                                                or (self.is_pixel_approx_white(array[y+1][x], 30) == 'white')
                                                                                or (self.is_pixel_approx_white(array[y+1][x+1], 30) == 'white')
                                                                                or (self.is_pixel_approx_white(array[y][x+1], 30) == 'white')
                                                                                or (self.is_pixel_approx_white(array[y-1][x], 30) == 'white')
                                                                                or (self.is_pixel_approx_white(array[y-1][x-1], 30) == 'white')
                                                                                or (self.is_pixel_approx_white(array[y][x-1], 30) == 'white')
                                                                                or (self.is_pixel_approx_white(array[y-1][x+1], 30) == 'white'))):
                    coords.append((x, y))
                    self.store_cobs_coords.append((x, y, 0.4))
                    self.sprm_ox.append(x)
                    self.sprm_oy.append(y)
        for count, item in enumerate(coords):
            middle = Window.ROBOT_SIZE / 2
            x, y = item
            self.cfg_canvas.create_rectangle(x - middle, y - middle, x + middle,
                                             y + middle, fill="black", width=1)
            if (count % 1000 == 0):
                self.canvas.update()

    def launch_rrt(self):
        print("Start RTT REEDS")

        start = [float(self.start_coordinate.x),
                 float(self.start_coordinate.y), np.deg2rad(0.0)]
        goal = [float(self.goal_coordinate.x),
                float(self.goal_coordinate.y), np.deg2rad(90.0)]

        rrt_star_reeds_shepp = RRTStarReedsShepp(start, goal,
                                                 self.store_cobs_coords,
                                                 [0, self.goal_coordinate.x], Window.MAP_SIZE_X, Window.MAP_SIZE_Y, max_iter=50)
        path = rrt_star_reeds_shepp.planning(animation=show_animation)

        if path and show_animation:
            rrt_star_reeds_shepp.draw_graph()
            plt.plot([x for (x, y, yaw) in path], [
                     y for (x, y, yaw) in path], '-r')
            plt.grid(True)
            plt.pause(0.001)
            plt.show(block=False)

    def move_robot_on_path_current_pos_sprm(self, index):
        self.currentPos = self.solutionPath[index]
        print("X", self.currentPos[0])
        print("Y", self.currentPos[1])
        self.canvas.coords(
            self.image_robot, self.currentPos[0], self.currentPos[1])
        self.canvas.update()
        time.sleep(1)

    def set_init_solution_path_sprm(self, rx, ry):
        self.solutionPath.append(self.start_coordinate)
        for i in range(1, len(rx) - 1):
            self.solutionPath.append((int(rx[i]), int(ry[i])))
        self.solutionPath.append(self.goal_coordinate)
        self.solutionPath.reverse()

    def draw_path_sprm(self, rx, ry):
        start_x = self.start_coordinate.x
        start_y = self.start_coordinate.y
        self.blue_circle = self.canvas.create_circle(
            self.start_coordinate.x, self.start_coordinate.y, Window.CIRCLE_SIZE, fill="blue", width=1)
        for i in range(1, len(rx) - 1):
            self.path_line = self.canvas.create_line(rx[i], ry[i],
                                                     rx[i + 1], ry[i + 1], fill='red', tag="line")
        self.canvas.delete(self.rectangle_robot_hitbox)

    def calc_path_sprm(self, rx, ry):
        self.set_init_solution_path_sprm(rx, ry)
        self.solutionPath = list(dict.fromkeys(self.solutionPath))

    def draw_robot_following_path_sprm(self):
        for i in range(1, (len(self.solutionPath) - 1)):
            self.move_robot_on_path_current_pos_sprm(int(i))
        self.canvas.delete(self.goal_circle)
        self.canvas.update()
        time.sleep(1)

    def reset_before_path_sprm(self):
        self.canvas.coords(
            self.image_robot, self.start_coordinate.x, self.start_coordinate.y)
        self.update_robot_hitbox()
        self.canvas.update()
        self.canvas.delete(self.blue_circle)
        self.canvas.delete(self.path_line)
        self.goal_circle = self.canvas.create_circle(
            self.goal_coordinate.x, self.goal_coordinate.y, Window.CIRCLE_SIZE, fill="yellow", width=1)
        self.solutionPath = []
        self.canvas.delete("line")

    def show_solution_workspace(self, rx, ry):
        self.draw_path_sprm(rx, ry)
        self.calc_path_sprm(rx, ry)
        self.draw_robot_following_path_sprm()
        self.reset_before_path_sprm()

    def launch_sprm(self):
        print("STARTING SPRM")
        sx = self.start_coordinate.x
        sy = self.start_coordinate.y
        gx = self.goal_coordinate.x
        gy = self.goal_coordinate.y
        robot_size = 20.0

        if show_animation:
            plt.plot(self.sprm_ox, self.sprm_oy, ".k")
            plt.plot(sx, sy, "^r")
            plt.plot(gx, gy, "^m")
            plt.axis([0, Window.MAP_SIZE_X, 0, Window.MAP_SIZE_Y])
            plt.gca().invert_yaxis()
            plt.grid(True)

        start = time.time()
        rx, ry = PRM_planning(sx, sy, gx, gy, self.sprm_ox, self.sprm_oy, robot_size,
                              int(self.nb_samples_sprm), int(self.nb_edges_sprm))

        end = time.time()
        print("Time of execution SPRM: %d seconds" % (end - start))
        self.finish_algo = True
        assert rx, 'Cannot found path'

        if show_animation:
            plt.plot(rx, ry, "-r")
            plt.show(block=False)

        print("END SPRM")
        self.show_solution_workspace(rx, ry)
        print("END SHOW SOLUTION")

    def get_sprm_form_values(self):
        self.nb_samples_sprm = self.nb_samples_sprm.get()
        self.nb_edges_sprm = self.nb_edges_sprm.get()
        print("Number of SAMPLES:", int(self.nb_samples_sprm))
        print("Number of EDGES:", int(self.nb_edges_sprm))
        self.sprm_form_canv.destroy()
        self.sprm_form_root.destroy()
        self.launch_sprm()

    def open_form_sprm(self):
        print("OPEN FORM")
        self.sprm_form_root = tk.Tk()
        self.sprm_form_root.title("SPRM FORM")

        self.sprm_form_canv = tk.Canvas(
            self.sprm_form_root, width=400, height=300)
        self.sprm_form_canv.pack()

        label_sample = tk.Label(self.sprm_form_root, text='Number of Samples:')
        self.sprm_form_canv.create_window(200, 10, window=label_sample)

        self.nb_samples_sprm = tk.Entry(self.sprm_form_root)
        self.sprm_form_canv.create_window(200, 40, window=self.nb_samples_sprm)

        label_edges = tk.Label(self.sprm_form_root, text='Number of Edges:')
        self.sprm_form_canv.create_window(200, 100, window=label_edges)

        self.nb_edges_sprm = tk.Entry(self.sprm_form_root)
        self.sprm_form_canv.create_window(200, 140, window=self.nb_edges_sprm)

        button_val = tk.Button(self.sprm_form_root, text='Validate',
                               command=self.get_sprm_form_values)
        self.sprm_form_canv.create_window(200, 180, window=button_val)

    def select_algorithms(self):
        value = self.number_algo.get()
        if (self.finish_algo is False):
            print("Please wait until the algorithm is finished !")
            return
        if (value == 0 and self.finish_algo is True):
            print("launch SPRM")
            self.open_form_sprm()
            self.finish_algo = False
        if (value == 1 and self.finish_algo is True):
            print("launch RTT")
            self.finish_algo = False
        if (value == 2 and self.finish_algo is True):
            print("launch RTT REEDS")
            self.finish_algo = False

    def show_algorithms(self):
        print("Open modal")
        self.number_algo = tk.IntVar()
        self.number_algo.set(-1)
        algorithms = [
            ("SPRM"),
            ("RTT"),
            ("RTT_REEDS")
        ]

        tk.Label(self.master,
                 text="""Choose your favourite algorithms:""",
                 justify=tk.LEFT,
                 padx=20).pack()

        for val, algorithm in enumerate(algorithms):
            tk.Radiobutton(self.master,
                           text=algorithm,
                           padx=20,
                           variable=self.number_algo,
                           command=self.select_algorithms,
                           value=val).pack()

    def draw_cobs(self):
        if self.game_started is True:
            print("START DRAWING COBS")
            self.create_configspace()
            self.compute_map_configspace()
            self.draw_configspace_init()
            self.show_algorithms()
            print("END DRAWING COBS")

    def launch_game(self):
        print("Launch Game")
        self.game_started = True
        print("Coord Start:")
        Vector.display_vector(self.start_coordinate)
        print("Coord Goal:")
        Vector.display_vector(self.goal_coordinate)
        self.open_dialog_path()  # REACTIVATE !!!!!
        # self.move()


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("%dx%d" % (300, 300))
    root.title("Rumba AI GUI")
    app = Window(root)
    app.pack(fill=tk.BOTH, expand=1)
    root.mainloop()

# This project is made by Hugo WALTER
