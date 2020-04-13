import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import time


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
        file_menu.add_command(label="Load Map", command=self.open_file_map)
        file_menu.add_command(label="Exit", command=self.quit)
        menu.add_cascade(label="File", menu=file_menu)

        self.canvas = tk.Canvas(self)
        self.canvas.bind("<Button-1>", self.detect_left_click)
        self.canvas.bind("<Button-3>", self.detect_right_click)
        self.canvas.bind("<Motion>", self.circle_cursor_placement)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.circle = None
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

    def reset_game(self):
        self.circle = None
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
        self.canvas.delete("all")
        self.canvas.bind("<Motion>", self.circle_cursor_placement)

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
        print(r, g, b, flush=True)
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
            self.canvas.create_circle(
                event.x, event.y, Window.CIRCLE_SIZE, fill="yellow", width=1)
            self.goal_coordinate = Vector(event.x, event.y)
            Vector.display_vector(self.goal_coordinate)
            self.remove_circle_cursor()
            self.goal_point_defined = True
            self.launch_game()

    def is_win(self, calc):
        if calc.x == self.goal_coordinate.x and calc.y == self.goal_coordinate.y:
            print("ITS WIN")
            return True
        else:
            print("ITS LOOSE")
            return False

    def move(self):
        calc = Vector(self.start_coordinate.x, self.start_coordinate.y)
        calc.x = self.start_coordinate.x + 10  # + or - depend on direction
        calc.y = self.start_coordinate.y + 0  # + or - depend on direction
        self.canvas.coords(self.image_robot, calc.x, calc.y)
        self.update_robot_hitbox()
        print("New pos X:", calc.x)
        print("New pos Y:", calc.y)
        # self.is_win(calc)
        # loop in this function

    def launch_game(self):
        print("Launch Game")
        self.game_started = True
        print("Coord Start:")
        Vector.display_vector(self.start_coordinate)
        print("Coord Goal:")
        Vector.display_vector(self.goal_coordinate)
        self.move()

        # time.sleep(1)
        # do simple loop to move start to goal pos (x & y)
        # getInfosbypixel from BMP
        # do algo to move only if x + 1 & y + 1 are white


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("%dx%d" % (300, 300))
    root.title("Rumba AI GUI")
    app = Window(root)
    app.pack(fill=tk.BOTH, expand=1)
    root.mainloop()

# This project is made by Hugo WALTER
