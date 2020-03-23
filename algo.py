import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os


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

        file_menu = tk.Menu(menu)
        file_menu.add_command(label="Load Map", command=self.openFileMap)
        file_menu.add_command(label="Load Robot", command=self.openFileRobot)
        file_menu.add_command(label="Exit", command=self.quit)
        menu.add_cascade(label="File", menu=file_menu)

        self.canvas = tk.Canvas(self)
        self.canvas.bind("<Button-1>", self.detectLeftClic)
        self.canvas.bind("<Button-3>", self.detectRightClic)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.imageMap = None  # none yet
        self.imageRobot = None  # none yet
        self.renderRobot = None  # none yet
        self.startPointDefined = False
        self.goalPointDefined = False

        # Where I open my file

    def openFileMap(self):
        filename = filedialog.askopenfilename(initialdir=os.getcwd(
        ), title="Select BMP File", filetypes=[("BMP Files", "*.bmp")])
        if not filename:
            return  # user cancelled; stop this method

        load = Image.open(filename)
        load = load.resize((1280, 720), Image.ANTIALIAS)
        w, h = load.size
        print(w)
        print(h)
        self.renderMap = ImageTk.PhotoImage(
            load)  # must keep a reference to this

        if self.imageMap is not None:  # if an image was already loaded
            self.canvas.delete(self.imageMap)  # remove the previous image

        self.imageMap = self.canvas.create_image(
            (w / 2, h / 2), image=self.renderMap)

        root.geometry("%dx%d" % (w, h))

    def openFileRobot(self):
        filename = filedialog.askopenfilename(initialdir=os.getcwd(
        ), title="Select BMP File", filetypes=[("BMP Files", "*.bmp")])
        if not filename:
            return  # user cancelled; stop this method

        load = Image.open(filename)
        load = load.resize((25, 25), Image.ANTIALIAS)
        w, h = load.size
        print(w)
        print(h)
        self.renderRobot = ImageTk.PhotoImage(
            load)  # must keep a reference to this
        if self.imageRobot is not None:  # if an image was already loaded
            self.canvas.delete(self.imageRobot)  # remove the previous image

    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    tk.Canvas.create_circle = _create_circle

    def detectLeftClic(self, event):
        print("left clicked at", event.x, event.y)
        if self.renderRobot is not None and self.startPointDefined == False:
            self.imageRobot = self.canvas.create_image(
                (event.x, event.y), image=self.renderRobot)
            StartCoordinate = Vector(event.x, event.y)
            Vector.displayVector(StartCoordinate)
            self.startPointDefined = True

    def detectRightClic(self, event):
        print("right clicked at", event.x, event.y)
        if self.startPointDefined == True:
            self.canvas.create_circle(
                event.x, event.y, 10, fill="red", width=1)
            GoalCoordinate = Vector(event.x, event.y)
            Vector.displayVector(GoalCoordinate)
            self.goalPointDefined = True


root = tk.Tk()
root.geometry("%dx%d" % (300, 300))
root.title("BMP Image GUI")
app = Window(root)
app.pack(fill=tk.BOTH, expand=1)
root.mainloop()

# on right click place robot coordinates
# on left click place goal point (launch game) verif que le robot a été placé
