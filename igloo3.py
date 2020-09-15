import tkinter as tk
from tkinter import filedialog 
from frameClasses import *



rootWindow = tk.Tk()
rootWindow.title('igloo3')


fileF = fileFrame(rootWindow)
fileF.Frame.grid(row=0, column=0, padx=5,  pady=5)

rootWindow.mainloop()



