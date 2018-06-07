# -*- coding: utf-8 -*-

"""
Will simulate from 5:00-6:30
Class begins at 5:50 (** students in total, ** to floor 5, ** to floor 8, ** to floor 11)
Class ends at 5:30 (** students in total, ** from floor 5, ** from floor 8, ** from floor 11)
"""

import matplotlib.pyplot as plt
import time as timeHelper
import random
import numpy as np
import math

import pandas as pd

#import matplotlib.pyplot as plt

def numberToTime(arrivalPoint):

    hour=round(arrivalPoint//3600)
    minute=round(arrivalPoint//60-hour*60)
    second=round(arrivalPoint-hour*3600-minute*60)

    return '%02d' % hour+":"+'%02d' % minute+":"+'%02d' % second
    

class Person():

    arrivalTime=0
    serviceStartsAt=0
    serviceEndsAt=0
    arrivalFloor=0
    targetFloor=0    

    def __init__(self, arrivalTime, targetFloor, arrivalFloor):

        self.arrivalTime=arrivalTime
        self.targetFloor=targetFloor
        self.arrivalFloor=arrivalFloor

    def __repr__(self):

        return ''.join([str(x) for x in [numberToTime(self.arrivalTime),'\tFloor',self.arrivalFloor,'\tFloor ',
              self.targetFloor,'\t',numberToTime(self.serviceStartsAt),'\t',numberToTime(self.serviceEndsAt),
              '\t',self.serviceEndsAt-self.serviceStartsAt]])


class Student(Person):

    pass

        

class VirtualStudent(Person):

    def __init__(self, arrivalFloor, student):

        self.arrivalTime = student.arrivalTime
        self.serviceStartsAt = student.serviceStartsAt
        self.serviceEndsAt = student.serviceEndsAt
        self.arrivalFloor = arrivalFloor
        self.targetFloor = student.arrivalFloor


class Elevator():

    capacity=32
    currentLoad=0
    currentFloor=0
    express='Y'
    canGoTo=None  #determine express or local
    busy=0  #1 is busy, 0 is idle
    goingUp=2  #1 is going up, 0 is going down
    ready=0
    workingTime=0

    def __init__(self,express):

        self.targetFloor = []
        self.studentInEle = []

        if express=="Y":
            self.canGoTo=[2,8,11]
        else:
            self.canGoTo=[2,5,8,11]

        self.currentFloor=random.choice(self.canGoTo)        

    def __repr__(self):

        return '\t'.join([str(x) for x in [
                self.canGoTo,self.currentFloor, self.targetFloor, self.currentLoad]])

#reset the attributes for a idle elevator        

    def freeElevator(self):

        self.workingTime=0
        self.busy=0
        self.goingUp=None
        self.targetFloor=[]

#update the working time when the elevator is busy

    def updateWorkingTime(self): 

        #for elevator going up
        if self.goingUp==1:  
            if self.currentFloor<min(self.targetFloor):  
                if self.workingTime<min(self.targetFloor)-self.currentFloor:
                    self.workingTime+=1
                else:
                    self.workingTime=0
                    self.currentFloor=min(self.targetFloor)
                    self.targetFloor.remove(min(self.targetFloor))
                    self.busy=0   #free for now to be available to load students, will be busy again after
                                  #loading all students

        #for elevator going down
        if self.goingUp==0:
            if self.currentFloor>max(self.targetFloor):
                if self.workingTime<self.currentFloor-max(self.targetFloor):
                    self.workingTime+=1
                else:
                    self.workingTime=0
                    self.currentFloor=max(self.targetFloor)
                    self.targetFloor.remove(max(self.targetFloor))
                    self.busy=0   #free for now to be available to load students, will be busy again after
                                  #loading all students

        #if it has arrived the last target floor, free the elevator            
        if self.targetFloor==[]:
                self.freeElevator()

#generate the floor number based on the probabilities
def floorGenerator(Cutfor5,Cutfor8):

    temp=random.uniform(0,1)
    if temp<=Cutfor5:
        return 5
    elif temp<=Cutfor5+Cutfor8:
        return 8
    else:
        return 11
    

def loadCheck(elevator,student):

    if student.targetFloor not in elevator.canGoTo:
        return False
    if elevator.currentFloor!=student.arrivalFloor:   #elevator and student are not on the same floor
        return False
    if elevator.currentLoad==elevator.capacity:       #elevator has no available space for a student
        return False
    if student.targetFloor-student.arrivalFloor>0 and elevator.goingUp==0:
        return False                                   #student going up, elevator going down
    if student.targetFloor-student.arrivalFloor<0 and elevator.goingUp==1:
        return False                                   #student going down, elevator going up

    return True

def unloadStudent(elevator, time, completedOrder):

    count=0

    for student in elevator.studentInEle:
        if count<3 and student.targetFloor==elevator.currentFloor:

            student.serviceEndsAt=time
            completedOrder.append(student)
            elevator.studentInEle.remove(student)
            elevator.currentLoad -= 1
            count+=1       

    return count  #indicate whether all students have been unloaded



def loadStudents(studentQueue,time,freeElevatorIndex,elevators):

    loadedStu=[]
    eleToBeRemoved=[]

    for student in studentQueue:
        if student.arrivalTime>time:
            break

        for elevatorIndex in freeElevatorIndex:
            if freeElevatorIndex.index(elevatorIndex) not in eleToBeRemoved: 
                if loadCheck(elevators[elevatorIndex[0]],student)==True:

                    #update service starting time
                    loadAStudent(elevators[elevatorIndex[0]],student,time)
                    loadedStu.append(student)
                    elevatorIndex[1]+=1                    

                    if elevatorIndex[1]==3:  #check if 3 students have already been loaded to this elevator
                        eleToBeRemoved.append(freeElevatorIndex.index(elevatorIndex))

                    break        

    #remove students loaded to elevator

    for student in loadedStu:
        studentQueue.remove(student)

#load students to a elevator               
def loadAStudent(elevator,student,time):

    #update service starting time
    student.serviceStartsAt=time

    #if elevator is empty, determine the direction    
    if elevator.currentLoad==0:
        if student.targetFloor>elevator.currentFloor:
            elevator.goingUp=1
        else:
            elevator.goingUp=0

    #add a new target floor
    if student.targetFloor not in elevator.targetFloor:
        elevator.targetFloor.append(student.targetFloor)

    #add to current load and student    
    elevator.currentLoad+=1
    elevator.studentInEle.append(student)

#initialize the student queue
def initStudentQueue():

    studentQueue=[]

    for i in range(300):
        student=Student(math.ceil(random.normalvariate(17700, 240)),2,floorGenerator(0.583,0.333))
        if student.arrivalTime>18000 and student.arrivalTime<23400:
            studentQueue.append(student)

    for i in range(2150):
        student=Student(math.ceil(random.normalvariate(19200, 240)),2,floorGenerator(0.36,0.267))
        if student.arrivalTime>18000 and student.arrivalTime<23400:
            studentQueue.append(student)

    for i in range(650):
        student=Student(math.ceil(random.normalvariate(20100, 240)),floorGenerator(0.346,0.231),2)
        if student.arrivalTime>18000 and student.arrivalTime<23400:
            studentQueue.append(student) 

    for i in range(2450):
        student=Student(math.ceil(random.normalvariate(20700, 240)),floorGenerator(0.398,0.224),2)
        if student.arrivalTime>18000 and student.arrivalTime<23400:
            studentQueue.append(student) 

    for i in range(975):
        student=Student(math.ceil(random.normalvariate(21600, 240)),floorGenerator(0.359,0.282),2)
        if student.arrivalTime>18000 and student.arrivalTime<23400:
            studentQueue.append(student) 

    return sorted(studentQueue, key=lambda Student: Student.arrivalTime) #sort the list by arrivalTime

 
#print the student queue with all attributes

def printStudentQueue(studentQueue):

    print('Arrival Time\tArrival \tTarget\t Starting\tEnding\tWaiting Time')
    for student in studentQueue:
        print(student)    


def elevatorSystemGenerator(**kargs):

    ######system input#####        
    numExpress=kargs['numExpress']  #number of express elevators
    numLocal=kargs['numLocal']    #number of local elevators    

    systemStarts=kargs['systemStarts'] #the system starts at 5:00pm
    systemEnds= kargs['systemEnds']#the system ends at 6:30pm    
    step = kargs.get('step', None)


    #######################

    #Step 1:initialize the student queue
    studentQueue=initStudentQueue()
    #printStudentQueue(studentQueue)

    
    #Step 2: initialize elevators with random status
    elevators=[Elevator('Y') for i in range(numExpress)]
    for i in range(numLocal):
        elevators.append(Elevator('N'))
        

    #initialize a student list for completed order
    completedOrder=[]    
    timeRange = range(systemStarts,systemEnds+1)
    if not step: step = len(timeRange)
    stepCounter = step
    #Step 3: initialize and start the system clock  
    for time in timeRange:
        
        if not stepCounter: stepCounter=step
        stepCounter -= 1
        
        freeElevatorIndex=[]

    #check free elevators & unload students    
        for elevator in elevators:
            #obtain index for free elevators to further load students later on

            if not elevator.busy:
                if unloadStudent(elevator,time,completedOrder)==0:
                    freeElevatorIndex.append([elevators.index(elevator),0])  #elevator index and # of students loaded so far
            else:    
                elevator.updateWorkingTime()  #update working time and free elevators

                
         #load students to free elevators
        if freeElevatorIndex!=[]:#check if any elevator available
            loadStudents(studentQueue,time,freeElevatorIndex,elevators)

        
        targetedStudentIdx = []
        for i,loadNum in freeElevatorIndex:
            if loadNum < 3 and elevators[i].studentInEle:
                elevators[i].busy = 1
            if not elevators[i].studentInEle:
                for j in range(len(studentQueue)):
                    if j not in targetedStudentIdx:
                        if studentQueue[j].arrivalTime > time:
                            break
                        else:
                            if studentQueue[j].arrivalFloor in elevators[i].canGoTo and\
                               studentQueue[j].arrivalFloor != elevators[i].currentFloor:

                               loadAStudent(elevators[i],VirtualStudent(elevators[i].currentFloor,
                                            studentQueue[j]),
                                            time)
                               targetedStudentIdx.append(j)
                               break                        
        if not stepCounter or time == systemEnds: 
            yield [x for x in completedOrder if isinstance(x, Student)], studentQueue, elevators, time

        #printStudentQueue(studentQueue)

def getFinalStats(completedOrder):
    result=[0,0,0,0,0,0,0,0,0,0,0,0]
    count=[0,0,0,0,0,0]

    for order in completedOrder:
        if order.arrivalFloor==2:
            if order.targetFloor==5:
                result[0]+=order.serviceStartsAt-order.arrivalTime
                result[1]+=order.serviceEndsAt-order.serviceStartsAt
                count[0]+=1
            elif order.targetFloor==8:
                result[2]+=order.serviceStartsAt-order.arrivalTime
                result[3]+=order.serviceEndsAt-order.serviceStartsAt
                count[1]+=1
            else:
                result[4]+=order.serviceStartsAt-order.arrivalTime
                result[5]+=order.serviceEndsAt-order.serviceStartsAt
                count[2]+=1
        elif order.arrivalFloor==5:

            result[6]+=order.serviceStartsAt-order.arrivalTime
            result[7]+=order.serviceEndsAt-order.serviceStartsAt
            count[3]+=1

        elif order.arrivalFloor==8:

            result[8]+=order.serviceStartsAt-order.arrivalTime
            result[9]+=order.serviceEndsAt-order.serviceStartsAt
            count[4]+=1

        else:

            result[10]+=order.serviceStartsAt-order.arrivalTime
            result[11]+=order.serviceEndsAt-order.serviceStartsAt
            count[5]+=1

    return [result[i]/count[i//2] for i in range(len(result))]


def visualizeSystemSnapShop(time, studentQueue, elevators):
    
    objects = ['2','5','8','11']
    y_pos = np.arange(len(objects))
    performance = [
            len([stu for stu in studentQueue if stu.arrivalFloor == 2]),
            len([stu for stu in studentQueue if stu.arrivalFloor == 5]),
            len([stu for stu in studentQueue if stu.arrivalFloor == 8]),
            len([stu for stu in studentQueue if stu.arrivalFloor == 11]),
            
            ]
 
    
    plt.figure(1)
    plt.subplot(1,4,4)
    plt.barh(y_pos, performance, align='center', alpha=0.5)
    plt.yticks(y_pos, objects)
    plt.xlabel('number of student waiting')
    plt.title('Floor status at {}'.format(numberToTime(time)))
    plt.xlim(0, 35)
    
    
    
    expColor = 'C1'
    locColor = 'C2'
    
    
    indexMapping = {1:2,2:3,3:6,4:7,5:10,6:11}
    for i in range(1,7):
        
        ax=plt.subplot(3,4, indexMapping[i] )
        
        objects = ['']
        y_pos = np.arange(len(objects))
        performance = [elevators[i-1].currentLoad]
        plt.bar(y_pos, performance, align='center', alpha=0.5, 
                color=expColor if i <= 2 else locColor)
        plt.yticks(y_pos, objects)
        plt.xlabel('{} Load'.format('Elevator '+str(i)))
        plt.title('')
        plt.ylim(0, 32)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
    
    plt.subplot(1,4,1)
    plt.scatter( [i+1 for i in range(6)], 
                 [ele.currentFloor for ele in elevators], 
                 s=750, c=[expColor]*2+[locColor]*4, alpha=0.5, marker=r's',
            )

    plt.xlim(0, 7)    
    plt.ylim(1,12)
    
    plt.plot()
    
    plt.tight_layout()
    plt.pause(1e-17)
    plt.subplot(144).cla()
    plt.subplot(1,4,1).cla()
    for i in range(1,7):
        
        plt.subplot(3,4, indexMapping[i] ).cla()
    
    
def getStatByStepRecord(**kargs):
    
    studentQueue = kargs['studentQueue']
    elevators = kargs['elevators']
    time = kargs['time']
    
    return [numberToTime(time)]+[            
            len([x for x in studentQueue if int(x.arrivalFloor) == floor]) for floor in [2,5,8,11]            
            ]
    
    
def run(config, step=None, visualize=False, getStatByStep=False):
    
    if step: config['step'] = step
    elevatorSyetem = elevatorSystemGenerator(**config)
     
    res = None
    
    statSchema = ['time'] + ['number of student waiting at floor {}'.format(i) for i in [2,5,8,11]]
    statList = []
    
    finished = False
    while not finished:
        
        res = next(elevatorSyetem)
        _, studentQueue, elevators, time = res
        finished = time >= config['systemEnds']
        studentQueueAtTime = [student for student in studentQueue if student.arrivalTime <=time]
            
        if visualize:
            timeHelper.sleep(0.1)
            visualizeSystemSnapShop(time, studentQueueAtTime, elevators)
            
        if getStatByStep: statList.append(getStatByStepRecord(studentQueue=studentQueueAtTime,
                                            elevators=elevators,
                                            time=time
                                            )) 
    
    if getStatByStep:
        
        pd.DataFrame(statList, columns=statSchema).to_csv('stat_by_step.csv')
    
    return res
    
def visualizeOneRun(config, step=1000):
    
    run(config, step=step, visualize=True)
    

def main(config):
    

    replications = config['replications'] #number of replications for the model 

    resList = []

    for i in range(replications):

        completedOrder, _, _, _ = run(config)
        resList.append(getFinalStats(completedOrder))

    print(pd.DataFrame(resList, 
                       columns=['Average waiting time 2 to 5',
                                'Average service time 2 to 5',
                                'Average waiting time 2 to 8',
                                'Average service time 2 to 8',
                                'Average waiting time 2 to 11',
                                'Average service time 2 to 11',
                                'Average waiting time 5 to 2',
                                'Average service time 5 to 2',
                                'Average waiting time 8 to 2',
                                'Average service time 8 to 2',
                                'Average waiting time 11 to 2',
                                'Average service time 11 to 2']).mean())



if __name__ == "__main__":
    config = {
    'numExpress': 3,  #number of express elevators
    'numLocal': 3,    #number of local elevators    
    'systemStarts': int(5*60*60),  #the system starts at 5:00pm
    'systemEnds': int(6.5*60*60), 
    'replications': 10
    }
    
    
    #run(config, step=1, getStatByStep=True)
    visualizeOneRun(config, step=30)
    #main(config)

    

    

    

    

    

    

    

    

    

    

    

    

    

    

    

    

    

    

    

