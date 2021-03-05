import numpy as np
import math
import random
import json
import matplotlib.pyplot as plt
import matplotlib.animation as anim


class Simulation2():
    def __init__(self):
        self.choices = { \
                            "D": ["test"], \
                            "V": [self.VisualizationInit, self.VisualizationUpdate], \
                            "R": [None, self.RandomUpdate], \
                            "G": ["test3"], \
                            "O": ["test3"]
                        }

    def Start(self):
        # Default lattice size and amount of loops
        self.size = 50
        self.loops = 10000

        # Asks user which branch to run
        data_collection_choice = Simulation.ParseChoices("Run Visualisation or Data Collection? [V/D]: ", ["V", "D"])
        self.conditions_choice = Simulation.ParseChoices("Random, Glider, or Oscillator? [R/G/O]: ", ["R", "G", "O"])

        # Attempts to call the visualization or data collection initializer by referencing the choice dictionary
        try: 
            self.choices[data_collection_choice.capitalize()][0]()
        except:
            pass

        # Runs the update loop of visualization or data collection
        self.choices[data_collection_choice.capitalize()][1]()
            
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
        self.size = Simulation.ParseInput("Specify the size of the lattice: ", int)
        self.loops = Simulation.ParseInput("MonteCarlo loops: ", int)

        self.grid = np.zeros((self.size, self.size))
        self.grid[24,26] = 1
        self.grid[25,26] = 1
        self.grid[26,26] = 1
        #self.grid = np.random.choice([-1,1], size=(self.size, self.size))

    # Controls the display of data
    def VisualizationUpdate(self):
        figure, self.data_points = Simulation.CreateFigure(self.size)
        self.animation = anim.FuncAnimation(figure, func=self.Animate, frames=self.LoopFunction, interval=10, blit=False, repeat=False)
        plt.show()

    # Updates the heatmap with the new spins
    def Animate(self, grid):
        self.data_points.set_data(grid)
        return self.data_points

    # Creates a heatmap in matplotlib of the spins
    @staticmethod
    def CreateFigure(size):
        figure, axes = plt.subplots()
        axes.set_xlabel("X")
        axes.set_ylabel("Y")
        data_points = axes.imshow(np.zeros((size, size)), vmin=-1, vmax=1)
        return figure, data_points

    # Loops through the dynamics Markov chains and Metropolis Algorithm
    def LoopFunction(self):
        for _ in range(self.loops):
            # Calls the update function of either Glauber or Kawasaki dynamics
            self.choices[self.conditions_choice.capitalize()][1]()
            yield self.grid


    def RandomUpdate(self):
        self.GameOfLife()

    def GameOfLife(self):
        next_step = self.grid
        for i in range(self.size):
            next_i = (i + 1) % self.size
            last_i = (i - 1) % self.size
            for j in range(self.size):
                next_j = (j + 1) % self.size
                last_j = (j - 1) % self.size
                neighbors = np.array([self.grid[next_i, j], self.grid[next_i, next_j], self.grid[i, next_j], \
                                     self.grid[last_i, next_j], self.grid[last_i, j], self.grid[last_i, last_j], \
                                     self.grid[i, last_j], self.grid[next_i, last_j]])
                occurrences = np.count_nonzero(neighbors == 1)
                if (self.grid[i, j] == 1):
                    if (occurrences < 2) or (occurrences > 3):
                        next_step[i, j] = 0
                elif (occurrences == 3):
                    next_step[i, j] = 1
        self.grid = next_step




# Simulation class which contains all functions
class Simulation():
    def __init__(self):
        # Dictionary of the choices by the user on runtime that maps which branch of the program to run
        self.choices = { \
                            "G": [self.GlauberInit, self.GlauberUpdate], \
                            "K": [None, self.KawasakiUpdate], \
                            "D": [None, self.DataCollectionUpdate], \
                            "V": [self.VisualizationInit, self.VisualizationUpdate] \
                        }
        # Initializing json object for data storage
        self.json_object = {}
        self.json_object[TEMPERATURE] = []
        self.json_object[ENERGY] = []
        self.json_object[MAGNETIZATION] = []
        self.json_object[SPECIFIC_HEAT] = []
        self.json_object[SUSCEPTIBILITY] = []
        self.json_object[C_ERROR] = []           

    def Start(self):
        # Default lattice size and amount of loops
        self.size = 50
        self.loops = 10000

        # Asks user which branch to run
        self.dynamics_choice = Simulation.ParseChoices("Simulate using Glauber or Kawasaki dynamics? [G/K]: ", ["G", "K"])
        data_collection_choice = Simulation.ParseChoices("Run Visualisation or Data Collection? [V/D]: ", ["V", "D"])

        # Attempts to call the visualization or data collection initializer by referencing the choice dictionary
        try: 
            self.choices[data_collection_choice.capitalize()][0]()
        except:
            pass

        # Default sets the grid to a random selection of 1 or -1, will change to all 1s or -1s if Glauber Data Collection is run
        self.grid = np.random.choice([-1,1], size=(self.size, self.size))

        # Runs the update loop of visualization or data collection
        self.choices[data_collection_choice.capitalize()][1]()
            
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

################### Functions that control the live visualization ###################

    # Gets user input for visualization parameters
    def VisualizationInit(self):
        self.size = Simulation.ParseInput("Specify the size of the lattice: ", int)
        self.temp = Simulation.ParseInput("Enter a temperture value for the simulation: ", float)
        self.loops = Simulation.ParseInput("MonteCarlo loops: ", int)

    # Controls the display of data
    def VisualizationUpdate(self):
        figure, self.data_points = Simulation.CreateFigure(self.size)
        self.animation = anim.FuncAnimation(figure, func=self.Animate, frames=self.LoopFunction, interval=10, blit=False, repeat=False)
        plt.show()

    # Updates the heatmap with the new spins
    def Animate(self, grid):
        self.data_points.set_data(grid)
        return self.data_points

    # Creates a heatmap in matplotlib of the spins
    @staticmethod
    def CreateFigure(size):
        figure, axes = plt.subplots()
        axes.set_xlabel("X")
        axes.set_ylabel("Y")
        data_points = axes.imshow(np.zeros((size, size)), vmin=-1, vmax=1)
        return figure, data_points

    # Loops through the dynamics Markov chains and Metropolis Algorithm
    def LoopFunction(self):
        for _ in range(self.loops):
            # Calls the update function of either Glauber or Kawasaki dynamics
            self.choices[self.dynamics_choice.capitalize()][1]()
            yield self.grid

################### Functions that control the full temperature range data collection ###################

    # Controls the progression through the temperatures [1,3] and saves data gathered to a json file
    def DataCollectionUpdate(self):
        print("Running data collection...")
        try: 
            # Corrects the spins to all up or down if Glauber is being used
            self.choices[self.dynamics_choice.capitalize()][0]()
        except:
            pass
        
        temperatures = np.linspace(1.0, 3.0, num=21)
        self.json_object[TEMPERATURE] = temperatures.tolist()

        for temp in temperatures:
            self.temp = temp
            self.SetData()
            print("Data collected for temperature:", temp)

        self.SaveData(self.json_path)
        self.PlotData(self.json_path)

    def SetData(self):
        # Creates arrays for average calculations over all loops
        self.energies = np.array([])
        self.magnetizations = np.array([])

        # Sets the update loop of either Glauber or Kawasaki
        update = self.choices[self.dynamics_choice.capitalize()][1]

        for i in range(self.loops + 100):
            # Runs the update loop that was set before the for loop
            update()
            # Waits for equilibrium and samples with autocorrection time of 10
            if i >= 100 and i % 10 == 0:
                self.energies = np.append(self.energies, self.TotalEnergy())
                self.magnetizations = np.append(self.magnetizations, self.TotalMagnetization())

        # Calculates and saves all important data to the json object
        self.json_object[ENERGY].append(np.average(self.energies))
        self.json_object[MAGNETIZATION].append(np.average(np.abs(self.magnetizations)))
        self.json_object[SPECIFIC_HEAT].append(Simulation.SpecificHeat(self.energies, self.size, self.temp))
        self.json_object[SUSCEPTIBILITY].append(Simulation.Susceptibility(self.magnetizations, self.size, self.temp))
        self.json_object[C_ERROR].append(Simulation.BootStrap(self.energies, self.size, self.temp))

    # Writes to a json file
    def SaveData(self, file_path):
        with open(file_path, 'w') as outfile:
            json.dump(self.json_object, outfile)

    # Plots gathered data by reading json file
    def PlotData(self, file_path):
        with open(file_path) as json_file:
            # Load the json object from the file
            j = json.load(json_file)
            temps = j.get(TEMPERATURE)

            Simulation.FormatPlot(plt.plot(temps, j.get(MAGNETIZATION)), "Magnetisation", "Temperature", "Average Magnetisation")
            Simulation.FormatPlot(plt.plot(temps, j.get(SUSCEPTIBILITY)), "Susceptibility", "Temperature", "Susceptibility")
            Simulation.FormatPlot(plt.plot(temps, j.get(ENERGY)), "Energy", "Temperature", "Average Energy")
            Simulation.FormatPlot((plt.plot(temps, j.get(SPECIFIC_HEAT)), plt.errorbar(temps, j.get(SPECIFIC_HEAT), yerr=j.get(C_ERROR), fmt='none')), "Specific Heat", "Temperature", "Specific Heat")
            print("Finished")

    # Function that allows for many plots to be made in less space
    @staticmethod
    def FormatPlot(plot, title, x_axis, y_axis):
        plt.title(title)
        plt.xlabel(x_axis)
        plt.ylabel(y_axis)
        plt.show()

################### Functions for the Markov Chains and Metropolis algorithm ###################

    # Sets initial spins to all 1s if necessary
    def GlauberInit(self):
        self.grid = np.ones((self.size, self.size))

    # Performs Markov chain for Glauber dynamics
    def GlauberUpdate(self):
        for _ in range(self.size**2):
            # Selects a random spin
            x = random.randint(0,self.size-1)
            y = random.randint(0,self.size-1)

            #Performs Metropolis Test
            delta_e = self.DeltaE(x, y)
            if delta_e <= 0 or random.random() <= math.exp(-delta_e/self.temp):
                self.grid[y, x] *= -1

    # Performs Markov chain for Kawasaki dynamics
    def KawasakiUpdate(self):
        for _ in range(self.size**2):
            # Selects two different spins randomly from the grid
            x1, y1, x2, y2 = self.RandomSpinSelector()

            # Performs Metropolis Test
            delta_e = self.DeltaE(x1, y1) + self.DeltaE(x2, y2)
            if (abs(x1 - x2) <= 1 and abs(y1 - y2) == 0) or (abs(x1 - x2) == 0 and abs(y1 - y2) <= 1):
                delta_e -= self.grid[y1, x1] + self.grid[y2, x2]
            if delta_e <= 0 or random.random() <= math.exp(-delta_e/self.temp):
                self.grid[y1, x1] *= -1
                self.grid[y2, x2] *= -1

    # General formula for change in E given one changed spin
    def DeltaE(self, x, y):
        return 2 * self.grid[y, x] \
            * (self.grid[(y + 1) % self.size, x] + self.grid[(y - 1)  % self.size, x] \
            + self.grid[y, (x + 1)  % self.size] + self.grid[y, (x - 1)  % self.size])

    # Selects two spins and verifies they are different before returning their positions
    def RandomSpinSelector(self):
        x1 = random.randint(0,self.size-1)
        y1 = random.randint(0,self.size-1)            
        x2 = random.randint(0,self.size-1)
        y2 = random.randint(0,self.size-1)
        if self.grid[y1, x1] == self.grid[y2, x2]:
            return self.RandomSpinSelector()
        else:
            return x1, y1, x2, y2

################### General formula functions ###################

    # Calculates total energy of the system at a given state
    def TotalEnergy(self):
        energy = 0
        for i in range(self.size):
            for j in range(self.size):
                if i != self.size - 1:
                    i_over = i + 1
                else:
                    i_over = 0
                if j != self.size - 1:
                    j_above = j + 1
                else:
                    j_above = 0
                energy += - self.grid[i, j] * (self.grid[i, j_above] + self.grid[i_over, j])
        return energy

    # Simply sums over the passed grid
    def TotalMagnetization(self):
        return np.sum(self.grid)    

    # Formula for specific heat
    @staticmethod
    def SpecificHeat(energies, size, temp):
        e_squared = energies ** 2
        average_e = np.average(energies)
        return ( np.average(e_squared) - average_e**2 ) / ( size**2 * temp**2)

    # Formula for susceptibility
    @staticmethod
    def Susceptibility(magnetizations, size, temp):
        m_squared = magnetizations ** 2
        average_m = np.average(magnetizations)
        return ( np.average(m_squared) - average_m**2 ) / ( size**2 * temp)

    # Bootstrap method for calculating error of specific heat
    @staticmethod
    def BootStrap(measurements, size, temp):
        resampled_specific_heats = np.array([])
        for _ in range(500):
            # Randomly chooses n measurments from n given measurements with repeats allowed
            resampled_data = np.random.choice(measurements, len(measurements))
            # Calculates the resampled specific heat
            new_c = Simulation.SpecificHeat(resampled_data, size, temp)
            resampled_specific_heats = np.append(resampled_specific_heats, new_c)
        # Finds the standard deviation of 500 resampled specific heats
        return np.sqrt( np.average(resampled_specific_heats**2) - np.average(resampled_specific_heats)**2 )

# Creates a simulation object
sim = Simulation2()
sim.json_path = "data.jsonc"

# Uncomment this line and comment the below line to run the simulation with either live visualization or full data collection
sim.Start()

# Uncomment this line and comment the above line to just plot already collected data from sim.json_path which you can specify above
#sim.PlotData(sim.json_path)