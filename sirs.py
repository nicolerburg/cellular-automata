import numpy as np
import math
import random
import json
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import matplotlib.colors as clr
import matplotlib.ticker as tkr
from enum import IntEnum

INFECTED_FRACTIONS = "Infected Fractions"
INFECTED_FRACTIONS_VARIANCE = "Infected Fractions Variance"

SLICE_INFECTED_FRACTIONS = "Sliced Infected Fractions"
SLICE_INFECTED_FRACTIONS_VARIANCE = "Sliced Infected Fractions Variance"
SLICE_INFECTED_FRACTIONS_ERROR = "Sliced Infected Fractions Error"

VACCINATED_INFECTED_FRACTIONS = "Vaccinated Infected Fraction"
VACCINATED_INFECTED_FRACTIONS_ERROR = "Vaccinated Infected Fractions Error"

SAMPLES = 1000
SLICED_SWEEPS = 10000
EQUILIBRIUM_TIME = 100
RESOLUTION = 25

class State(IntEnum):
    # Remember to update all member variables
    # and functions if another state is added.
    S = 1
    I = 2
    R = 3
    V = 4

    minimum = S
    maximum = R

    @staticmethod
    def labels():
        return ["Susceptible", "Infected", "Recovered"]
    
    @staticmethod
    def colors():
        return ["white", "firebrick", "cornflowerblue"]

    @staticmethod
    def bins():
        return np.array([0, State.S, State.I, State.R]) + 0.5

    @staticmethod
    def tickz():
        return np.array([1 + 1/ 3, 2, 2 + 2 / 3])


class SIRModel():
    def __init__(self):
        self.choices = {
            "D": [self.DataInit],
            "V": [self.VisualizationInit],
            "A": [self.SetConditions, (50, 0.2, 0.3, 0.1)],
            "E": [self.SetConditions, (50, 0.7, 0.7, 0.7)],
            "W": [self.SetConditions, (100, 0.8, 0.1, 0.01)],
            "C": [self.UserConditions, ()]
        }
        self.json_data = {}
        self.json_data[INFECTED_FRACTIONS] = []
        self.json_data[INFECTED_FRACTIONS_VARIANCE] = []

        self.json_data[SLICE_INFECTED_FRACTIONS] = []
        self.json_data[SLICE_INFECTED_FRACTIONS_VARIANCE] = []
        self.json_data[SLICE_INFECTED_FRACTIONS_ERROR] = []

        self.json_data[VACCINATED_INFECTED_FRACTIONS] = []
        self.json_data[VACCINATED_INFECTED_FRACTIONS_ERROR] = []

    def Start(self):
        self.mode = SIRModel.ParseChoices("Data collection or visualization? [D/V]: ", ["D", "V"])
        #self.size = SIRModel.ParseInput("Enter size of the lattice: ", int)
        #self.loops = SIRModel.ParseInput("MonteCarlo loops: ", int)
        #self.p_infection = SIRModel.ParseProbability("Enter probability of infection (p1): ", float)
        #self.p_recovery = SIRModel.ParseProbability("Enter probability of recovery (p2): ", float)
        #self.p_immunity_loss = SIRModel.ParseProbability("Enter probability of loss of immunity (p3): ", float)

        #self.mode = "D"
        # self.size = 50
        # self.p_infection = 0.7
        # self.p_recovery = 0.7
        # self.p_immunity_loss = 0.7
        self.loops = 500

        self.choices[self.mode][0]()




    @staticmethod
    def ParseProbability(prompt, type):
        probability = SIRModel.ParseInput(prompt, type)
        if probability > 1.0:
            print("Probability can not exceed 1.0")
            return SIRModel.ParseProbability(prompt, type)
        return probability

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
        return SIRModel.ParseInput(prompt, type)
    
    @staticmethod
    def ParseChoices(prompt, options):
        user_input = input(prompt)
        if user_input.capitalize() in options:
            return user_input.capitalize()
        else:
            return SIRModel.ParseChoices(prompt, options)

    @staticmethod
    def CreateFigure(size):
        figure, axes = plt.subplots()
        axes.set_xlabel("X")
        axes.set_ylabel("Y")

        labels = State.labels()
        boundary = clr.BoundaryNorm(State.bins(), len(labels), clip=True)

        graph = axes.imshow(np.zeros((size, size)), \
        cmap=ListedColormap(State.colors()), \
        vmin=State.minimum, \
        vmax=State.maximum)

        figure.colorbar(graph, \
        format=tkr.FuncFormatter(lambda x, pos: labels[boundary(x)]), \
        ticks=State.tickz())

        return figure, axes, graph






    def Animate(self, grid):
        self.graph.set_data(grid)
        self.axes.set_title( \
            "Susceptible: " + str(self.susceptible) \
            + ", Infected: " + str(self.infected) \
            + ", Recovered: " + str(self.recovered))
        return self.graph

    def FrameFunction(self):
        for _ in range(self.loops):
            # TODO: May need to switch to 
            # self.choices[self.mode][1]()
            self.VisualizationUpdate()
            yield self.grid
    




    def InitRandomGrid(self, definite_immunity = 0):
        probability = (1 - definite_immunity) / 3
        self.grid = np.random.choice(a=[int(State.S), int(State.I), int(State.R), int(State.V)], size=(self.size, self.size), p=[probability, probability, probability, definite_immunity])

    def SetConditions(self, size, p_1, p_2, p_3):
        self.size = size
        self.p_infection = p_1
        self.p_recovery = p_2
        self.p_immunity_loss = p_3

    def UserConditions(self, *kargs):
        self.size = SIRModel.ParseInput("Enter size of the lattice: ", int)
        self.loops = SIRModel.ParseInput("MonteCarlo loops: ", int)
        self.p_infection = SIRModel.ParseProbability("Enter probability of infection (p1): ", float)
        self.p_recovery = SIRModel.ParseProbability("Enter probability of recovery (p2): ", float)
        self.p_immunity_loss = SIRModel.ParseProbability("Enter probability of loss of immunity (p3): ", float)





    def VisualizationInit(self):
        conditions = SIRModel.ParseChoices("Absorption, Equilibrium, Wave, or Custom? [A/E/W/C]: ", ["A", "E", "W", "C"])
        self.choices[conditions][0](*self.choices[conditions][1])
        self.InitRandomGrid()

        self.figure, self.axes, self.graph = SIRModel.CreateFigure(self.size)
        self.animation = anim.FuncAnimation(self.figure, func=self.Animate, frames=self.FrameFunction, interval=10, blit=False, repeat=False)
        plt.show()

    def VisualizationUpdate(self):
        self.UpdateInfections()




    def DataInit(self):
        # TODO: Add data specific variables here
        collection_choice = SIRModel.ParseChoices("Fraction of Infected & Sliced, or Permanent Immunity? [F/P]: ", ["F", "P"])
        self.size = 50
        if collection_choice == "F":
            self.DataUpdate()
        elif collection_choice == "P":
            start_state = SIRModel.ParseChoices("Equillibrium or Large Lattice? [E/L]: ", ["E", "L"])
            if start_state == "L":
                self.size = 100
                self.VaccinatedData(0.8, 0.1, 0.02)
            elif start_state == "E":
                self.VaccinatedData(0.5, 0.5, 0.5)


    def DataUpdate(self):
        print(np.linspace(0,1,RESOLUTION))

        # Slice of p_2 = 0.5 p_3 = 0.5 and 0.2 <= p_1 <= 0.5
        for p_1 in np.linspace(0.2, 0.5, RESOLUTION):
            self.average_array = []
            self.variance_array = []
            self.DataSlice(SLICED_SWEEPS, p_1, 0.5, 0.5)
            self.json_data[SLICE_INFECTED_FRACTIONS].append(self.average_array[0])
            self.json_data[SLICE_INFECTED_FRACTIONS_VARIANCE].append(self.variance_array[0])
            self.json_data[SLICE_INFECTED_FRACTIONS_ERROR].append(self.BootStrap(self.total_infected))
            #print(p_1)
        self.SaveData("sliced_data.jsonc")
        self.PlotSlicedData("sliced_data.jsonc")

        # Slice of p_2 = 0.5 and 0 <= p_1,p_3 <= 1
        for p_1 in np.linspace(0,1,RESOLUTION):
            self.average_array = []
            self.variance_array = []
            for p_3 in np.linspace(0,1,RESOLUTION):
                self.DataSlice(SAMPLES, p_1, 0.5, p_3)
            self.json_data[INFECTED_FRACTIONS].append(self.average_array)
            self.json_data[INFECTED_FRACTIONS_VARIANCE].append(self.variance_array)
            #print(p_1)
        self.SaveData("phase_data.jsonc")
        self.PlotData("phase_data.jsonc")

    def VaccinatedData(self, p_1, p_2, p_3):
        for i in np.linspace(0, 1, RESOLUTION):
            print("p_1", i)
            values = []
            #standard_error_mean = []
            for j in range(5):
                print("Loop", j)
                self.average_array = []
                self.variance_array = []
                self.DataSlice(SAMPLES, p_1, p_2, p_3, vaccinated_fraction=i)
                values.append(self.average_array[0])
            
            std = np.std(np.asarray(values))
            #standard_error_mean.append( std / math.sqrt(5) )
            self.json_data[VACCINATED_INFECTED_FRACTIONS].append(self.average_array[0])
            self.json_data[VACCINATED_INFECTED_FRACTIONS_ERROR].append(std / math.sqrt(5))
            print(i)
        self.SaveData("vaccinated_data.jsonc")
        self.PlotVaccinatedData("vaccinated_data.jsonc")
            

    def UpdateInfections(self):
        self.infected = 0
        self.recovered = 0
        self.susceptible = 0
        for _ in range(self.size * self.size):
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            dice = random.random()
            state = self.grid[y][x]
            if state == State.S:
                if dice <= self.p_infection and self.HasInfectedNear(x, y):
                    self.grid[y][x] = State.I
                    self.infected += 1
                else:
                    self.susceptible += 1
            elif state == State.I:
                if dice <= self.p_recovery:
                    self.grid[y][x] = State.R
                    self.recovered += 1
                else:
                    self.infected += 1
            elif state == State.R:
                if dice <= self.p_immunity_loss:
                    self.grid[y][x] = State.S
                    self.susceptible += 1
                else:
                    self.recovered += 1

    def HasInfectedNear(self, x, y):
        for i in range(x - 1, x + 1):
            for j in range(y - 1, y + 1):
                if self.grid[j % self.size][i % self.size] == State.I:
                    return True
        return False

    def DataSlice(self, sweeps, p_1, p_2, p_3, vaccinated_fraction = 0):
        sum = 0
        squared_sum = 0
        # Array to store the number affected over all sweeps
        self.total_infected = []
        self.SetConditions(self.size, p_1, p_2, p_3)
        self.InitRandomGrid(definite_immunity = vaccinated_fraction)
        for i in range(sweeps + EQUILIBRIUM_TIME):
            # Runs the update loop that was set before the for loop
            self.UpdateInfections()
            if self.infected == 0:
                break
            # Waits for equilibrium and samples with autocorrection time of 10
            if i >= EQUILIBRIUM_TIME:
                self.total_infected.append(self.infected)
                sum += self.infected
                squared_sum += self.infected**2
        average = sum / sweeps
        squared_average = squared_sum / sweeps
        self.average_array.append(average / (self.size**2))
        self.variance_array.append((squared_average - average**2) / (self.size**2))


    def BootStrap(self, measurements):
        resampled_variance = np.array([])
        for _ in range(500):
            # Randomly chooses n measurements from n given measurements with repeats allowed
            resampled_data = np.random.choice(measurements, len(measurements))
            # Calculates the resampled variance
            new_variance = ( np.average(np.square(resampled_data)) - np.average(resampled_data)**2 ) / (self.size**2)
            resampled_variance = np.append(resampled_variance, new_variance)
        # Finds the standard deviation of 500 resampled specific heats
        return np.std(resampled_variance)



    def SaveData(self, filepath):
        with open(filepath, 'w') as outfile:
            json.dump(self.json_data, outfile)

    def PlotSlicedData(self, filepath):
        with open(filepath) as json_file:
            j = json.load(json_file)
            sliced_variance = j.get(SLICE_INFECTED_FRACTIONS_VARIANCE)

            #plt.scatter(np.linspace(0.2, 0.5, RESOLUTION), sliced_variance)
            plt.errorbar(np.linspace(0.2, 0.5, RESOLUTION), sliced_variance, yerr=j.get(SLICE_INFECTED_FRACTIONS_ERROR), capsize = 5, fmt='none')
            plt.title("Variance of Infected Sites")
            plt.xlabel("Probability of Infection (p_1)")
            plt.ylabel("Variance")
            plt.show()
            # TODO:
            # Extract data
            # Call plot function(s)
            print("Finished plotting data!")

    def PlotVaccinatedData(self, filepath):
        with open(filepath) as json_file:
            j = json.load(json_file)
            v_infected_fractions = j.get(VACCINATED_INFECTED_FRACTIONS)
            fractions_error = j.get(VACCINATED_INFECTED_FRACTIONS_ERROR)

            plt.scatter(np.linspace(0, 1, RESOLUTION), v_infected_fractions, marker=".")
            plt.errorbar(np.linspace(0, 1, RESOLUTION), v_infected_fractions, yerr=fractions_error, capsize = 5, fmt='none')
            plt.title("Minimal Immune Fraction")
            plt.xlabel("Fraction of Immunity")
            plt.ylabel("Average Infected Fraction")
            plt.show()
            # TODO:
            # Extract data
            # Call plot function(s)
            print("Finished plotting data!")

    def PlotData(self, filepath):
        with open(filepath) as json_file:
            j = json.load(json_file)
            infected_fractions = j.get(INFECTED_FRACTIONS)
            variance = j.get(INFECTED_FRACTIONS_VARIANCE)

            plt.imshow(infected_fractions, extent=[0,1,0,1])
            plt.title("Phase Diagram")
            plt.xlabel("Probability of Infection (p_1)")
            plt.ylabel("Probability of Losing Immunity (p_3)")
            plt.show()

            plt.contour(variance, extent=[0,1,0,1])
            plt.title("Variance Contour")
            plt.xlabel("Probability of Infection (p_1)")
            plt.ylabel("Probability of Losing Immunity (p_3)")
            plt.show()
            # TODO:
            # Extract data
            # Call plot function(s)
            print("Finished plotting data!")





sim = SIRModel()
sim.json_path = "data.jsonc"

#sim.Start()

sim.PlotSlicedData("sliced_data.jsonc")