import pygame, sys, random, itertools
import numpy as np
import pandas as pd
from pygame.locals import *
from collections import deque
import copy
import pyautogui
BOARDWIDTH = 3  
BOARDHEIGHT = 3 
N=3
TILESIZE = 120
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None

#                 R    G    B
BLACK =         (  0,   0,   0)
WHITE =         (255, 255, 255)
BLUE =         (  0,  50, 255)
GREEN = (  0,  255, 255)
BGCOLOR = WHITE
# TILECOLOR = BLUE
TEXTCOLOR = BLACK
BORDERCOLOR = BLACK
BASICFONTSIZE = 15
TEXT = BLACK
BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = BLACK

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)
UP = 'up' #variable for up, down, left, right
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT,SOLVE_SURF, SOLVE_RECT,NEXT_RECT,NEXT_SURF,TILECOLOR,clickable

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Slide Puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # Store the option buttons and their rectangles in OPTIONS.
    SOLVE_SURF, SOLVE_RECT = makeText('Solve as BFS',    TEXT, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 250)
    RESET_SURF, RESET_RECT = makeText('Reset',    TEXT, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 310)
    NEXT_SURF, NEXT_RECT = makeText('Solve as DFS',    TEXT, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 190)
    
    mainBoard = generateNewPuzzle()
    SOLVEDBOARD = getStartingBoard() # a solved board is the same as the board in a start state.
    allMoves = [] 
    i=0;
    j=0;
    clickable=0
    while True: # main game loop
        with open("puzzle.in", "r") as txt_file:
            board1 = [list(map(int, line.split())) for line in txt_file]
            state= [j for sub in board1 for j in sub]
        if isSolvable(board1):
            slideTo = None 
            msg = 'Solvable' # contains the message to show in the upper left corner.
        else:
            slideTo = None
            msg= 'Not Solvable'
        if mainBoard == SOLVEDBOARD:
            msg = 'Solved! Exitting the program'
            pyautogui.alert("you have finished the game,closing...")
            pygame.time.delay(3000)
            pygame.quit()
            sys.exit()
        drawBoard(mainBoard, msg)

        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    # check if the user clicked on an option button
                    if RESET_RECT.collidepoint(event.pos):
                        clickable=0
                        resetAnimation(mainBoard, allMoves) 
                        allMoves = []
                    elif SOLVE_RECT.collidepoint(event.pos):
                        clickable= 1;
                        TILECOLOR=GREEN;
                        if i==0:
                            resetAnimation(mainBoard, allMoves) 
                            allMoves = []
                        goal_state = [1, 2, 3, 4, 5, 6, 7, 8, 0] 
                        SOLVE_SURF, SOLVE_RECT = makeText('NEXT',    TEXT, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 250) #CHANGES THE TEXT UPON CLICKING SOLVE
                        solution=runBFS(state,goal_state);
                        soln=[];
                        for action in solution:
                            soln.append(action);
                        file2 = open("puzzle_out_BFS.txt", "w")
                        file2.writelines(soln) #writing the solution
                        file2.close();
                        print("Please check the folder for solution/answer at puzzle_out")
                        temp = soln[i];
                        if temp == 'L':
                            makeMove(mainBoard,RIGHT);
                        if temp == 'R':
                            makeMove(mainBoard,LEFT);
                        if temp == 'D':
                            makeMove(mainBoard,UP);
                        if temp == 'U':
                            makeMove(mainBoard,DOWN);
                        i+=1;
                    elif NEXT_RECT.collidepoint(event.pos):
                        clickable= 1;
                        TILECOLOR=GREEN;
                        if j==0:
                            resetAnimation(mainBoard, allMoves) 
                            allMoves = []
                        goal_state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
                        NEXT_SURF, NEXT_RECT = makeText('NEXT',    TEXT, BGCOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 190)
                        solution=runDFS(state,goal_state);
                        soln=[];
                        for action in solution:
                            soln.append(action);
                        file2 = open("puzzle_out_DFS.txt", "w")
                        file2.writelines(solution) #writing the solution TO PUZZLE.OUT
                        file2.close();
                        print("Please check the folder for solution/answer at puzzle_out")
                        temp = soln[j];
                        if temp == 'L':
                            makeMove(mainBoard,RIGHT);
                        if temp == 'R':
                            makeMove(mainBoard,LEFT);
                        if temp == 'D':
                            makeMove(mainBoard,UP);
                        if temp == 'U':
                            makeMove(mainBoard,DOWN);
                        j+=1;
                else:

                    if clickable==0:
                        blankx, blanky = getBlankPosition(mainBoard)
                        if spotx == blankx + 1 and spoty == blanky:
                            slideTo = LEFT
                        elif spotx == blankx - 1 and spoty == blanky:
                            slideTo = RIGHT
                        elif spotx == blankx and spoty == blanky + 1:
                            slideTo = UP
                        elif spotx == blankx and spoty == blanky - 1:
                            slideTo = DOWN

            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN

        if slideTo:
            slideAnimation(mainBoard, slideTo, 'Press the tile to slide', 8) 
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo) 
        pygame.display.update()
        FPSCLOCK.tick(FPS)

# ---------------------------------FOR EXER 2---------------------------------

class PuzzleNode:
    def __init__(self, state, parent, action):
        self.state = state  # Current state of the puzzle
        self.parent = parent  # Parent node
        self.action = action  # Action taken to reach this state

def runBFS(initial_state, goal_state):
    """
    Solve the 8-puzzle using breadth-first search.

    Args:
        initial_state (list): The initial state of the puzzle as a list.
        goal_state (list): The goal state of the puzzle as a list.

    Returns:
        list or None: A list of actions to solve the puzzle (e.g., ['Up', 'Left', ...]) or None if no solution is found.
    """
    def is_goal_state(state):
# Check if the given state is the goal state.

        return state == goal_state

    def get_possible_moves(state):
# Generate possible moves (neighbors) from the current state.
        moves = []
        empty_idx = state.index(0)
        row, col = empty_idx // 3, empty_idx % 3

        # Define possible moves: up, down, left, right
        possible_moves = [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]

        for dr, dc, action in possible_moves:
            new_row, new_col = row + dr, col + dc

            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_state = state[:]
                new_idx = new_row * 3 + new_col
                new_state[empty_idx], new_state[new_idx] = new_state[new_idx], new_state[empty_idx]
                moves.append((new_state, action))

        return moves

    def bfs_search():
        """Perform breadth-first search to find the solution."""
        queue = deque([PuzzleNode(initial_state, None, None)])
        visited = set()

        while queue:
            node = queue.popleft()

            if is_goal_state(node.state):
                return get_solution_path(node)

            visited.add(tuple(node.state))

            for move, action in get_possible_moves(node.state):
                if tuple(move) not in visited:
                    child_node = PuzzleNode(move, node, action)
                    queue.append(child_node)

        return None

    def get_solution_path(node):
# Reconstruct the solution path from the goal node
        path = []
        while node.parent:
            path.append(node.action)
            node = node.parent
        path.reverse()
        return path

    solution_path = bfs_search()
    return solution_path

#           FOR DFS
def runDFS(initial_state, goal_state):
    # Solve the 8-puzzle using depth-first search.

    # Args:
        # initial_state (list): The initial state of the puzzle as a list.
        # goal_state (list): The goal state of the puzzle as a list.
    def is_goal_state(state):
        return state == goal_state

    def get_possible_moves(state):
        
        empty_idx = state.index(0)
        row, col = empty_idx // 3, empty_idx % 3
        moves=[]
        # Define possible moves: up, down, left, right
        possible_moves = [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]

        for dr, dc, action in possible_moves:
            new_row, new_col = row + dr, col + dc

            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_state = state[:]
                new_idx = new_row * 3 + new_col
                new_state[empty_idx], new_state[new_idx] = new_state[new_idx], new_state[empty_idx]
                moves.append((new_state, action))
        return moves

    def dfs_search():
        """Perform depth-first search to find the solution."""
        stack = [PuzzleNode(initial_state, None, None)]
        visited = set()

        while stack:
            node = stack.pop()

            if is_goal_state(node.state):
                return get_solution_path(node)

            visited.add(tuple(node.state))

            for move, action in get_possible_moves(node.state):
                if tuple(move) not in visited:
                    child_node = PuzzleNode(move, node, action)
                    stack.append(child_node)

        return None

    def get_solution_path(node):
# Reconstruct the solution path from the goal node.
        path = []
        while node.parent:
            path.append(node.action)
            node = node.parent
        path.reverse()
        return path
    solution_path = dfs_search()
    return solution_path

# ---------------------------------FROM EXER 1---------------------------------

def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT): 
        terminate()
    for event in pygame.event.get(KEYUP): 
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event) 

     
def isSolvable(table):
    temp = []
    inversions = 0
    #for converting to one single array
    for i in range(0, len(table)):
        for j in range(0, len(table)):
            temp.append(table[i][j])
    #for counting of inversions
    for r in range(0, len(temp)):
        for c in range(r+1, len(temp)):
            if temp[r] > temp[c]:
                inversions = inversions + 1
    
    #checking if odd or even
    if (inversions % 2 == 0):
        return True;
    else:
        return False;
    #for initialization of starting board
def getStartingBoard():
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH
        board.append(column)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1
    board[BOARDWIDTH-1][BOARDHEIGHT-1] = BLANK
    return board

#For finding out where the number 0 or 9 is
def getBlankPosition(board):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == BLANK:
                return (x, y)

#function for moving tiles
def makeMove(board, move):
    blankx, blanky = getBlankPosition(board)

    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]

#function for checking whether the clicked tile is movable or not
def isValidMove(board, move):
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != len(board) - 1) or \
           (move == RIGHT and blankx != 0)


def getRandomMove(board, lastMove=None):
    validMoves = [UP, DOWN, LEFT, RIGHT]

    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
    top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


def drawTile(tilex, tiley, number, adjx=0, adjy=0):
    left, top = getLeftTopOfTile(tilex, tiley)
    if clickable==0:
        TILECOLOR=BLUE
    else:
        TILECOLOR=GREEN
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE))
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
    DISPLAYSURF.blit(textSurf, textRect)

#For GUI
def makeText(text, color, bgcolor, top, left):
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)

#for the displaying of the board
def drawBoard(board, message):
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])

    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)
    DISPLAYSURF.blit(NEXT_SURF, NEXT_RECT)
#for the GUI of slide animation
def slideAnimation(board, direction, message, animationSpeed):

    blankx, blanky = getBlankPosition(board)
    if direction == UP:
        movex = blankx
        movey = blanky + 1
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky

    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()
    moveLeft, moveTop = getLeftTopOfTile(movex, movey)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, animationSpeed):
        checkForQuit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -i)
        if direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, i)
        if direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -i, 0)
        if direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

#for initializing the puzzle
def generateNewPuzzle():
    sequence = []
    board = getStartingBoard()
    with open("puzzle.in", "r") as txt_file:
        board = [list(map(int, line.split())) for line in txt_file]
    board=[list(i) for i in zip(*board)]
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y]==0:
                board[x][y] = BLANK
    return (board)

#function for reseting the table
def resetAnimation(board, allMoves):
    revAllMoves = allMoves[:] #for copy
    revAllMoves.reverse()
    for move in revAllMoves:
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, '', animationSpeed=int(TILESIZE / 2))
        makeMove(board, oppositeMove)


if __name__ == '__main__':
    main()