import tkinter

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2

# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.axes import Axes
import matplotlib
import numpy as np

import mlogging
logger = mlogging.get_logger(__name__, "debug")

class FigureOptionParser(object):
    def __init__(self):
        self.number_of_axes = 1
        self.lock_axes = True
        self.time_format ="s"
        
    def process_config(self, **config):
        for k, v in config.items():
            self.__dict__[k] = v

# we need a custom icon. For now, copy what is needed to a local
# directory.  we could then think of how to install a custom icon. I
# think it is not possible to have multiple data paths.
            
class IglooToolbar(NavigationToolbar2):
    DATAPATH = "./mpl-data"
    def __init__(self, canvas, master):
        datapath_org = matplotlib.rcParams['datapath']
        matplotlib.rcParams['datapath'] = IglooToolbar.DATAPATH
        self.toolitems=(('Home', 'Reset original view', 'home', 'home'),
                        ('Back', 'Back to  previous view', 'back', 'back'),
                        ('Forward', 'Forward to next view', 'forward', 'forward'),
                        ('Lock', 'Toggle axes lock', 'lock', 'toggle_axes_lock'),
                        (None, None, None, None),
                        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
                        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
                        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
                        (None, None, None, None),
                        ('Save', 'Save the figure', 'filesave', 'save_figure'))
        super().__init__(canvas, master)
        matplotlib.rcParams['datapath'] = datapath_org
        self.callback_functions = {}

    def add_callback(self, name, fun):
        self.callback_functions[name] = fun
        
    def toggle_axes_lock(self):
        cb = self.callback_functions["toggle_xaxes_lock"]
        cb()
        
        

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
        
        self.fig, _ax = plt.subplots(nrows=self.number_of_axes, ncols=1, sharex=self.lock_axes, squeeze=False)
        self.ax = list(_ax[:,0]) # using squeeze=True returns ax as an array
                                 # also when number_of_axes==1, but we will
                                 # use only one column ever, so it is
                                 # convenient to drop the last index.
        for ax in self.ax:
            ax.set_picker(True)
        self.active_ax = 0 
        self.canvas = FigureCanvas(self.fig, master=self.master)
        self.canvas.mpl_connect('pick_event', self.onPick)
        self.add_toolbar()
        self.canvas.draw()

    def add_toolbar(self):
        ''' Add a toolbar'''
        #self.toolbar = NavigationToolbar2(self.canvas, self.master)
        self.toolbar = IglooToolbar(self.canvas, self.master)
        self.toolbar.add_callback("toggle_xaxes_lock", self.toggle_xaxes_lock)
        self.toolbar.update()

        
    @property
    def widget(self):
        ''' TK widget'''
        return self.canvas.get_tk_widget()
        
    def line_plot(self, x, y, ax_id=None, label=''):
        ''' Plot a line

        Parameters
        ----------
        x : array of float
            x data
        y : array of float
            y data
        ax_id : int or None 
           id of axis. Active axes id is used if ax_id==None.
        label : str
            text to add to the ylabel of the axes object
        '''
        ax_id = ax_id or self.active_ax
        p = self.ax[ax_id].plot(x, y, picker=IglooFigure.PICKRADIUS)[0]
        self.plot_objects[p] = dict(label=label, ax=self.ax[ax_id])
        self.update_ylabels(self.ax[ax_id])
        
    def onPick(self, event):
        if event.mouseevent.button==3 and isinstance(event.artist, Line2D):
            # remove a line when picked with right button (3)
            self.plot_objects.pop(event.artist)
            self.update_ylabels(event.artist.axes)
            event.artist.remove()
            self.canvas.draw()
            
        elif event.mouseevent.button==1 and isinstance(event.artist, Axes):
            # clicked axes active
            index = self.ax.index(event.artist)
            logger.debug(f"Active ax : {index}")
            
    def update_ylabels(self, ax):
        ''' Updates ylabels for given axes instance'''
        s = []
        for k, v in self.plot_objects.items():
            if v['ax'] is ax:
                s.append(v['label'])
        label = "; ".join(s)
        ax.set_ylabel(label)

    def toggle_xaxes_lock(self):
        ax_id = self.active_ax
        self.lock_axes = not self.lock_axes
        if self.lock_axes:
            g = self.ax[ax_id].get_shared_x_axes()
            g.join(*self.ax)
            self.ax[ax_id].autoscale() # forces the axes to be updated.
        else:
            g = self.ax[ax_id].get_shared_x_axes()
            for a in g.get_siblings(self.ax[ax_id]):
                g.remove(a)
        self.canvas.draw()
            
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

    def line_plot(self, widget, x, y, ax_id=None, label=''):
        ''' Line plot for 2D data 

        Parameters
        ----------
        widget : TK widget
            target window
        x : array of float
            x data
        y : array of float
            y data
        ax_id : int or None
            id of axis (row). if None, then the active axes are used. 
        label : str ('')
            string to add to the axes ylabel.
        '''
        f = self.figures[widget]
        f.line_plot(x, y, ax_id, label)

    def toggle_xaxes_lock(self, widget):
        f = self.figures[widget]
        f.toggle_xaxes_lock()
    


        
if __name__ == "__main__":
    import numpy as np
    root = tkinter.Tk()
    root.wm_title("Embedding in Tk")

    def on_key_press(event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, canvas, toolbar)


    fm = FigureManager()
    options = dict(number_of_axes=2, lock_axes=False)
    widget = fm.new_figure(root, **options)
    widget.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    #canvas.mpl_connect("key_press_event", on_key_press)
    f = fm.figures[widget]
    tb = f.toolbar

    def _quit():
        root.quit()     # stops mainloop
        root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

                    
    button = tkinter.Button(master=root, text="Quit", command=_quit)
    button.pack(side=tkinter.BOTTOM)

    fm.line_plot(widget, np.arange(10), np.arange(10)**2,label='line1 (m)')
    fm.line_plot(widget, np.arange(10), 5+np.arange(10)**2, label="ballast (cm)")
    fm.figures[widget].active_ax=1
    fm.line_plot(widget, np.arange(10)+5, 5-np.arange(10)**2, label="ballast (cm)")
    fm.toggle_xaxes_lock(widget)
    fm.toggle_xaxes_lock(widget)
    f = fm.figures[widget]

    tkinter.mainloop()

