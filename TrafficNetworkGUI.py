import tkinter as tk
import numpy
import bisect
import time
import os
import threading
import sqlite3 as sql
from FiniteStateMachine import FSM
import random
import math
from tkinter import *

direction = {}
distance = {}
parent = {}
last = 0
direction[(1, 0)] = 2
direction[(0, -1)] = 1
direction[(-1, 0)] = 4
direction[(0, 1)] = 3
vehicleObject = []
lightObject = {}


def func(l, k, x0, x):
    val = math.exp(-k * (x - x0)) + 1.0
    return l * 1.0 / val


def calculateTime(congestion):
    duration = 0
    l = 50
    k = 0.8
    x0 = 2.0
    cong = int(congestion / 10)
    lRange = func(l, k, x0, cong * 10)
    rRange = func(l, k, x0, (cong + 0.5) * 10)
    duration = max(0, int((lRange + rRange) / 2 - func(l, k, x0, 1)))
    # print(duration)
    return min(30, duration)


def random_color():
    number_of_colors = 8

    color = ["red", "orange", "blue", "violet", "green"]
    # print(color)
    return random.choice(color)

class Clock:
    def __init__(self, simulation_time):
        self.simulation_time = simulation_time
        self.clock  = canvas.create_text(500, 450, text=self.simulation_time)

    def start_clock(self):
        if self.simulation_time < 0:
            f = 1
        else:
            self.simulation_time -= 1
            print(self.simulation_time)
            canvas.delete(self.clock)
            self.clock = canvas.create_text(500, 450, text=self.simulation_time)
            for i in range(1, 5):
                simulator[i-1].start()
            canvas.after(6000, self.start_clock())


class Simulator:
    def __init__(self, Id, lamda, simulation_time):
        self.Id = Id
        self.lamda = lamda
        self.probability = []
        self.simulation_time = simulation_time
        # print(self.Id)

    def calculate_probability(self, vehicle):
        return (math.pow(self.lamda, vehicle) * math.exp(-1 * self.lamda)) / math.factorial(vehicle)

    def initialize(self):
        prob = 0
        self.probability.append(prob)
        for vehicle in range(1, 21):
            prob += self.calculate_probability(vehicle)
            self.probability.append(prob)

    def start(self):

        r = random.uniform(0, 1)
        vehicles = bisect.bisect_left(self.probability, r, 0, len(self.probability)) + 1
        # vehicles = 2
        # print(self.Id, vehicles)
        simulate(self.Id, vehicles)



class TrafficLight:
    def __init__(self, x, y, cordx, cordy):
        self.Id = (x - 1) * parallelWays + y
        self.fsm = self.fsm4()
        self.cordX = cordx
        self.cordY = cordy
        self.arr = []
        self.arr.append(canvas.create_line(self.cordX, self.cordY + 5, self.cordX, self.cordY + width / 4 + 5,
                                           fill='red', arrow=tk.FIRST))
        self.arr.append(canvas.create_line(self.cordX, self.cordY + width / 4 + 5, self.cordX + width / 4,
                                           self.cordY + width / 4 + 5,
                                           fill='red', arrow=tk.LAST))
        self.arr.append(canvas.create_line(self.cordX - width / 4 - 5, self.cordY, self.cordX - 5, self.cordY,
                                           fill='red', arrow=tk.LAST))
        self.arr.append(canvas.create_line(self.cordX - width / 4 - 5, self.cordY, self.cordX - width / 4 - 5,
                                           self.cordY + width / 4,
                                           fill='red', arrow=tk.LAST))
        self.arr.append(canvas.create_line(self.cordX, self.cordY - 5, self.cordX, self.cordY - 5 - width / 4,
                                           fill='red', arrow=tk.FIRST))
        self.arr.append(canvas.create_line(self.cordX - width / 4, self.cordY - 5 - width / 4, self.cordX,
                                           self.cordY - 5 - width / 4,
                                           fill='red', arrow=tk.FIRST))
        self.arr.append(canvas.create_line(self.cordX + 5, self.cordY, self.cordX + width / 4 + 5, self.cordY,
                                           fill='red', arrow=tk.FIRST))
        self.arr.append(canvas.create_line(self.cordX + width / 4 + 5, self.cordY, self.cordX + width / 4 + 5,
                                           self.cordY - width / 4,
                                           fill='red', arrow=tk.LAST))
        self.timeleft = 0
        self.runtime = 50
        self.state = 0
        self.state_str = "S0"
        self.timer = canvas.create_text(self.cordX - 2*width, self.cordY - length/2, text=self.state_str + " " + str(self.timeleft))
        self.cong = {}
        for i in range(0, 9):
            self.cong[(self.Id, i)] = 0
        self.queue = [[] for i in range(1, 100)]
        self.timeleft = 1
        self.congestion = 0

        self.rst = 0

    def findcongestion(self, state, ways):
        congestion = 0
        for i in range(0, ways):
            if state & (1 << i):
                congestion = max(congestion, self.cong[(self.Id, i)])

        return congestion

    def fsm4(self):
        fsm = FSM([])
        fromState = "S"
        toState = "S"
        rst = 0

        self.stateValue = {}
        self.stateValue["S0"] = 0
        self.stateValue["S1"] = 17
        self.stateValue["S2"] = 34
        self.stateValue["S3"] = 68
        self.stateValue["S4"] = 136
        self.stateValue["S5"] = 3
        self.stateValue["S6"] = 12
        self.stateValue["S7"] = 48
        self.stateValue["S8"] = 192

        for i in range(0, 8):
            fsm.addTransition(fromState + str(i), toState + str((i + 1)), rst)

        fsm.addTransition("S8", "S1", rst)

        rst = 1
        for i in range(1, 9):
            fsm.addTransition(fromState + str(i), "S0", rst)
        dir = random.randint(0, 4)
        fsm.start("S" + str(dir))
        return fsm

    def changeState(self, state):
        for i in range(0, 8):
            if state & (1 << i):
                canvas.itemconfig(self.arr[i], fill='green')
            else:
                canvas.itemconfig(self.arr[i], fill='red')

    def startLight(self):

        if self.runtime > 0 and self.Id == 1:
            self.runtime -= 1
        elif self.Id == 1:
            self.runtime = 200 
            for i in range(1, 5):
                simulator[i-1].start()

        if self.timeleft <= 0:
            # self.arr1 = canvas.create_line(self.cordX, self.cordY - width / 4, self.cordX, self.cordY,
            #                                fill='red', arrow=tk.FIRST)
            # self.arr2 = canvas.create_line(self.cordX, self.cordY, self.cordX, self.cordY + width / 4,
            #                                fill='red', arrow=tk.END)
            # self.arr3 = canvas.create_line(self.cordX - width / 4, self.cordY, self.cordX, self.cordY,
            #                                fill='red', arrow=tk.FIRST)
            # self.arr4 = canvas.create_line(self.cordX, self.cordY, self.cordX + width / 4, self.cordY,
            #                                fill='red', arrow=tk.END)

            nextState = self.fsm.event(self.rst, self.cong, self.Id)
            maxCongestion = 0
            for i in range(1, 9):
                congestion = 0
                state = self.stateValue["S" + str(i)]
                for j in range(0, 8):
                    if state & (1 << j):
                        congestion += self.cong[(self.Id, j)]
                if congestion > maxCongestion:
                    maxCongestion = congestion
                    nextState = "S" + str(i)
            # print(maxCongestion, nextState)
            if maxCongestion == 0:
                self.changeState(0)
                self.timeleft = 2
                self.state = 0
                self.state_str = "S0"
            else:
                # print(self.Id, maxCongestion, nextState)
                self.state_str = nextState
                self.changeState(self.stateValue[nextState])
                congestion = self.findcongestion(self.stateValue[nextState], 8)
                self.timeleft = calculateTime(congestion)
                self.state = self.stateValue[nextState]
            canvas.after(50, self.startLight)
            self.timeleft -= 1
        else:
            canvas.delete(self.timer)
            self.timeleft -= 1
            self.timer = canvas.create_text(self.cordX - 2*width, self.cordY - length/2, text=self.state_str + " " + str(self.timeleft))
            canvas.after(50, self.startLight)



class Car(object):
    def __init__(self, Id, a, b, c, d, src, dest, nxtDest=(0, 0), dir=0, color=None):
        self.Id = Id
        if color == None:
            self.color = random_color()
        self.rect = canvas.create_rectangle(a, b, c, d, outline=self.color, fill=self.color)
        self.speed = (0, 0)
        self.src = src
        self.dest = dest
        self.dir = dir
        self.nxtDest = nxtDest
        self.runtime = 0
        self.number = -1
        self.nxtDir = 0
        self.nxtjunc = 0
        self.delete = 0
        self.inqueue = 0
        self.lane = 1

    def findSrc(self, newDir, dir, src):
        newSrc = src

        if dir == 1:
            dist = length
            if (self.nxtjunc + parallelWays, self.nxtjunc) in distance:
                dist = distance[(self.nxtjunc + parallelWays, self.nxtjunc)]
            if newDir == 2:
                newSrc = (src[0] + width, src[1] - width - dist, 1, 0, parent[(self.nxtjunc, self.dest[2])])
            elif newDir == 1:
                newSrc = (src[0], src[1] - dist - width, src[2], src[3], parent[(self.nxtjunc, self.dest[2])])
            elif newDir == 4:
                newSrc = (src[0], src[1] - dist, -1, 0, parent[(self.nxtjunc, self.dest[2])])

        elif dir == 2:
            dist = length
            if (self.nxtjunc - 1, self.nxtjunc) in distance:
                dist = distance[(self.nxtjunc - 1, self.nxtjunc)]
            if newDir == 2:
                newSrc = (src[0] + dist + width, src[1], src[2], src[3], parent[(self.nxtjunc, self.dest[2])])
            elif newDir == 1:
                newSrc = (src[0] + dist, src[1], 0, -1, parent[(self.nxtjunc, self.dest[2])])
            elif newDir == 3:
                newSrc = (src[0] + dist + width, src[1] + width, 0, 1, parent[(self.nxtjunc, self.dest[2])])

        elif dir == 3:
            dist = length
            if (self.nxtjunc - parallelWays, self.nxtjunc) in distance:
                dist = distance[(self.nxtjunc - parallelWays, self.nxtjunc)]
            if newDir == 2:
                newSrc = (src[0], src[1] + dist, 1, 0, parent[(self.nxtjunc, self.dest[2])])
            elif newDir == 3:
                newSrc = (src[0], src[1] + dist + width, src[2], src[3], parent[(self.nxtjunc, self.dest[2])])
            elif newDir == 4:
                newSrc = (src[0] - width, src[1] + width + dist, -1, 0, parent[(self.nxtjunc, self.dest[2])])

        else:
            dist = length
            if (self.nxtjunc + 1, self.nxtjunc) in distance:
                dist = distance[(self.nxtjunc + 1, self.nxtjunc)]
            if newDir == 4:
                newSrc = (src[0] - dist - width, src[1], src[2], src[3], parent[(self.nxtjunc, self.dest[2])])
            elif newDir == 1:
                newSrc = (src[0] - width - dist, src[1] - width, 0, -1, parent[(self.nxtjunc, self.dest[2])])
            elif newDir == 3:
                newSrc = (src[0] - dist, src[1], 0, 1, parent[(self.nxtjunc, self.dest[2])])

        return newSrc

    def check(self, state, go, come, Id):

        if come == go:
            # print(self.src, come, go, Id, canvas.itemcget(lightObject[Id].arr[come * 2 - 2], 'fill'))
            return canvas.itemcget(lightObject[Id].arr[come * 2 - 2], 'fill') == 'green'
        elif go == come + 1 or go == come - 3:
            # print(self.src, come, go, Id, canvas.itemcget(lightObject[Id].arr[come * 2 - 1], 'fill'))
            return canvas.itemcget(lightObject[Id].arr[come * 2 - 1], 'fill') == 'green'
        else:
            return True

    def goodToGo(self, nxtDir, dir, Id):

        if Id > parallelWays ** 2:
            return True
        # print(self.nxtDest, nxtDir, dir, Id)
        Id = int(Id)
        # print(Id)

        state = lightObject[Id].state
        # for i in range(0, 8):
        #   if state & (1<<(7-i)):
        #     print("1",end='')
        #   else:
        #     print("0",end='')
        # print()
        # print(state, nxtDir, dir)
        if self.check(state, nxtDir, dir, Id):
            # print(self.number)
            self.number -= 1
            self.number = max(0, self.number)
            return True
        return False

    def findNextDest(self, src, speed):
        if speed[1] == 0:
            if speed[0] > 0:
                dist = length
                if (self.nxtjunc - 1, self.nxtjunc) in distance:
                    dist = distance[(self.nxtjunc - 1, self.nxtjunc)]
                nxtDest = (src[0] + dist + width / 2, src[1])
            else:
                dist = length
                if (self.nxtjunc + 1, self.nxtjunc) in distance:
                    dist = distance[(self.nxtjunc + 1, self.nxtjunc)]
                nxtDest = (src[0] - (dist + width / 2), src[1])
        else:
            dist = length
            if speed[1] > 0:
                if (self.nxtjunc - parallelWays, self.nxtjunc) in distance:
                    dist = distance[(self.nxtjunc - parallelWays, self.nxtjunc)]
                nxtDest = (src[0], src[1] + (dist + width / 2))
            else:
                if (self.nxtjunc + parallelWays, self.nxtjunc) in distance:
                    dist = distance[(self.nxtjunc + parallelWays, self.nxtjunc)]
                nxtDest = (src[0], src[1] - (dist + width / 2))
        # print(nxtDest)
        return nxtDest

    def findRuntime2(self):
        runtime = 1
        x = (self.src[0] - self.nxtDest[0]) ** 2 + (self.src[1] - self.nxtDest[1]) ** 2
        x = math.sqrt(x)
        speed = max(abs(self.speed[0]), abs(self.speed[1]))
        runtime = x / speed
        return int(runtime)

    def findDirection(self):

        # print(x+y, graph[x+y])
        # i = 0
        # size = len(graph[x + y])
        # random.shuffle(graph[x+y])
        # while True:
        #     i = i % size
        #     ndir = graph[x+y][i]
        #     if self.dir != graph[x + y][i] and abs(self.dir - graph[x + y][i]) != 2:
        #         return graph[x + y][i]
        #     i += 1
        if self.nxtjunc == self.dest[2]:
            return self.dest[3]
        par = parent[(self.nxtjunc, self.dest[2])]
        if par == self.nxtjunc + 1:
            return 2
        elif par == self.nxtjunc - 1:
            return 4
        elif par == self.nxtjunc + parallelWays:
            return 3
        else:
            return 1

    def findRuntime(self, x, y):
        runtime = 1
        dist = (x - self.nxtDest[0]) ** 2 + (y - self.nxtDest[1]) ** 2
        dist = math.sqrt(dist)
        speed = max(abs(self.speed[0]), abs(self.speed[1]))
        runtime = dist / speed
        return int(runtime)

    def reached(self):
        x = self.src[0] + self.speed[0] * self.runtime
        y = self.src[1] + self.speed[1] * self.runtime
        dist = (x - self.nxtDest[0]) ** 2 + (y - self.nxtDest[1]) ** 2
        dist = math.sqrt(dist)
        # print(x, y, self.nxtDest, dist, width)
        return dist <= width / 2

    def findWay(self, come, go):
        if come == go:
            return 2 * come - 2
        elif go == come + 1 or go == come - 3:
            return 2 * come - 1
        else:
            return 8

    def check_queue(self):
        dir1 = direction[(self.src[2], self.src[3])]
        lane = self.lane
        if lane == 1:
            dir1 = (dir1 - 1) if dir1 != 1 else 4
            return lightObject[self.nxtjunc].cong[(self.nxtjunc, self.findWay(self.dir, dir1))]
        if lane == 2:
            return lightObject[self.nxtjunc].cong[(self.nxtjunc, self.findWay(self.dir, self.dir))]
        if lane == 3:
            dir1 = (dir1 + 1) if dir1 != 4 else 1
            return lightObject[self.nxtjunc].cong[(self.nxtjunc, self.findWay(self.dir, dir1))]
        return 0

    def increase_queue(self):
        dir1 = direction[(self.src[2], self.src[3])]
        lane = self.lane
        if lane == 1:
            dir1 = (dir1 - 1) if dir1 != 1 else 4
            lightObject[self.nxtjunc].cong[(self.nxtjunc, self.findWay(self.dir, dir1))] += 1
        if lane == 2:
            lightObject[self.nxtjunc].cong[(self.nxtjunc, self.findWay(self.dir, self.dir))] += 1
        if lane == 3:
            dir1 = (dir1 + 1) if dir1 != 4 else 1
            lightObject[self.nxtjunc].cong[(self.nxtjunc, self.findWay(self.dir, dir1))] += 1

    def reached_queue(self, queue_number):
        if self.dir == 1:
            return (self.src[1] + self.speed[1] * (self.runtime + 1)) <= (
                        self.nxtDest[1] + width / 2 + queue_number * 2)
        if self.dir == 3:
            return (self.src[1] + self.speed[1] * (self.runtime + 1)) >= (
                        self.nxtDest[1] - width / 2 - queue_number * 2)
        if self.dir == 2:
            return (self.src[0] + self.speed[0] * (self.runtime + 1)) >= (
                        self.nxtDest[0] - width / 2 - queue_number * 2)
        if self.dir == 4:
            return (self.src[0] + self.speed[0] * (self.runtime + 1)) <= (
                        self.nxtDest[0] + width / 2 + queue_number * 2)

    def find_position(self, queue_number):
        x = self.src[0]
        y = self.src[1]
        if self.dir == 1:
            y = self.nxtDest[1] + width / 2 + queue_number * 5
        if self.dir == 3:
            y = self.nxtDest[1] - width / 2 - queue_number * 5
        if self.dir == 2:
            x = self.nxtDest[0] - width / 2 - queue_number * 5
        if self.dir == 4:
            x = self.nxtDest[0] + width / 2 + queue_number * 5
        return x, y

    def move(self):
        # print(self.runtime)
        # x, y = canvas.coords(self.rect)[0], canvas.coords(self.rect)[1]

        # queue_number = self.check_queue()
        # if queue_number:
        #     self.number = queue_number
        #     actualSpeed = self.speed
        #     speed = max(abs(self.speed[0]), abs(self.speed[1]))
        #     self.set_speed(0)

        if self.delete == 1:

            if self.runtime <= 100:
                self.runtime += 1
                canvas.move(self.rect, self.speed[0], self.speed[1])
                canvas.after(10, self.move)
            else:
                canvas.delete(self.rect)
                Id = self.Id
                color = self.color
                del (self)
                # addVehicle(Id, srcPoints, destPoints, length, width, color)
        else:

            # print(self.inqueue, self.delete)
            if self.inqueue == 0 and self.delete == 0:
                queue_size = len(lightObject[self.nxtjunc].queue[self.lane + 3 * (self.dir-1)])
                if self.reached_queue(queue_size):
                    # print("reached")
                    # actualSpeed = self.speed
                    # speed = max(abs(self.speed[0]), abs(self.speed[1]))
                    # self.set_speed(0)
                    self.inqueue = 1
                    self.increase_queue()
                    if len(lightObject[self.nxtjunc].queue[self.lane + 3 * (self.dir-1)]) == 0:
                        lightObject[self.nxtjunc].queue[self.lane + 3 * (self.dir-1)].append(1)
                        self.Id = 1
                        # print(queue_size, self.Id, self.inqueue)
                    else:
                        queueId = lightObject[self.nxtjunc].queue[self.lane + 3 * (self.dir-1)][-1]
                        lightObject[self.nxtjunc].queue[self.lane + 3 * (self.dir-1)].append(queueId + 1)
                        self.Id = queueId + 1
                    x1, y1 = self.find_position(queue_size)
                    x, y = shifter(self.src)
                    lane = self.lane
                    x1 += (width / 6) * x * lane
                    y1 += (width / 6) * y * lane
                    # print(x1, y1, self.nxtDest)
                    color = self.color
                    canvas.delete(self.rect)
                    self.rect = canvas.create_rectangle(x1, y1, x1 - 2, y1 - 2, outline=color,
                                                        fill=color)
                    # print("x "+ str(self.Id))
                    canvas.after(10, self.move)
                else:
                    # print("not reached")
                    canvas.move(self.rect, self.speed[0], self.speed[1])
                    canvas.after(10, self.move)
                    self.runtime += 1
            elif self.inqueue and self.delete == 0:
                if lightObject[self.nxtjunc].queue[self.lane + 3 * (self.dir-1)][0] != self.Id:
                    queue_size = lightObject[self.nxtjunc].queue[self.lane + 3 * (self.dir-1)].index(self.Id)
                    x1, y1 = self.find_position(queue_size)
                    x, y = shifter(self.src)
                    lane = self.lane
                    x1 += (width / 6) * x * lane
                    y1 += (width / 6) * y * lane
                    color = self.color
                    canvas.delete(self.rect)
                    self.rect = canvas.create_rectangle(x1, y1, x1 - 2, y1 - 2, outline=color,
                                                        fill=color)
                    canvas.after(10, self.move)
                else:
                    if True:

                        # print(self.src)
                        # print("last process")
                        actualSpeed = self.speed
                        speed = max(abs(self.speed[0]), abs(self.speed[1]))
                        self.set_speed(0)

                        # if self.nxtDir == 0:
                        #   nxtDir = random.randint(1, 4)
                        #   while abs(nxtDir-self.dir) == 2 or :
                        #     nxtDir = random.randint(1, 4)
                        #   self.nxtDir = nxtDir

                        # nxtDir = 1
                        # print(self.dir, nxtDir)
                        # nxtDir = (self.dir + 1) % 4
                        # if nxtDir == 0:
                        #  nxtDir = 4

                        # print(self.dir, nxtDir)
                        cordX, cordY = self.src[0], self.src[1]
                        if actualSpeed[1] == 0:
                            if actualSpeed[0] > 0:
                                # cordX += length
                                x = int((cordX - length) / (length + width)) + 1
                                y = int(cordY / (length + width)) * parallelWays
                            else:
                                # cordX -= length
                                x = int((cordX - length) / (length + width))
                                y = int(cordY / (length + width) - 1) * parallelWays
                        else:
                            if actualSpeed[1] < 0:
                                # cordY += length
                                x = int((cordX - length) / (length + width)) + 1
                                y = int(cordY / (length + width) - 1) * parallelWays
                            else:
                                # cordY -= length
                                x = int((cordX - length) / (length + width))
                                y = int(cordY / (length + width)) * parallelWays
                        # print(self.src, x, y)
                        if self.number == -1:
                            self.nxtDir = self.findDirection()
                            if self.nxtjunc in lightObject:
                                self.number = 10
                                # print(self.number, self.nxtjunc)
                                # lightObject[self.nxtjunc].cong[(self.nxtjunc, self.findWay(self.dir, self.nxtDir))] += 1

                        # print(x+y)

                        # print(self.number)
                        if self.goodToGo(self.nxtDir, self.dir, self.nxtjunc) and self.number == 0:

                            # print(self.nxtjunc)
                            self.number = -1
                            lightObject[self.nxtjunc].cong[(self.nxtjunc, self.findWay(self.dir, self.nxtDir))] -= 1
                            x = lightObject[self.nxtjunc].queue[self.lane + 3 * (self.dir-1)].pop(0)
                            # print("x = " + str(x))
                            nsrc = self.findSrc(self.nxtDir, self.dir, self.src)
                            var = self.nxtjunc
                            self.nxtjunc = parent[(self.nxtjunc, self.dest[2])]
                            # print(nsrc)
                            # time.sleep(10)
                            # print(self.src, nsrc)
                            self.src = nsrc
                            # print(self.nxtjunc, self.src)
                            self.nxtDest = self.findNextDest(nsrc, (speed * nsrc[2], speed * nsrc[3]))

                            # time.sleep(1)
                            self.set_speed(speed)
                            leftRange = length
                            rightRange = parallelWays * (length + width) + 2 * length
                            # print(leftRange, rightRange, self.nxtDest, self.src, self.speed)
                            # if self.dir == nxtDir:
                            #
                            #   x, y = self.nxtDest[0], self.nxtDest[1]
                            #   x += width*nsrc[2]
                            #   y += width*nsrc[3]
                            #   self.nxtDest = (x, y)
                            #   #self.runtime = self.findRuntime(x, y)
                            # else:
                            # print(self.dir, nxtDir, self.src)
                            # time.sleep(10)
                            flag = 0
                            if var == self.dest[2]:
                                flag = 1
                            canvas.delete(self.rect)
                            if self.delete != 1:

                                # print("finally")
                                self.inqueue = 0
                                x, y = shifter(self.src)
                                lane = findLane(self.src, self.dest, direction[(self.src[2], self.src[3])])
                                nsrc = (
                                self.src[0] + (width / 6) * x * lane, self.src[1] + (width / 6) * y * lane, self.src[2],
                                self.src[3])
                                # nsrc = (self.src[0] + random.randint(1, width / 2 - 2) * x,
                                #         self.src[1] + random.randint(1, width / 2 - 2) * y, self.src[2], self.src[3])
                                color = self.color
                                if x == 0:
                                    x = 1
                                if y == 0:
                                    y = 1
                                self.rect = canvas.create_rectangle(nsrc[0], nsrc[1], nsrc[0] - 2*x, nsrc[1] - 2*y,
                                                                    outline=color,
                                                                    fill=color)
                                self.lane = lane
                                # self.runtime = self.findRuntime2()
                                self.runtime = 1
                                canvas.move(self.rect, self.speed[0], self.speed[1])
                                canvas.after(10, self.move)
                                self.dir = self.nxtDir
                                self.delete = flag
                            else:
                                # print("YES")
                                Id = self.Id
                                color = self.color
                                del (self)
                                addVehicle(Id, srcPoints, destPoints, length, width, color)
                        else:
                            canvas.move(self.rect, self.speed[0], self.speed[1])
                            self.speed = actualSpeed
                            canvas.after(10, self.move)

                    else:
                        canvas.move(self.rect, self.speed[0], self.speed[1])
                        canvas.after(10, self.move)
                        self.runtime += 1


    def set_speed(self, x):
        self.speed = x * self.src[2], x * self.src[3]

    def set_runtime(self, runtime):
        self.runtime = runtime


def shifter(src):
    x = 1
    y = 1
    if direction[(src[2], src[3])] == 1:
        x = 1
        y = 0
    elif direction[(src[2], src[3])] == 2:
        x = 0
        y = 1
    elif direction[(src[2], src[3])] == 3:
        x = -1
        y = 0
    else:
        x = 0
        y = -1
    return x, y


def findLane(src, dest, dir):
    junc = parent[(src[4], dest[2])]
    # print(src, dest, junc)
    if dest[2] == src[4]:
        if dir == 1:
            if dest[3] == 1:
                return 2
            if dest[3] == 2:
                return 3
            if dest[3] == 4:
                return 1
            return 1
        if dir == 2:
            if dest[3] == 1:
                return 1
            if dest[3] == 2:
                return 2
            if dest[3] == 3:
                return 3
            return 1
        if dir == 3:
            if dest[3] == 2:
                return 1
            if dest[3] == 3:
                return 2
            if dest[3] == 4:
                return 3
            return 1
        if dir == 4:
            if dest[3] == 1:
                return 3
            if dest[3] == 3:
                return 1
            if dest[3] == 4:
                return 2
            return 1
    if junc == src[4] + 1:
        if dir == 2:
            return 2
        if dir == 1:
            return 3
        if dir == 3:
            return 1
    if junc == src[4] - 1:
        if dir == 4:
            return 2
        if dir == 1:
            return 1
        if dir == 3:
            return 3
    if junc == src[4] + parallelWays:
        if dir == 2:
            return 3
        if dir == 3:
            return 2
        if dir == 4:
            return 1
    if junc == src[4] - parallelWays:
        if dir == 2:
            return 1
        if dir == 1:
            return 2
        if dir == 4:
            return 3
    return 1


def startVehicle(Id, src, dest, speed, length, width, color=None):
    x, y = shifter(src)
    lane = findLane(src, dest, direction[(src[2], src[3])])
    # print(lane)
    nsrc = (src[0] + (width / 6) * x * lane, src[1] + (width / 6) * y * lane, src[2], src[3])
    if x == 0:
        x = 1
    if y == 0:
        y = 1
    car = Car(Id, nsrc[0], nsrc[1], nsrc[0] - 2*x, nsrc[1] - 2*y, src, dest, canvas, color)
    car.src = src
    car.lane = lane
    car.dest = dest
    car.nxtjunc = src[4]
    car.nxtDest = car.findNextDest(src, (speed * nsrc[2], speed * nsrc[3]))
    # print(src, car.dest,car.nxtDest)
    dir = direction[(nsrc[2], nsrc[3])]
    car.dir = dir
    # print(src, speed)
    car.set_speed(speed / 10)
    # print(car.nxtDest)
    # car.runtime = car.findRuntime2()
    car.move()
    # vehicleObject.append(car)


def make_road(parallelWays, length, width):
    src = [[] for i in range(1, 6)]
    dest = [[] for i in range(1, 6)]
    start = length

    # canvas.create_line(start, start, start + length, start, start + length, start, start + length, start - length)

    x = start
    y = start
    for i in range(0, parallelWays):
        x += width
        if (i, i + 1) in distance:
            x += distance[(i, i + 1)]
        else:
            x += length
        src[3].append((x, y - length, 0, 1, (i + 1)))
        dest[3].append((x - width, y - length, (i + 1), 1))
        # canvas.create_line(x, y - length, x, y, x, y, x + length, y, x + length, y, x + length, y - length)

    # x += length + width
    # src.append((x, y - length, 0, 1, parallelWays))
    # dest.append((x - width, y - length, parallelWays, 1))
    # canvas.create_line(x, y - length, x, y, x, y, x + length, y)

    y = start
    tf = 1
    for i in range(0, parallelWays):
        src[2].append((start, y, 1, 0, i * parallelWays + 1))
        y += width
        dest[2].append((start, y, i * parallelWays + 1, 4))
        # canvas.create_line(start, y, start + length, y, start + length, y, start + length, y + length, start + length,
        #                   y + length, start, y + length)
        if (tf, tf + parallelWays) in distance:
            y += distance[(tf, tf + parallelWays)]
        else:
            y += length
        tf += parallelWays
    x = start
    y = start

    # for i in range(0, parallelWays - 1):
    #     x += length + width
    #     y = start
    #     for j in range(0, parallelWays - 1):
    #         y += width
    #         canvas.create_rectangle(x, y, x + length, y + length)
    #         y += length

    for i in range(0, parallelWays + 1):
        if (i, i + 1) in distance:
            x += distance[(i, i + 1)]
        else:
            x += length
        x += width
    x -= width
    y = start
    tf = 1
    for i in range(0, parallelWays):
        dest[4].append((x, y, parallelWays * (i + 1), 2))
        y += width
        src[4].append((x, y, -1, 0, parallelWays * (i + 1)))
        # canvas.create_line(x, y, x - length, y, x - length, y, x - length, y + length, x - length, y + length, x,
        #                    y + length)
        if (tf, tf + parallelWays) in distance:
            y += distance[(tf, tf + parallelWays)]
        else:
            y += length
        tf += parallelWays
    x = start

    # canvas.create_line(x, y, x + length, y, x + length, y, x + length, y + length)

    for i in range(0, parallelWays):
        if (i, i + 1) in distance:
            x += distance[(i, i + 1)]
        else:
            x += length
        src[1].append((x, y, 0, -1, i + 1 + parallelWays * (parallelWays - 1)))
        x += width
        dest[1].append((x, y, i + 1 + parallelWays * (parallelWays - 1), 3))
        # canvas.create_line(x, y + length, x, y, x, y, x + length, y, x + length, y, x + length, y + length)

    # canvas.create_line(x, y + length, x, y, x, y, x + length, y)

    x = length
    y = length
    for i in range(1, parallelWays + 2):
        tf = 1
        x1 = x
        y1 = y
        if (i - 1, i) in distance:
            last = distance[(i - 1, i)]
        else:
            last = length
        for j in range(1, parallelWays + 1):
            canvas.create_line(x1, y1, x1 + last, y1)
            y2 = y1 + width / 6
            for k in range(1, 6):
                if k == 3:
                    canvas.create_line(x1, y2, x1 + last, y2, fill='red')
                else:
                    canvas.create_line(x1, y2, x1 + last, y2, fill='yellow', dash=(2, 4))
                y2 += width / 6
            y1 += width
            canvas.create_line(x1, y1, x1 + last, y1)
            if (tf, tf + parallelWays) in distance:
                y1 += distance[(tf, tf + parallelWays)]
            else:
                y1 += length
            tf += parallelWays
        x += width
        x += last

    x = 2 * length
    y = length
    for i in range(1, parallelWays + 1):
        tf = 1
        x1 = x
        y1 = y
        last = length
        for j in range(1, parallelWays + 2):
            canvas.create_line(x1, y1 - last, x1, y1)
            x2 = x1 + width / 6
            for k in range(1, 6):
                if k == 3:
                    canvas.create_line(x2, y1 - last, x2, y1, fill='red')
                else:
                    canvas.create_line(x2, y1 - last, x2, y1, fill='yellow', dash=(2, 4))
                x2 += width / 6
            x1 += width
            canvas.create_line(x1, y1 - last, x1, y1)
            x1 -= width
            if (tf, tf + parallelWays) in distance:
                y1 += distance[(tf, tf + parallelWays)]
                last = distance[(tf, tf + parallelWays)]
            else:
                y1 += length
                last = length
            y1 += width
            tf += parallelWays
        x += width
        if (i, i + 1) in distance:
            x += distance[(i, i + 1)]
        else:
            x += length
    return src, dest


def startTrafficLight():
    # print(db_path)
    # conn = sql.connect(db_path, check_same_thread=False, isolation_level='deferred', timeout=11)
    # conn.execute("Drop table if exists TrafficLight")
    # conn.execute('''CREATE TABLE TrafficLight(
    #                           ID int NOT NULL,
    #                           lightChangeTIme int,
    #                           timeLeft int,
    #                           congestion1 int,
    #                           congestion2 int,
    #                           congestion3 int,
    #                           congestion4 int,
    #                           congestion5 int,
    #                           congestion6 int,
    #                           congestion7 int,
    #                           congestion8 int,
    #                           state int,
    #                           reset int,
    #                           PRIMARY KEY (ID))''')
    # conn.close()
    # defaultChangeTime = 20
    #
    # for Id in range(0, count):
    #     conn = sql.connect(db_path, check_same_thread=False, isolation_level='deferred', timeout=11)
    #     conn.execute('''INSERT INTO TrafficLight (ID,
    #                           lightChangeTIme,
    #                           timeLeft,
    #                           congestion1,
    #                           congestion2,
    #                           congestion3,
    #                           congestion4,
    #                           congestion5,
    #                           congestion6,
    #                           congestion7,
    #                           congestion8,
    #                           state,
    #                           reset) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
    #                  (Id + 1, defaultChangeTime, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    #     conn.commit()
    # conn.close()
    cordx = length
    for x in range(0, parallelWays):
        if (x, x + 1) in distance:
            cordx += distance[(x, x + 1)]
        else:
            cordx += length
        cordy = length
        tf = 1
        for y in range(0, parallelWays):
            lightObject[y * parallelWays + x + 1] = TrafficLight(y + 1, x + 1, cordx + width / 2, cordy + width / 2)
            lightObject[y * parallelWays + x + 1].startLight()
            if (tf, tf + parallelWays) in distance:
                cordy += distance[(tf, tf + parallelWays)]
            else:
                cordy += length
            tf += parallelWays
            cordy += width
        cordx += width
    # while True:
    #     ()


def addVehicle(choice, Id, color=None):
    # choice = 3
    src = srcPoints[choice][random.randint(0, len(srcPoints[choice]) - 1)]
    # src = srcPoints[choice][0]

    # choice = random.randint(1, 4)
    a = []
    if choice == 1:
        a = [3, 4]
    if choice == 2:
        a = [4, 1]
    if choice == 3:
        a = [1, 2]
    if choice == 4:
        a = [3, 2]
    dchoice = numpy.random.choice(numpy.arange(0, 2), p=[0.5, 0.5])
    # print(choice, a[dchoice])
    choice = a[dchoice]
    # choice = 2
    dest = destPoints[choice][random.randint(0, len(destPoints[choice]) - 1)]
    # dest = destPoints[choice][1]
    speed = random.randint(3, 6)
    # print(dest)
    # print(choice)
    startVehicle(Id, src, dest, speed, length, width, color)


def simulate(Id, vehicle=1):
    # print("Enter the number of vehicles")
    # vehicle = input()
    # vehicle = int(vehicle)
    for i in range(0, vehicle):
        addVehicle(Id, i)
        # time.sleep(0.1)
    # while True:
    #     canvas.update()
    """while True:
    time.sleep(0.025)
    for object in vehicleObject:
      object.move()
      ()"""


class graph(object):
    def __init__(self, canvas):
        self.canvas = canvas


def createGraph():
    graph = [[] for i in range(0, parallelWays ** 2 + 5)]
    for i in range(1, parallelWays + 1):
        for j in range(1, parallelWays + 1):
            if i == 1 or j == 1 or i == parallelWays or j == parallelWays:
                continue
            else:
                for k in range(1, 4):
                    graph[(i - 1) * parallelWays + j].append(k)

    for i in range(1, parallelWays + 1):

        if i > 1 and i < parallelWays:
            graph[i].append(2)
            graph[i].append(3)
            graph[i].append(4)
            graph[parallelWays * (parallelWays - 1) + i].append(1)
            graph[parallelWays * (parallelWays - 1) + i].append(2)
            graph[parallelWays * (parallelWays - 1) + i].append(4)
            graph[(i - 1) * parallelWays + 1].append(1)
            graph[(i - 1) * parallelWays + 1].append(2)
            graph[(i - 1) * parallelWays + 1].append(3)
            graph[(i - 1) * parallelWays + parallelWays].append(1)
            graph[(i - 1) * parallelWays + parallelWays].append(4)
            graph[(i - 1) * parallelWays + parallelWays].append(3)
        elif i == 1:
            graph[i].append(2)
            graph[i].append(3)
            graph[parallelWays * (parallelWays - 1) + i].append(1)
            graph[parallelWays * (parallelWays - 1) + i].append(2)
        else:
            graph[i].append(4)
            graph[i].append(3)
            graph[parallelWays * (parallelWays - 1) + i].append(1)
            graph[parallelWays * (parallelWays - 1) + i].append(4)
    return graph


def initializeDistance():
    # for i in range(1, parallelWays**2+1):
    #     for j in range(1, parallelWays**2+1):
    #         distance[(i, j)] = 0

    # for i in range(1, parallelWays**2+1):
    #     if i%parallelWays != 0:
    #         distance[(i, i+1)] = length
    #         distance[(i+1, i)] = length
    #     if i <= (parallelWays-1)*parallelWays:
    #         distance[(i, i+parallelWays)] = length
    #         distance[(i+parallelWays, i)] = length
    tf = 1
    # for i in range(1, parallelWays):
    #     distance[(i, i+1)] = random.randint(length-50, length+50)
    #     distance[(i + 1, i)] = distance[(i, i + 1)]
    #     distance[(tf, tf+parallelWays)] = random.randint(length-50, length+50)
    #     distance[(tf + parallelWays, tf)] = distance[(tf, tf+parallelWays)]
    #     tf += parallelWays
    for i in range(1, parallelWays):
        distance[(i, i + 1)] = random.randint(length - 50, length + 50)
        distance[(i + 1, i)] = distance[(i, i + 1)]
        distance[(tf, tf + parallelWays)] = random.randint(length - 50, length + 50)
        distance[(tf + parallelWays, tf)] = distance[(tf, tf + parallelWays)]
        tf += parallelWays
    for i in range(1, parallelWays):
        tf = i
        for j in range(1, parallelWays):
            tf += parallelWays
            # print(i,j,tf)
            distance[(tf, tf + 1)] = distance[(i, i + 1)]
            distance[(tf + 1, tf)] = distance[(i, i + 1)]
    tf = 1
    for i in range(1, parallelWays):
        for j in range(1, parallelWays):
            distance[(tf + j, tf + j + parallelWays)] = distance[(tf, tf + parallelWays)]
            distance[(tf + j + parallelWays, tf + j)] = distance[(tf, tf + parallelWays)]
        tf += parallelWays


def findAllPaths():
    dist = {}
    for i in range(1, parallelWays ** 2 + 1):
        for j in range(1, parallelWays ** 2 + 1):
            if i == j:
                dist[(i, j)] = 0
            else:
                dist[(i, j)] = 9999
            parent[(i, j)] = j
    for i in range(1, parallelWays ** 2 + 1):
        if i % parallelWays != 0:
            dist[(i, i + 1)] = distance[(i, i + 1)]
            dist[(i + 1, i)] = distance[(i + 1, i)]
        if i <= (parallelWays - 1) * parallelWays:
            dist[(i, i + parallelWays)] = distance[(i, i + parallelWays)]
            dist[(i + parallelWays, i)] = distance[(i + parallelWays, i)]
    n = parallelWays ** 2 + 1
    for k in range(1, n):
        for v in range(1, n):
            for u in range(1, n):
                if dist[(u, k)] + dist[(k, v)] < dist[(u, v)]:
                    dist[(u, v)] = dist[(u, k)] + dist[(k, v)]
                    parent[(u, v)] = parent[(u, k)]


def start_simulator():

    simulator = []
    simulation_time = 50
    for i in range(1, 5):
        simulator.append(Simulator(i, random.randint(8, 16), simulation_time))
        simulator[i-1].initialize()
        # simulator[i-1].start()
        # print("YES")
    return simulator

if __name__ == '__main__':
    root = tk.Tk()

    root.title("Traffic Simulation")
    canvas = tk.Canvas(root, width=2000, height=900, bg="white")
    # canvas.create_text(1000,450, text="Simulation Ckock")
    # canvas.create_text(800, 800, fill="darkblue", font="Times 20 italic bold",text="Click the bubbles that are multiples of two.")
    canvas.pack()

    last = 0
    parallelWays = 3
    length = 200
    width = 40
    timeDelay = 1
    initializeDistance()
    findAllPaths()
    srcPoints, destPoints = make_road(parallelWays, length, width)

    # for i in range(1, parallelWays**2 + 1):
    #   print(i)
    #   for j in graph[i]:
    #     print(j, end=" ")
    #   print()
    #
    print(srcPoints)
    # random.shuffle(srcPoints)
    # random.shuffle(destPoints)
    for i in range(1, parallelWays ** 2 + 1):
        for j in range(1, parallelWays ** 2 + 1):
            if (i, j) in distance:
                print(distance[(i, j)], end="   ")
            else:
                print(0, end="   ")
        print()
    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # db_path = os.path.join(BASE_DIR, "TrafficSimulator1.db")
    simulator = start_simulator()
    startTrafficLight()
    random_color()
    # Clock(1000).start_clock()
    root.mainloop()


