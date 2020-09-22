import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


class FigureOptionParser(object):
    def __init__(self):
        self.number_of_axes = 1
        self.lock_axes = True
        self.time_format ="s"
        
    def process_config(self, **config):
        for k, v in config.items():
            self.__dict__[k] = v
            

class IglooFigure(FigureOptionParser):
    ''' A figure object for figures

    Parameters
    ----------
    master : TK widget
         master window to draw into
    **config : dictionary with config options, parsed by FigureOptionParser
    
    Class to provide an interface to a single window, with possibly multiple axes.

    The main method to call is create_canvas(), after which a TK widget is created and set as 
    an attribute.

    Plotting methods are

         line_plot()

    '''
    PICKRADIUS = 5
    
    def __init__(self, master, **config):
        super().__init__()
        self.master = master
        self.process_config(**config)
        self.plot_objects = dict()
        
    def create_canvas(self):
        ''' Create a canvas with figure and axes'''
        
        self.fig, self.ax = plt.subplots(nrows=self.number_of_axes, ncols=1, sharex=self.lock_axes, squeeze=False)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.mpl_connect('pick_event', self.onPick)
        self.add_toolbar()
        self.canvas.draw()

    def add_toolbar(self):
        ''' Add a toolbar'''
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.update()

        
    @property
    def widget(self):
        ''' TK widget'''
        return self.canvas.get_tk_widget()
        
    def line_plot(self, ax_id, x, y, label):
        ''' Plot a line

        Parameters
        ----------
        ax_id : int
           id of axis
        
        x : array of float
            x data
        y : array of float
            y data
        label : str
            text to add to the ylabel of the axes object
        '''
        p = self.ax[ax_id, 0].plot(x, y, picker=IglooFigure.PICKRADIUS)[0]
        self.plot_objects[p] = dict(label=label, ax=self.ax[ax_id,0])
        self.update_ylabels(self.ax[ax_id,0])
        
    def onPick(self, event):
        # remove a line when picked with right button (3)
        if event.mouseevent.button==3 and isinstance(event.artist, Line2D):
            self.plot_objects.pop(event.artist)
            self.update_ylabels(event.artist.axes)
            event.artist.remove()
            self.canvas.draw()
            
    def update_ylabels(self, ax):
        ''' Updates ylabels for given axes instance'''
        s = []
        for k, v in self.plot_objects.items():
            if v['ax'] is ax:
                s.append(v['label'])
        label = "; ".join(s)
        ax.set_ylabel(label)
            
class FigureManager(object):
    ''' Main interface for plotting data in figures
    
    Implemented plot types:

    line_plot()
    
    '''
    
    def __init__(self):
        self.figures = dict()
        
    def new_figure(self, master, **config):
        '''Creates a new figure

        Parameters
        ----------
        master : TK widget
            window to draw the figure into
        config : dictionary 
            configuration settings for creating a figure, parsed by FigureOptionParser
        
        Returns
        -------
        TK widget
        '''
        igloo_figure = IglooFigure(master, **config)
        igloo_figure.create_canvas()
        widget = igloo_figure.widget
        self.figures[widget] = igloo_figure
        return widget

    def line_plot(self, widget, ax_id, x, y, label=''):
        ''' Line plot for 2D data 

        Parameters
        ----------
        widget : TK widget
            target window
        ax_id : int
            id of axis (row)
        x : array of float
            x data
        y : array of float
            y data
        label : str ('')
            string to add to the axes ylabel.
        '''
        f = self.figures[widget]
        f.line_plot(ax_id, x, y, label)

    

if __name__ == "__main__":
    import numpy as np
    root = tkinter.Tk()
    root.wm_title("Embedding in Tk")

    def on_key_press(event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, canvas, toolbar)


    fm = FigureManager()
    widget = fm.new_figure(root)
    widget.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    #canvas.mpl_connect("key_press_event", on_key_press)


    def _quit():
        root.quit()     # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

                    
    button = tkinter.Button(master=root, text="Quit", command=_quit)
    button.pack(side=tkinter.BOTTOM)

    fm.line_plot(widget, 0, np.arange(10), np.arange(10)**2,label='line1 (m)')
    fm.line_plot(widget, 0, np.arange(10), 5+np.arange(10)**2, label="ballast (cm)")
    tkinter.mainloop()

