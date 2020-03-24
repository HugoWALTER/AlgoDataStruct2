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
        self.renderMap = None
        self.renderRobot = None
        self.storedMap = None
        self.storedRobot = None
        self.StartCoordinate = None
        self.GoalCoordinate = None
        self.startPointDefined = False
        self.goalPointDefined = False
        self.chargeDefaultMap()
        self.chargeDefaultRobot()

    def resetGame(self):
        self.imageMap = None
        self.imageRobot = None
        self.renderMap = None
        self.renderRobot = None
        self.storedMap = None
        self.storedRobot = None
        self.StartCoordinate = None
        self.GoalCoordinate = None
        self.startPointDefined = False
        self.goalPointDefined = False

    def chargeDefaultMap(self):
        self.storedMap = Image.open("Room.bmp", "r")
        self.storedMap = self.storedMap.resize((1280, 720), Image.ANTIALIAS)
        w, h = self.storedMap.size
        self.renderMap = ImageTk.PhotoImage(
            self.storedMap)

        if self.imageMap is not None:
            self.canvas.delete(self.imageMap)

        self.imageMap = self.canvas.create_image(
            (w / 2, h / 2), image=self.renderMap)

        root.geometry("%dx%d" % (w, h))

    def chargeDefaultRobot(self):
        self.storedRobot = Image.open("robot.bmp", "r")
        self.storedRobot = self.storedRobot.resize((25, 25), Image.ANTIALIAS)
        w, h = self.storedRobot.size
        self.renderRobot = ImageTk.PhotoImage(
            self.storedRobot)
        if self.imageRobot is not None:
            self.canvas.delete(self.imageRobot)

    def openFileMap(self):
        # reset game
        self.resetGame()
        filename = filedialog.askopenfilename(initialdir=os.getcwd(
        ), title="Select MAP File", filetypes=[("BMP Files", "*.bmp")])
        if not filename:
            return

        self.storedMap = Image.open(filename)
        self.storedMap = self.storedMap.resize((1280, 720), Image.ANTIALIAS)
        w, h = self.storedMap.size
        self.renderMap = ImageTk.PhotoImage(
            self.storedMap)

        if self.imageMap is not None:
            self.canvas.delete(self.imageMap)

        self.imageMap = self.canvas.create_image(
            (w / 2, h / 2), image=self.renderMap)

        root.geometry("%dx%d" % (w, h))
        self.openFileRobot()

    def openFileRobot(self):
        filename = filedialog.askopenfilename(initialdir=os.getcwd(
        ), title="Select ROBOT File", filetypes=[("BMP Files", "*.bmp")])
        if not filename:
            return

        self.storedRobot = Image.open(filename)
        self.storedRobot = self.storedRobot.resize((25, 25), Image.ANTIALIAS)
        w, h = self.storedRobot.size
        self.renderRobot = ImageTk.PhotoImage(
            self.storedRobot)
        if self.imageRobot is not None:
            self.canvas.delete(self.imageRobot)

    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    tk.Canvas.create_circle = _create_circle

    def getColorPixelAtPos(self, x, y):
        rgb_im = self.storedMap.convert('RGB')
        r, g, b = rgb_im.getpixel((x, y))
        print(r, g, b)

    def detectLeftClic(self, event):
        print("left clicked at", event.x, event.y)
        self.getColorPixelAtPos(event.x, event.y)
        if self.renderMap is not None and self.renderRobot is not None and self.startPointDefined == False:
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

    def isWin(self):
        if self.StartCoordinate.x == self.GoalCoordinate.x and self.StartCoordinate.y == self.GoalCoordinate.y:
            print("ITS WIN")
            return True
        else:
            print("ITS LOOSE")
            return False

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
root.title("Rumba AI GUI")
app = Window(root)
app.pack(fill=tk.BOTH, expand=1)
root.mainloop()
