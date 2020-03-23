import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import time


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def displayVector(self):
        print(str(self.x)+';'+str(self.y))


class Window(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        menu = tk.Menu(self.master)
        master.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Load Map", command=self.openFileMap)
        file_menu.add_command(label="Load Robot", command=self.openFileRobot)
        file_menu.add_command(label="Exit", command=self.quit)
        menu.add_cascade(label="File", menu=file_menu)

        self.canvas = tk.Canvas(self)
        self.canvas.bind("<Button-1>", self.detectLeftClic)
        self.canvas.bind("<Button-3>", self.detectRightClic)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.imageMap = None
        self.imageRobot = None
        self.renderRobot = None
        self.StartCoordinate = None
        self.GoalCoordinate = None
        self.startPointDefined = False
        self.goalPointDefined = False

        # Where I open my file

    def openFileMap(self):
        filename = filedialog.askopenfilename(initialdir=os.getcwd(
        ), title="Select BMP File", filetypes=[("BMP Files", "*.bmp")])
        if not filename:
            return

        load = Image.open(filename)
        load = load.resize((1280, 720), Image.ANTIALIAS)
        w, h = load.size
        self.renderMap = ImageTk.PhotoImage(
            load)

        if self.imageMap is not None:
            self.canvas.delete(self.imageMap)

        self.imageMap = self.canvas.create_image(
            (w / 2, h / 2), image=self.renderMap)

        root.geometry("%dx%d" % (w, h))

    def openFileRobot(self):
        filename = filedialog.askopenfilename(initialdir=os.getcwd(
        ), title="Select BMP File", filetypes=[("BMP Files", "*.bmp")])
        if not filename:
            return

        load = Image.open(filename)
        load = load.resize((25, 25), Image.ANTIALIAS)
        w, h = load.size
        self.renderRobot = ImageTk.PhotoImage(
            load)
        if self.imageRobot is not None:
            self.canvas.delete(self.imageRobot)

    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    tk.Canvas.create_circle = _create_circle

    def detectLeftClic(self, event):
        print("left clicked at", event.x, event.y)
        if self.renderRobot is not None and self.startPointDefined == False:
            self.imageRobot = self.canvas.create_image(
                (event.x, event.y), image=self.renderRobot)
            self.StartCoordinate = Vector(event.x, event.y)
            Vector.displayVector(self.StartCoordinate)
            self.startPointDefined = True

    def detectRightClic(self, event):
        print("right clicked at", event.x, event.y)
        if self.startPointDefined == True and self.goalPointDefined == False:
            self.canvas.create_circle(
                event.x, event.y, 10, fill="red", width=1)
            self.GoalCoordinate = Vector(event.x, event.y)
            Vector.displayVector(self.GoalCoordinate)
            self.goalPointDefined = True
            self.launchGame()

    def launchGame(self):
        print("Launch Game")
        print("Coord Start: ")
        Vector.displayVector(self.StartCoordinate)
        print("Coord Goal: ")
        Vector.displayVector(self.GoalCoordinate)
        self.canvas.move(self.imageRobot, 10, 0)
        # time.sleep(1)
        # do simple loop to move start to goal pos (x & y)
        # getInfosbypixel from BMP
        # do algo to move only if x + 1 & y + 1 are white


root = tk.Tk()
root.geometry("%dx%d" % (300, 300))
root.title("BMP Image GUI")
app = Window(root)
app.pack(fill=tk.BOTH, expand=1)
root.mainloop()

# on right click place robot coordinates
# on left click place goal point (launch game) verif que le robot a été placé
