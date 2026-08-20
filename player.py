from board import Direction, Rotation, Action, Shape
from random import Random
import time


class Player:
    def choose_action(self, board):
        raise NotImplementedError


class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x,y) in board.cells:
                    s += "#"
                else:
                    s += "."
            print(s, y)
                

            

    def choose_action(self, board):
        self.print_board(board)
        time.sleep(0.5)
        if self.random.random() > 0.97:
            # 3% chance we'll discard or drop a bomb
            return self.random.choice([
                Action.Discard,
                Action.Bomb,
            ])
        else:
            # 97% chance we'll make a normal move
            return self.random.choice([
                Direction.Left,
                Direction.Right,
                Direction.Down,
                Rotation.Anticlockwise,
                Rotation.Clockwise,
            ])

class PratiksPlayer(Player):
    def __init__(self):
        self.discards = 0
        self.bombs = 0
    
    def printBoard(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x,y) in board.cells:
                    s += "#"
                elif (x,y) in self.getHoles():
                    s += "H"
                else:
                    s += "."
            print(s, y)
    
    
    def getMaxHeight(self, sandbox):
        maxHeight = -1000
        
        for x in range(sandbox.width):
            currentHeight = self.getColumnHeight(x, sandbox)
            if currentHeight > maxHeight:
                maxHeight = currentHeight
                
        return maxHeight
            
        
    def getColumnHeight(self, x, sandbox):
        colHeight = 0
        for y in range(0, sandbox.height):
            if (x, y) in sandbox.cells:
                colHeight += (sandbox.height-y)
                break
        return colHeight
    
            
    def getHoles(self, sandbox):
        #hole is an unoccupied cell, or a group of unoccupied cells, that have an occupied block above them  
        
        holes = set()
        
        for x in range(sandbox.width):
            for y in range(sandbox.height - self.getColumnHeight(x, sandbox), sandbox.height): #only checks each column til its max occupied height, for efficiency (since holes can't exist above the highest block in a column)
                if (x,y) in sandbox.cells:
                    i = 1
                    while y+i < 24 and (x,y+i) not in sandbox.cells:
                        holes.add((x,y+i))
                        i += 1
        
        return holes
                    
    
    def isRightmostColFull(self, sandbox):
        rightMostCol = sandbox.width-1
        if self.getColumnHeight(rightMostCol, sandbox) > 0:
            return 1
        else:
            return 0   

        
    def completedLines(self, line, sandbox):
        #a complete line is a full row (same y, different x)
        return all((x, line) in sandbox.cells for x in range(0, sandbox.width-1))
    
    def numberOfCompletedLines(self, sandbox):

        
        global lastScore
        diffScore = sandbox.score - lastScore

        if diffScore >= 1600:
            return 4
        elif diffScore >= 400:
            return 3
        elif diffScore >= 100:
            return 2
        elif diffScore >= 42:
            return 1
        else:
            return 0
                  
        
    def bumpiness(self, sandbox):
        bumpiness = 0
        for x in range(sandbox.width-2):
            bumpiness += abs(self.getColumnHeight(x, sandbox) - self.getColumnHeight(x+1, sandbox))
        
        return bumpiness
        
    
    def aggregateHeight(self, sandbox):
        aggregateHeight = 0
        
        for x in range(sandbox.width):
            aggregateHeight += self.getColumnHeight(x, sandbox)

        return aggregateHeight       
                    
        
            
    

    def scoreBoard(self, sandbox):
        #main heuristic function, will look at the position of the given board (sandbox) and return the score value that it should have, 
        #based on holes, height etc

        numberOfHoles = len(self.getHoles(sandbox))
        maxHeight = self.getMaxHeight(sandbox) 
        rightmostCol = self.isRightmostColFull(sandbox)
        completedLines = self.numberOfCompletedLines(sandbox)
        bumpiness = self.bumpiness(sandbox)
        aggregateHeight = self.aggregateHeight(sandbox)
        
        #Weights
        holesWeight = -100
        maxHeightWeight = -7
        rightmostColWeight = -30
        completedLinesWeight = 0
        bumpinessWeight = -13
        aggregateHeightWeight = 0
        

    
             
        if completedLines > 2:
            completedLinesWeight = 1001
        else:
            completedLinesWeight = 0

        if maxHeight > 15:
            maxHeightWeight = -300
            rightmostColWeight = 0
            aggregateHeightWeight = -400
            bumpinessWeight = -20
            completedLinesWeight = 400
        
        score = numberOfHoles * holesWeight + maxHeight * maxHeightWeight + rightmostCol * rightmostColWeight + completedLines * completedLinesWeight + bumpiness * bumpinessWeight + aggregateHeight * aggregateHeightWeight
        return score
    
    
    
    
    def rightMostCell(self):
        rightMost = 0
        
        for (x,y) in sandbox.falling.cells:
            current = x 
            if current > rightMost:
                rightMost = current
        
        return rightMost

    def leftMostCell(self):
        leftMost = sandbox.width
        
        for (x,y) in sandbox.falling.cells:
            current = x 
            if current < leftMost:
                leftMost = current
        
        return leftMost       
    
    def moveToTarget(self, sandbox, t_pos, t_rot):
        movesDone = []
        
        #rotates until it gets to the given position
        rotationsDone = 0
        while sandbox.falling != None and rotationsDone < t_rot:
            sandbox.rotate(Rotation.Clockwise)
            movesDone.append(Rotation.Clockwise)
            rotationsDone += 1
        
        #moves horizontally to given position
        if t_pos <= 4 and t_pos >= 0:
            while sandbox.falling != None and self.leftMostCell() > t_pos:
                sandbox.move(Direction.Left)
                movesDone.append(Direction.Left)
                   
        elif t_pos > 4 and t_pos <= 9:
            while sandbox.falling != None and self.rightMostCell() < t_pos:
                sandbox.move(Direction.Right)
                movesDone.append(Direction.Right)
    
        
        #drops block and then returns the moves it has done
        if sandbox.falling == None:
            #block crashed while trying to move to the given position, so returning an empty list to indicate that this move is not legal
            return []
        else:
            sandbox.move(Direction.Drop)
            movesDone.append(Direction.Drop)  
            return movesDone


    
    def choose_action(self, board):
        global sandbox, lastScore
        bestScore = -10000000000
        bestMove = [Direction.Drop] #default move is to drop
        oldHoles = len(self.getHoles(board))
        lastScore = board.score
        
        
        possibleRotations = 4
        if board.falling.shape == Shape.I:
            possibleRotations = 2
        elif board.falling.shape == Shape.O:
            possibleRotations = 1
            
        for position in range(0, 10):
            for rotation in range(0,possibleRotations):
                sandbox = board.clone()
                currentMove = self.moveToTarget(sandbox, position, rotation)
                if currentMove == []:
                    #if move led to a block being crashed, dont evaluate this position/rotation further
                    continue
                
                currentScore = self.scoreBoard(sandbox)


                if currentScore > bestScore:
                    bestScore = currentScore
                    bestMove = currentMove
                    bestSandbox = sandbox.clone()
                
        
        if len(self.getHoles(bestSandbox)) > oldHoles and self.discards < 10 and bestSandbox.score - lastScore < 1000:
            bestMove = Action.Discard
            self.discards += 1
        
        return bestMove



SelectedPlayer = PratiksPlayer
