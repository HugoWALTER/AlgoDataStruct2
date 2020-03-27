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
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        menu = tk.Menu(self.master)
        master.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Load Map", command=self.open_file_map)
        file_menu.add_command(label="Load Robot", command=self.open_file_robot)
        file_menu.add_command(label="Exit", command=self.quit)
        menu.add_cascade(label="File", menu=file_menu)

        self.canvas = tk.Canvas(self)
        self.canvas.bind("<Button-1>", self.detect_left_click)
        self.canvas.bind("<Button-3>", self.detect_right_click)
        self.canvas.bind("<Motion>", self.free_robot_placement)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.circle = 0
        self.image_map = None
        self.image_robot = None
        self.render_map = None
        self.render_robot = None
        self.stored_map = None
        self.stored_robot = None
        self.start_coordinate = None
        self.goal_coordinate = None
        self.start_point_defined = False
        self.goal_point_defined = False
        self.game_started = False
        self.can_be_placed = False
        self.charge_default_map()
        self.charge_default_robot()

    def reset_game(self):
        self.circle = 0
        self.image_map = None
        self.image_robot = None
        self.render_map = None
        self.render_robot = None
        self.stored_map = None
        self.stored_robot = None
        self.start_coordinate = None
        self.goal_coordinate = None
        self.start_point_defined = False
        self.goal_point_defined = False
        self.game_started = False
        self.can_be_placed = False

    def charge_default_map(self):
        self.stored_map = Image.open("Room.bmp", "r")
        self.stored_map = self.stored_map.resize((1280, 720), Image.ANTIALIAS)
        w, h = self.stored_map.size
        self.render_map = ImageTk.PhotoImage(
            self.stored_map)

        if self.image_map is not None:
            self.canvas.delete(self.image_map)

        self.image_map = self.canvas.create_image(
            (w / 2, h / 2), image=self.render_map)

        root.geometry("%dx%d" % (w, h))

    def charge_default_robot(self):
        self.stored_robot = Image.open("robot.bmp", "r")
        self.stored_robot = self.stored_robot.resize((25, 25), Image.ANTIALIAS)
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
        self.stored_map = self.stored_map.resize((1280, 720), Image.ANTIALIAS)
        w, h = self.stored_map.size
        self.render_map = ImageTk.PhotoImage(
            self.stored_map)

        if self.image_map is not None:
            self.canvas.delete(self.image_map)

        self.image_map = self.canvas.create_image(
            (w / 2, h / 2), image=self.render_map)

        root.geometry("%dx%d" % (w, h))
        self.open_file_robot()

    def open_file_robot(self):
        if self.game_started == False:
            filename = filedialog.askopenfilename(initialdir=os.getcwd(
            ), title="Select ROBOT File", filetypes=[("BMP Files", "*.bmp")])
            if not filename:
                return

            self.stored_robot = Image.open(filename)
            self.stored_robot = self.stored_robot.resize(
                (25, 25), Image.ANTIALIAS)
            w, h = self.stored_robot.size
            self.render_robot = ImageTk.PhotoImage(
                self.stored_robot)
            if self.image_robot is not None:
                self.canvas.delete(self.image_robot)

    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    tk.Canvas.create_circle = _create_circle

    def get_color_pixel_at_pos(self, x, y):
        rgb_im = self.stored_map.convert('RGB')
        r, g, b = rgb_im.getpixel((x, y))
        print(r, g, b)
        return r, g, b

    def display_color_cursor(self, event):
        if self.is_robot_free(event.x, event.y) == True:
            self.circle = self.canvas.create_circle(
                event.x, event.y, 10, fill="green", width=1)
            self.can_be_placed = True
        else:
            self.circle = self.canvas.create_circle(
                event.x, event.y, 10, fill="red", width=1)
            self.can_be_placed = False

    def free_robot_placement(self, event):
        x, y = event.x + 3, event.y + 7
        radius = 10
        x_max = x + radius
        x_min = x - radius
        y_max = y + radius
        y_min = y - radius

        self.canvas.delete(self.circle)
        self.display_color_cursor(event)

    def is_robot_free(self, x, y):
        r, g, b = self.get_color_pixel_at_pos(x, y)
        if r == 255 and g == 255 and b == 255:
            print("WHITE PIXEL")
            return True
        else:
            print("BLACK PIXEL")
            return False

    def remove_circle_cursor(self):
        self.canvas.delete(self.circle)
        self.canvas.unbind('<Motion>')

    def detect_left_click(self, event):
        print("left clicked at", event.x, event.y)
        self.is_robot_free(event.x, event.y)
        if self.render_map is not None and self.render_robot is not None and self.start_point_defined == False and self.can_be_placed == True:
            self.image_robot = self.canvas.create_image(
                (event.x, event.y), image=self.render_robot)
            self.start_coordinate = Vector(event.x, event.y)
            Vector.display_vector(self.start_coordinate)
            self.start_point_defined = True

    def detect_right_click(self, event):
        print("right clicked at", event.x, event.y)
        self.is_robot_free(event.x, event.y)
        if self.start_point_defined == True and self.goal_point_defined == False and self.can_be_placed == True:
            self.canvas.create_circle(
                event.x, event.y, 10, fill="red", width=1)
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
        calc.x = self.start_coordinate.x + 10
        calc.y = self.start_coordinate.y + 0
        self.canvas.coords(self.image_robot, calc.x, calc.y)
        print("New pos X:", calc.x)
        print("New pos Y:", calc.y)
        # self.is_win(calc)
        # self.canvas.move(self.image_robot, 10, 0)

    def launch_game(self):
        print("Launch Game")
        self.game_started = True
        print("Coord Start: ")
        Vector.display_vector(self.start_coordinate)
        print("Coord Goal: ")
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
