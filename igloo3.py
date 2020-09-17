import tkinter as tk
from tkinter import filedialog 
from tkinter import ttk 
import numpy as np
import matplotlib.pylab as plt
import sys
import os
import datetime as dt
import scipy.io
import dbdreader
from backend import * 
from frontend import * 



def main():
    rootWindow = tk.Tk()
    rootWindow.title('igloo3')

    Dcont = DataContainer()

    fileF = fileFrame(rootWindow, Dcont)
    fileF.Frame.grid(row=0, column=0, padx=5,  pady=5)

    rootWindow.mainloop()


if __name__ == "__main__":
        main()
