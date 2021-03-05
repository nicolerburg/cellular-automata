import numpy as np
import math
import random
import json
import matplotlib.pyplot as plt
import matplotlib.animation as anim

MONTE_CARLO_LOOPS = 200
MAX_SWEEPS = 6000

GLIDER_SWEEPS = 300

HISTOGRAM_DATA = "Histogram Data"
GLIDER_DATA = "Glider Data"

class Simulation():
    def __init__(self):
        self.choices = { \
                            "D": [self.DataCollectionInit, self.DataCollectionUpdate], \
                            "V": [self.VisualizationInit, self.VisualizationUpdate], \
                            "R": [self.RandomGrid, self.RandomDataCollection], \
                            "G": [self.GliderGrid, self.GliderDataCollection], \
                            "O": [self.OscillatorGrid, None]
                        }

    def Start(self):
        # Asks user which branch to run
        mode = Simulation.ParseChoices("Run Visualisation or Data Collection? [V/D]: ", ["V", "D"])
        self.size = Simulation.ParseInput("Specify the size of the lattice: ", int)

        self.grid = np.zeros((self.size, self.size))

        # Attempts to call the visualization or data collection initializer by referencing the choice dictionary
        self.choices[mode.capitalize()][0]()

        # Runs the update loop of visualization or data collection
        self.choices[mode.capitalize()][1]()
            
    # Functions which parse input
    @staticmethod
    def ParseInput(prompt, type):
        try:
            user_input = type(input(prompt))
            if user_input > 0:
                return user_input
            else:
                print("Please enter a value greater than zero.")
        except:
            pass
        return Simulation.ParseInput(prompt, type)

    @staticmethod
    def ParseChoices(prompt, options):
        user_input = input(prompt)
        if user_input.capitalize() in options:
            return user_input
        else:
            return Simulation.ParseChoices(prompt, options)


    # Gets user input for visualization parameters
    def VisualizationInit(self):
        self.loops = Simulation.ParseInput("Loops: ", int)
        conditions_choice = Simulation.ParseChoices("Random, Glider, or Oscillator? [R/G/O]: ", ["R", "G", "O"])


        self.choices[conditions_choice.capitalize()][0]()
        # self.grid = np.zeros((self.size, self.size))
        # self.grid[5,5] = 1
        # self.grid[5,6] = 1
        # self.grid[5,7] = 1
        #self.grid[4,6] = 2
        #print(self.grid)
        #plt.imshow(self.grid, vmin=0, vmax=1, interpolation = "nearest")
        #plt.show()

    # Controls the display of data
    def VisualizationUpdate(self):
        figure, self.data_points, self.axes = Simulation.CreateFigure(self.size)
        self.animation = anim.FuncAnimation(figure, func=self.Animate, frames=self.LoopFunction, interval=200, blit=False, repeat=False)
        plt.show()

    # Updates the heatmap with the new spins
    def Animate(self, grid):
        self.data_points.set_data(grid)
        self.axes.set_title("Active Sites: "+str(self.active_sites))
        return self.data_points

    # Creates a heatmap in matplotlib of the spins
    @staticmethod
    def CreateFigure(size):
        figure, axes = plt.subplots()
        axes.set_xlabel("X")
        axes.set_ylabel("Y")
        data_points = axes.imshow(np.zeros((size, size)), cmap= "Greys", vmin=0, vmax=1, interpolation = "nearest")
        return figure, data_points, axes

    def LoopFunction(self):
        for _ in range(self.loops):
            self.GameOfLife()
            yield self.grid

    def DataCollectionInit(self):
        self.conditions_choice = Simulation.ParseChoices("Random or Glider? [R/G]: ", ["R", "G"])

        self.choices[self.conditions_choice.capitalize()][0]()

    def DataCollectionUpdate(self):
        self.choices[self.conditions_choice.capitalize()][1]()

    def RandomDataCollection(self):
        self.json_object = {}
        self.json_object[HISTOGRAM_DATA] = []
        self.active_sites= 0
        for i in range(MONTE_CARLO_LOOPS):
            self.RandomGrid()
            counter = 0
            for j in range(MAX_SWEEPS):
                previous_sites = self.active_sites
                self.GameOfLife()
                if self.active_sites == previous_sites:
                    counter += 1
                else:
                    counter = 0
                if counter == 10:
                    self.json_object[HISTOGRAM_DATA].append(j)
                    break
            print(i)
        print(self.json_object[HISTOGRAM_DATA])
        self.SaveData("histogram_data.jsonc")
        self.PlotData("glider_data.jsonc","histogram_data.jsonc")

    def GliderDataCollection(self):
        self.json_object = {}
        self.json_object[GLIDER_DATA] = [[],[]]
        for k in range(GLIDER_SWEEPS + 1):
            print(k)
            self.GameOfLife()
            if (k % 10) == 0:
                current_positions = [[],[]]
                for i in range(self.size):
                    for j in range(self.size):
                        if self.grid[i, j]:
                            current_positions[0].append(i)
                            current_positions[1].append(j)
                if (max(current_positions[0]) - min(current_positions[0])) <= (self.size/2) and (max(current_positions[1]) - min(current_positions[1])) <= (self.size/2):
                    self.json_object[GLIDER_DATA][0].append(sum(current_positions[1]) / len(current_positions[1]))
                    self.json_object[GLIDER_DATA][1].append(sum(current_positions[0]) / len(current_positions[0]))
        self.SaveData("glider_data.jsonc")
        self.PlotData("glider_data.jsonc", "histogram_data.jsonc")

    def RandomGrid(self):
        self.grid = np.random.choice([0,1], size=(self.size, self.size))

    def GliderGrid(self):
        x, y = (0, 0)

        glider = [\
            [0, 1, 0], \
            [0, 0, 1], \
            [1, 1, 1] \
            ]
        
        self.AddToGrid(glider, x, y)

    def OscillatorGrid(self):
        x, y = int(self.size / 2) - 6, int(self.size / 2) - 6

        oscillator = [ \
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0], \
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1], \
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1], \
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1], \
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0], \
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0], \
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1], \
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1], \
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1], \
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0], \
            ]

        self.AddToGrid(oscillator, x, y)

    def GameOfLife(self):
        next_step = np.copy(self.grid)
        self.active_sites = 0
        for i in range(self.size):
            for j in range(self.size):
                living_neighbors = self.CountNeighbors(i, j)
                next_step[i,j] = living_neighbors == 3 or (living_neighbors == 2 and self.grid[i,j])
                self.active_sites += next_step[i,j]
        self.grid = np.copy(next_step)

    def CountNeighbors(self,x, y):
        count = 0
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                count += self.grid[i % self.size, j % self.size]
        count -= self.grid[x, y]
        return count

    def AddToGrid(self, cells, x, y):
        for j in range(len(cells)):
            for i in range(len(cells[0])):
                self.grid[(j + y) % self.size, (i + x) % self.size] = cells[j][i]

    def SaveData(self, file_path):
        with open(file_path, 'w') as outfile:
            json.dump(self.json_object, outfile)

    def PlotData(self, file_path_glider, file_path_hist):
        with open(file_path_glider) as json_file:
            # Load the json object from the file
            j = json.load(json_file)
            glider_data = j.get(GLIDER_DATA)
            #histogram_data = j.get(HISTOGRAM_DATA)

            time = np.arange(0, GLIDER_SWEEPS, 10)

            x_slope = (glider_data[0][6] - glider_data[0][5]) / 10
            y_slope = (glider_data[1][6] - glider_data[1][5]) / 10

            speed = math.sqrt(x_slope**2 + y_slope**2)
            print("The speed of the glider is:", speed, "units per sweep")

            plt.scatter(time, glider_data[0], marker=".")
            plt.title("Glider Center of Mass Data")
            plt.xlabel("Time (sweeps)")
            plt.ylabel("X Position")
            plt.show()

            plt.scatter(time, glider_data[1], marker=".")
            plt.title("Glider Center of Mass Data")
            plt.xlabel("Time (sweeps)")
            plt.ylabel("Y Position")
            plt.show()

        with open(file_path_hist) as json_file:
            # Load the json object from the file
            j = json.load(json_file)
            hist_data = j.get(HISTOGRAM_DATA)
            plt.hist(hist_data, 60, density = True)
            plt.title("Random Starting State")
            plt.xlabel("Time to steady state (sweeps)")
            plt.ylabel("Probability Density")
            plt.show()
            print("Finished")

sim = Simulation()

file_path_glider = "glider_data.jsonc"
file_path_hist = "histogram_data.jsonc"

# Uncomment this line and comment the above line to just graph the plots from the paths supplied
#sim.PlotData(file_path_glider, file_path_hist)

# Uncomment this line and comment the below line to run the simulation with either live visualization or full data collection
sim.Start()