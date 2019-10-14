class QueueUnderFlow(ValueError):
    pass

class SQueue:
    def __init__(self,init_len = 8):
        self.len = init_len #记录着元素储存区的有效容量
        self.elems = [0] * 8 # elem引用着队列的元素储存区
        self.head = 0 #队列首元素的下标
        self.elnum = 0
        #队列中元素的个数，如果等于len则入队列操作会自动扩张储存区
        
    def is_empty(self):
        return self.elnum == 0
    
    def fist(self):
        #得到队列的首元素，但是不移除这个元素
        if self.elnum == 0:
            raise QueueUnderFlow
        return self.elems[self.head]
    
    def dequeue(self):
        #出队列操作，在队尾出队列
        if self.elnum == 0:
            raise QueueUnderFlow
        e = self.elems[self.head]
        self.head = (self.head + 1) % self.len
        self.elnum -= 1
        return e
    
    def enqueue(self,elem):
        if self.elnum == self.len:
            self.__extend()
            #如果队列满了，就进行一次扩张，这里将扩张的过程局部化写成一个函数，便于理解
        self.elems[(self.head + self.elnum)%self.len] = elem
        self.elnum += 1
        #注意记录元素的下标的时候为了防止下标溢出要记住mod 长度一下，
        #然后要维护元素个数的变量保持正确的关系
    
    def __extend(self):
        old_len = self.len
        self.len = self.len * 2
        new_elems = [0]*(self.len)
        for i in range(old_len):
            new_elems[i] = self.elems[(self.head + i) % old_len]
        self.elems, self.head = new_elems, 0
        # 新的储存区域的长度是原来的两倍，把首元素放在新储存区域的0位置
        
    def size(self):
        return self.elnum
        
import random
class Passenger:
    def __init__(self,time,totalFloor):
        self.timeStamp = time
        self.init_floor = random.randrange(1,totalFloor+1)
        if self.init_floor == 1:
            self.direction = 'up'
        elif self.init_floor == totalFloor:
            self.direction = 'down'
        else:
            self.direction = random.choice(['up','down'])
            #random 里面的choice函数是从一个集合里面随机选择一个函数
        if self.direction == 'up':
            self.target_floor = random.randrange(self.init_floor+1,
                                                totalFloor+1)
        else:
            self.target_floor = random.randrange(1,self.init_floor)
        #目标楼层，初始楼层，方向之间是有关联的，
        #而且目标楼层肯定不等于初始楼层，这是考虑实际情况的做法
        self.time_get_on = 0
        # self.weight = random.normalvariate(65,10) 用最大载客人数判断电梯是否满
    
    def getStamp(self):
        return self.timeStamp
    
    def get_init_floor(self):
        return self.init_floor
    
    def get_direction(self):
        return self.direction
    
    def get_target_floor(self):
        return self.target_floor
    
    def WaitTime(self,currenttime):
        return currenttime - self.timeStamp
    
    def get_time_get_on(self):
        return self.time_get_on
    
    def get_time_on_elevator(self,currenttime):
        return currenttime - self.time_get_on
    
class Elevator:
    def __init__(self,totalFloor,timePerFloor,maxLoadingNum, maxvelocity = 0):
        self.upWaitingQueue = [SQueue() for i in range(totalFloor)]# 等待向上的人
        self.downWaitingQueue = [SQueue() for i in range(totalFloor)]# 等待向下的人
        self.getOffQueue = [SQueue() for i in range(totalFloor)]# 电梯内在每一层下电梯的人
        self.waitingPerson = 0# 等待的总人数
        self.loadingPerson = 0# 电梯上的人数
        self.timeInTotal = 0#这个变量用来统计所有人在电梯上呆的总时间和，就是每个人待的时间相加，从而用来生成乘客平均在电梯里的时间
        self.currentFloor = 1# 电梯目前所在楼层
        self.currentDirection = 'up'# 电梯目前的运行方向
        self.remainingTime = timePerFloor# 开始时电梯距离到达下一层的时间
        self.timePerFloor = timePerFloor# 电梯上升/下降一层所需时间
        self.totalFloor = totalFloor# 总楼层数
        self.waitingTimes = []# 每个乘客的等待时间
        self.totalNumPerson = 0# 总共服务的乘客人数
        self.maxLoadingNum = maxLoadingNum# 最大载客人数
        self.maxvelocity = maxvelocity# 电梯运行过程中的最大速度（即匀速时的速度）
        
    def isFull(self):# 判断电梯是否满
        return self.loadingPerson == self.maxLoadingNum
        
    def onFloor(self):
        #判断是否在一个整数楼层
        return self.remainingTime == 0 or self.remainingTime == self.timePerFloor
    
    def tick(self,currenttime):# 主程序，进行计时
        if (self.waitingPerson == 0 and
            self.loadingPerson == 0):
            return
        if self.remainingTime == 0:
            if self.currentDirection == 'up':
                self.currentFloor = self.currentFloor+1
            else:
                self.currentFloor = self.currentFloor-1
            if self.shouldStop():
                self.getOnAndOff(currenttime)
            if self.shouldChangeDirection():
                self.changeDirection()
            if self.shouldStop():
                self.getOnAndOff(currenttime)
                #重复写一次是为了避免一些特殊情况，节省电梯时间，见文件详述
            self.remainingTime = self.timePerFloor-1
            #这里的基本假设是上下乘客不需要时间（现在考虑假设每个乘客上下需要2秒）
        else:
            self.remainingTime = self.remainingTime-1
        self.timeInTotal += self.loadingPerson
    
    def shouldStop(self):# 判断是否需要停下来
        #这个函数只会在到达某一个楼层的时候调用
        # if self.remainingTime:
        #     raise SyntaxError('stop at nonfloor')好像不需要
        if not self.getOffQueue[self.currentFloor-1].is_empty():
            return True
        # if self.isFull():
        #     return False
            #在没有人下电梯的情况下，电梯满载才可以不停，如果有人下电梯，即使满载也要停
            # 改为满载也会停（符合实际）
        if (self.currentDirection == 'up' and
            not self.upWaitingQueue[self.currentFloor-1].is_empty()):
            return True
        if (self.currentDirection == 'down' and
            not self.downWaitingQueue[self.currentFloor-1].is_empty()):
            return True
        return False
            
    def getOnAndOff(self,currenttime):
        if not self.getOffQueue[self.currentFloor-1].is_empty():
            self.getOff(currenttime)
        #遵循先下后上的规则（可以考虑增加的功能是排队进电梯）
        self.getOn(currenttime)
            
    def getOff(self,currenttime):
        self.loadingPerson = (self.loadingPerson -
                              self.getOffQueue[self.currentFloor-1].size())
        self.totalNumPerson += self.getOffQueue[self.currentFloor-1].size()
        while not self.getOffQueue[self.currentFloor-1].is_empty():
            self.getOffQueue[self.currentFloor-1].dequeue()
             
    def getOn(self,currenttime):
        if (self.currentDirection == 'up' and
            (not self.upWaitingQueue[self.currentFloor-1].is_empty())):
            self.arriveUp(currenttime)
        if (self.currentDirection == 'down' and
            not self.downWaitingQueue[self.currentFloor-1].is_empty()):
            self.arriveDown(currenttime)
             
    def arriveUp(self,currenttime):
        while (not self.upWaitingQueue[self.currentFloor-1].is_empty()
               and not self.isFull()):
            person = self.upWaitingQueue[self.currentFloor-1].dequeue()
            self.getOffQueue[person.get_target_floor()-1].enqueue(person)# 这里没有考虑能不能都上去
            self.waitingTimes.append(person.WaitTime(currenttime))
            person.time_get_on = currenttime
            self.waitingPerson -= 1
            self.loadingPerson += 1
             
    def arriveDown(self,currenttime):
        while (not self.downWaitingQueue[self.currentFloor-1].is_empty()
               and not self.isFull()):
            person = self.downWaitingQueue[self.currentFloor-1].dequeue()
            self.getOffQueue[person.get_target_floor()-1].enqueue(person)# 这里没有考虑能不能都上去
            self.waitingTimes.append(person.WaitTime(currenttime))
            person.time_get_on = currenttime
            self.waitingPerson -= 1
            self.loadingPerson += 1
             
    def shouldChangeDirection(self):
        if self.currentDirection == 'up':# 改变方向的策略见说明
            if not self.is_passenger_upstairs():
                return True
            return False
        if self.currentDirection == 'down':
            if self.currentFloor == 1:
                return True
            
    def changeDirection(self):
        if self.currentDirection == 'up':
            self.currentDirection = 'down'
        elif self.currentDirection == 'down':
            self.currentDirection = 'up'

    # 判断楼上有没有正在等待的乘客
    def is_passenger_upstairs(self):
        for i in range(self.currentFloor, self.totalFloor):
            if self.upWaitingQueue[i - 1] and self.downWaitingQueue[i - 1]:
                return True
        return False
    
def simulation(numSeconds,totalFloor,timePerFloor,maxLoadingNum):
    elevator = Elevator(totalFloor,timePerFloor,maxLoadingNum)
    for currentSecond in range(numSeconds):
        if passengerComing():
            newpassenger = Passenger(currentSecond,totalFloor)
            startWaiting(elevator,newpassenger)
    
        elevator.tick(currentSecond)
    
    averageWait = sum(elevator.waitingTimes)/len(elevator.waitingTimes)
    averageLoad = elevator.timeInTotal/numSeconds
    averageSpendTime = elevator.timeInTotal/elevator.totalNumPerson
    print("""Average waiting %6.2f seconds, %3d persons on the elevator now, 
    there are totally %5d persons transported by the elevator,
    there are still %5d persons waiting now,
    average loadng %6.2f persons,
    average spending %6.2f seconds on the elevator."""
          %(averageWait,elevator.loadingPerson,elevator.totalNumPerson,
           elevator.waitingPerson,averageLoad,averageSpendTime),end = '\n\n')
    print(elevator.waitingTimes,end='\n\n')
             
def startWaiting(elevator,newpassenger):
    elevator.waitingPerson += 1
    if newpassenger.get_direction() == 'up':
        elevator.upWaitingQueue[newpassenger.get_init_floor()-1].enqueue(newpassenger)
    elif newpassenger.get_direction() == 'down':
        elevator.downWaitingQueue[newpassenger.get_init_floor()-1].enqueue(newpassenger)
    
def passengerComing():
    num = random.randrange(1,21)
    return num == 20

for i in range(10):
    print('Test',i+1,':')
    simulation(3600,10,5,10)
