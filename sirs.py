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

class State(IntEnum):
    # Remember to update all member variables
    # and functions if another state is added.
    S = 1
    I = 2
    R = 3

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
        return np.array([1 + 1 / 3, 2, 2 + 2 / 3])


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

    def Start(self):
        #self.mode = SIRModel.ParseChoices("Data collection or visualization? [D/V]: ", ["D", "V"])
        #self.size = SIRModel.ParseInput("Enter size of the lattice: ", int)
        #self.loops = SIRModel.ParseInput("MonteCarlo loops: ", int)
        #self.p_infection = SIRModel.ParseProbability("Enter probability of infection (p1): ", float)
        #self.p_recovery = SIRModel.ParseProbability("Enter probability of recovery (p2): ", float)
        #self.p_immunity_loss = SIRModel.ParseProbability("Enter probability of loss of immunity (p3): ", float)

        self.mode = "V"
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
    




    def InitRandomGrid(self):
        self.grid = np.random.choice(a=[int(State.S), int(State.I), int(State.R)], size=(self.size, self.size))

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
        self.DataUpdate()

    def DataUpdate(self):
        for _ in range(self.loops):
            self.InitRandomGrid()
            condition = True
            # TODO: Change later to termination condition.
            while condition:
                self.UpdateInfections()
                print(self.infected)
                # condition = True






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






    def SaveData(self, filepath):
        with open(filepath, 'w') as outfile:
            json.dump(self.json_data, outfile)

    def PlotData(self, filepath):
        with open(filepath) as json_file:
            j = json.load(json_file)
            # TODO:
            # Extract data
            # Call plot function(s)
            print("Finished plotting data!")




sim = SIRModel()
sim.json_path = "data.jsonc"

sim.Start()