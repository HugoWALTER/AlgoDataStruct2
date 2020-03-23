import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os


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
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.imageMap = None  # none yet
        self.imageRobot = None  # none yet

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
        # place robot on left click
        self.imageRobot = self.canvas.create_image(
            (600, 600), image=self.renderRobot)

        # root.geometry("%dx%d" % (w, h))


root = tk.Tk()
root.geometry("%dx%d" % (300, 300))
root.title("BMP Image GUI")
app = Window(root)
app.pack(fill=tk.BOTH, expand=1)
root.mainloop()

# on right click place robot coordinates
# on left click place goal point (launch game) verif que le robot a été placé
