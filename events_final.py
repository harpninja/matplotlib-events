'''
AnnotateablePlot
Draw and interact with an annotateable plot
Author: Kristina Johnson
'''
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import tkinter as tk
import numpy as np

class AnnotateablePlot():
    '''
    Draw a Plot that can be annotated
    '''
    def __init__(self):
        # temporary data
        self.hours = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.array1 = [8, 13, 18, 7, 5, 45, 54, 33, 12, 78, 99, 110]
        self.array2 = [7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84]
        self.array3 = [22, 19, 44, 73, 14, 85, 27, 31, 36, 7, 2, 77]
        self.columns = [self.array1, self.array2, self.array3]
        self.names = ['array1', 'array2', 'array3']

        # event coordinates
        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None
        self.coords = []        # list of selected points
        self.annotated = []     # list of annotated points
        self.annotation_mode = False    # annotation mode added to avoid mouse event
                                        # conflict with the Matplotlib canvas
                                        # navigation tools

        # plot variables
        self.width = 2
        self.fig1 = plt.figure()
        self.ax = self.fig1.add_subplot(1, 1, 1)

        # plots
        self.plot_list = []
        self.patch_list = []   # for the plot legend
        self.plot_selected = ''

        # event callbacks
        self.click = self.fig1.canvas.mpl_connect('pick_event', self.on_click)
        self.press = self.fig1.canvas.mpl_connect('button_press_event', self.on_press)
        self.drag = self.fig1.canvas.mpl_connect('button_release_event', self.on_release)
        self.key_press = self.fig1.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.key_release = self.fig1.canvas.mpl_connect('key_release_event', self.on_key_release)

        # create axis labels & legend
        self.ax.set_ylabel('Number', color="#555555", fontsize=12)
        self.ax.set_xlabel('Hour', color="#555555", fontsize=12)

        # dynamic plot colours based on data
        self.colour_map = plt.get_cmap('viridis')
        linear_space = np.linspace(0, 1, len(self.columns))
        self.colours = self.colour_map(linear_space)

        for i in range(0, len(self.columns)):
            self.plot_list.append(plt.plot(self.hours, self.columns[i], color=self.colours[i], linestyle='None', marker='o', markersize=2, picker=3))
            self.patch_list.append(mpatches.Patch(color=self.colours[i], label=self.names[i]))

        plt.legend(handles=self.patch_list)
        plt.show()

        # disconnect things later
        # self.fig1.canvas.mpl_disconnect(self.click)

    def is_in_array(self, point, array):
        '''
        Test if a point is in the given array of data.
        Note: the on_click event counts from array 0 not 1.
        '''
        int_x = int(point['x'])
        int_y = int(point['y'])
        if array[int_x - 1] == int_y:
            return True
        else:
            return False

    def is_in_rectangle(self, array):
        '''
        Test to find points in array that are contained within
        the dragged rectangular selection.
        '''
        x_min = None
        x_max = None
        y_min = None
        y_max = None

        if self.x2 > self.x1:
            x_min = self.x1
            x_max = self.x2
        else:
            x_min = self.x2
            x_max = self.x1

        if self.y2 > self.y1:
            y_min = self.y1
            y_max = self.y2
        else:
            y_min = self.y2
            y_max = self.y1

        for i in range(len(array)):
            if (x_min <= self.hours[i] <= x_max) and (y_min <= array[i] <= y_max):
                point = {'x': self.hours[i], 'y' : array[i]}
                print('point in rectangle = ', point)
                self.coords.append(point)

    def on_key_press(self, event):
        ''' Detect key presses.  Activate annotation mode. '''
        print('key_press:', event.key)
        if event.key == 'a':
            self.annotation_mode = True

    def on_key_release(self, event):
        ''' Detect key releases.  Exit annotation mode. '''
        print('key_release:', event.key)
        self.annotation_mode = False
        print('annotation mode is false')

    def on_click(self, event):
        ''' Get the values of the chosen point in the scatterplot'''
        if self.annotation_mode == True:
            print('annotation mode is true on_click')
            self.x1 = event.mouseevent.xdata
            self.y1 = event.mouseevent.ydata
            index = event.ind
            marker = event.artist
            x = np.take(marker.get_xdata(), index)
            y = np.take(marker.get_ydata(), index)

            point = {'x': x[0], 'y' : y[0]}
            print('point on_click = ', point)

            for i in range(0, len(self.columns)):
                if self.is_in_array(point, self.columns[i]):
                    print('the point ', point, ' is in array', i+1)
                    self.coords.append(point)
                    self.annotate_this()

            self.annotation_mode = False

    def on_press(self, event):
        ''' Get the starting mouse coordinates of a rectangular selection'''
        if self.annotation_mode == True:
            print('annotation mode is true on_press')
            self.x1 = event.xdata
            self.y1 = event.ydata
            print('on_press')

    def on_release(self, event):
        ''' Get the ending mouse coordinates of a rectangular selection'''
        if self.annotation_mode == True:
            self.x2 = event.xdata
            self.y2 = event.ydata
            print('on_release')
            print('x equals', self.x2, self.x1)
            print('y equals', self.y2, self.y1)

            # Check that this is not a single clicked point.
            # Do stuff for a dragged rectangular selection.
            if self.x1 != self.x2 or self.y1 != self.y2:
                for i in range(0, len(self.columns)):
                    self.is_in_rectangle(self.columns[i])

                if len(self.coords) > 0:
                    self.annotate_this()

                self.annotation_mode = False

    def colouring_in(self):
        ''' Colour in the points that have been annotated '''
        x_coords = []
        y_coords = []
        for i in range(len(self.annotated)):
            x_coords.append(self.annotated[i]['x'])
            y_coords.append(self.annotated[i]['y'])

        # Clear away previous plot.  Otherwise they just accumulate.
        self.fig1.clf()
        # Redraw original plots.
        for i in range(0, len(self.columns)):
            self.plot_list.append(plt.plot(self.hours, self.columns[i], color=self.colours[i], linestyle='None', marker='o', markersize=2, picker=3))
            

        # Create an additional plot which contains all of the annotated points.
        # This is overlaid on the original plots.
        # This is an inefficient way to accomplish the task, but the only one I could find that works.
        self.plot_selected = plt.plot(x_coords, y_coords, color='#ff1654', linestyle='None', marker='o', markersize=2, picker=3)    # plot overlay
        self.fig1.canvas.draw()     # redraw the canvas with plot overlay

    def annotate_this(self):
        '''
        Pop-up window for annotation management.
        Currently, the user could create more than one of these.  Future fix.
        '''
        popup = tk.Tk()
        popup.wm_title('Annotation')
        text_box = tk.Text(popup, width=60, height=20)
        btn_add = tk.Button(popup, text='Add', command=lambda: self.add_annotation(text_box.get('0.0', 'end-1c')))
        btn_remove = tk.Button(popup, text='Remove', command=lambda: self.remove_annotation(text_box.delete('1.0', tk.END)))
        btn_cancel = tk.Button(popup, text='Close Window', command=popup.destroy)

        # If the selected points are already annotated, display the annotations.
        if len(self.annotated) > 0:
            annotation_text = self.get_annotations()
            text_box.insert(tk.END, annotation_text)

        # draw the gui components
        text_box.grid(row=0, column=0, rowspan=1, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        btn_add.grid(row=1, column=0, rowspan=1, columnspan=1, sticky=tk.E, padx=5, pady=5)
        btn_remove.grid(row=1, column=1, rowspan=1, columnspan=1, sticky=tk.E, padx=5, pady=5)
        btn_cancel.grid(row=1, column=2, rowspan=1, columnspan=1, sticky=tk.E, padx=5, pady=5)
        popup.mainloop()

    def add_annotation(self, text):
        ''' Add annotated things to a separate list.  Clear the list of currently selected coordinates.'''
        self.annotated.extend(self.coords)
        for i in range(len(self.annotated)):
            if 'annotation' not in self.annotated[i]:
                self.annotated[i]['annotation'] = text
        print('annotated coordinates = ', self.annotated)
        self.colouring_in()
        self.coords = []

    def remove_annotation(self, text):
        ''' Remove annotation from selected points.'''
        for i in range(len(self.coords)):
            for j in range(len(self.annotated)):
                if (self.coords[i]['x'] == self.annotated[j]['x']) and (self.coords[i]['y'] == self.annotated[j]['y']):
                    print('self.annotated[j]: ', self.annotated[j])
                    print('self.coords[i]: ', self.coords[i])
                    del self.annotated[j]
                    break
        self.colouring_in()
        self.coords = []

    def get_annotations(self):
        ''' Get existing annotations for selected points.'''
        string = ''
        for i in range(len(self.coords)):
            for j in range(len(self.annotated)):
                if (self.coords[i]['x'] == self.annotated[j]['x']) and (self.coords[i]['y'] == self.annotated[j]['y']):
                    x = 'x:' + str(self.annotated[j]['x'])
                    y = 'y:' + str(self.annotated[j]['y'])
                    string = string + x + ' ' + y + ' - ' + self.annotated[j]['annotation'] + '\n'
        return string

# draw!
PLOT = AnnotateablePlot()
