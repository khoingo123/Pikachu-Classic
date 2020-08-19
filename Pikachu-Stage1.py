import pygame, sys, random, copy, time, collections, os
from pygame.locals import *

FPS = 10
WINDOWWIDTH = 960
WINDOWHEIGHT = 640
BOXSIZE = 60
BOARDWIDTH = 14
BOARDHEIGHT = 9
NUMPOKES = 21
NUMSAMEPOKES = 4
TIMEBAR_LENGTH = 300
TIMEBAR_WIDTH = 30
LEVELMAX = 5
LIVES = 10
GAMETIME = 240

XMARGIN = (WINDOWWIDTH - (BOXSIZE * BOARDWIDTH)) // 2
YMARGIN = (WINDOWHEIGHT - (BOXSIZE * BOARDHEIGHT)) // 2

# set up the colors
GRAY = (100, 100, 100)
NAVYBLUE = ( 60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = ( 0, 255, 0)
BOLDGREEN = (0, 175, 0)
BLUE = ( 0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = ( 0, 255, 255)
BLACK = (0, 0, 0)
BGCOLOR = NAVYBLUE
HIGHLIGHTCOLOR = BLUE
BORDERCOLOR = RED

# TIMEBAR setup
barPos = (WINDOWWIDTH // 2 - TIMEBAR_LENGTH // 2, YMARGIN // 2 - TIMEBAR_WIDTH // 2)
barSize = (TIMEBAR_LENGTH, TIMEBAR_WIDTH)
borderColor = BLACK
barColor = BOLDGREEN

# Make a dict to store scaled images
os.chdir('/Users/Administrator/PycharmProjects/dis me python/Pikachu/hero_icon')
NUMHEROES = len(os.listdir())
HEROES_DICT = {}

for i in range(len(os.listdir())):
    HEROES_DICT[i + 1] = pygame.transform.scale(pygame.image.load(os.listdir()[i]), (BOXSIZE, BOXSIZE))
os.chdir('/Users/Administrator/PycharmProjects/dis me python/Pikachu/')

# Make a dict to store scaled images
POKEMON_DICT = {}
for x in range(1, 22):
    pic = pygame.image.load('{}.png'.format(x))
    pic = pygame.transform.scale(pic, (BOXSIZE, BOXSIZE))
    POKEMON_DICT[x] = pic

# Load pictures
aegis = pygame.image.load('aegis_2.jpg')
aegis = pygame.transform.scale(aegis, (45, 45))

# Load background
startBG = pygame.image.load('dota_background/startBG.jpg')
startBG = pygame.transform.scale(startBG, (WINDOWWIDTH, WINDOWHEIGHT))

listBG = [pygame.image.load('dota_background/{}.jpg'.format(i)) for i in range(9)]
for i in range(len(listBG)):
    listBG[i] = pygame.transform.scale(listBG[i], (WINDOWWIDTH, WINDOWHEIGHT))

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, LIVESFONT, LEVEL
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Pikachu Classic')
    BASICFONT = pygame.font.SysFont('comicsansms', 70)
    LIVESFONT = pygame.font.SysFont('comicsansms', 45)

    while True:
        random.shuffle(listBG)
        LEVEL = 1
        showStartScreen()
        while LEVEL <= LEVELMAX:
            runGame()
            LEVEL += 1
            pygame.time.wait(1000)
        showGameOverScreen()

def showStartScreen():
    while True:
        DISPLAYSURF.blit(startBG, (0, 0))
        newGameSurf = BASICFONT.render('NEW GAME', True, WHITE)
        newGameRect = newGameSurf.get_rect()
        newGameRect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2)
        DISPLAYSURF.blit(newGameSurf, newGameRect)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if newGameRect.collidepoint((mousex, mousey)):
                    # If click to New Game rect, the game starts
                    return

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def runGame():
    mainBoard = getRandomizedBoard()
    clickedBoxes = [] # stores the (x, y) of clicked boxes
    firstSelection = None # stores the (x, y) of the first box clicked
    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event
    lastTimeGetPoint = time.time()
    hint = getHint(mainBoard)

    global GAMETIME, LEVEL, LIVES, TIMEBONUS, STARTTIME
    STARTTIME = time.time()
    TIMEBONUS = 0
    randomBG = listBG[LEVEL]

    while True:
        mouseClicked = False

        DISPLAYSURF.blit(randomBG, (0, 0))
        drawBoard(mainBoard)
        drawClickedBox(mainBoard, clickedBoxes)
        drawTimeBar()
        drawLives()

        if time.time() - STARTTIME > GAMETIME + TIMEBONUS:
            LEVEL = LEVELMAX + 1
            return
        if time.time() - lastTimeGetPoint >= 5:
            drawHint(hint)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey == event.pos
                mouseClicked = True
            if event.type == KEYUP:
                if event.key == K_n:
                    boxy1, boxx1 = hint[0][0], hint[0][1]
                    boxy2, boxx2 = hint[1][0], hint[1][1]
                    mainBoard[boxy1][boxx1] = 0
                    mainBoard[boxy2][boxx2] = 0
                    TIMEBONUS += 2
                    alterBoardWithLevel(mainBoard, boxy1, boxx1, boxy2, boxx2, LEVEL)

                    if isGameComplete(mainBoard):
                        drawBoard(mainBoard)
                        pygame.display.update()
                        return

                    if not(mainBoard[boxy1][boxx1] != 0 and bfs(mainBoard, boxy1, boxx1, boxy2, boxx2)):
                        hint = getHint(mainBoard)
                        while not hint:
                            pygame.time.wait(100)
                            resetBoard(mainBoard)
                            LIVES += -1
                            if LIVES == 0:
                                LEVEL = LEVELMAX + 1
                                return

                            hint = getHint(mainBoard)

        boxx, boxy = getBoxAtPixel(mousex, mousey)

        if boxx != None and boxy != None and mainBoard[boxy][boxx] != 0:
            # The mouse is currently over a box
            drawHighlightBox(mainBoard, boxx, boxy)

        if boxx != None and boxy != None and mainBoard[boxy][boxx] != 0 and mouseClicked == True:
            # The mouse is clicking on a box
            clickedBoxes.append((boxx, boxy))
            drawClickedBox(mainBoard, clickedBoxes)
            mouseClicked = False

            if firstSelection == None:
                firstSelection = (boxx, boxy)
            else:
                path = bfs(mainBoard, firstSelection[1], firstSelection[0], boxy, boxx)
                if path:
                    mainBoard[firstSelection[1]][firstSelection[0]] = 0
                    mainBoard[boxy][boxx] = 0
                    drawPath(mainBoard, path)
                    TIMEBONUS += 2
                    lastTimeGetPoint = time.time()
                    alterBoardWithLevel(mainBoard, firstSelection[1], firstSelection[0], boxy, boxx, LEVEL)

                    if isGameComplete(mainBoard):
                        drawBoard(mainBoard)
                        pygame.display.update()
                        return
                    if not(mainBoard[hint[0][0]][hint[0][1]] != 0 and bfs(mainBoard, hint[0][0], hint[0][1], hint[1][0], hint[1][1])):
                        hint = getHint(mainBoard)
                        while not hint:
                            pygame.time.wait(500)
                            resetBoard(mainBoard)
                            LIVES += -1
                            if LIVES == 0:
                                LEVEL = LEVELMAX + 1
                                return

                            hint = getHint(mainBoard)

                clickedBoxes = []
                firstSelection = None

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def getRandomizedBoard():
    list_pokemons = list(range(1, NUMPOKES + 1)) * NUMSAMEPOKES
    random.shuffle(list_pokemons)
    board = [[0 for _ in range(BOARDWIDTH)] for _ in range(BOARDHEIGHT)]

    # We create a board of images surrounded by 4 arrays of zeroes
    k = 0
    for i in range(1, BOARDHEIGHT - 1):
        for j in range(1, BOARDWIDTH - 1):
            board[i][j] = list_pokemons[k]
            k += 1
    return board

def leftTopCoordsOfBox(boxx, boxy):
    left = boxx * BOXSIZE + XMARGIN
    top = boxy * BOXSIZE + YMARGIN
    return left, top

def getBoxAtPixel(x, y):
    if x <= XMARGIN or x >= WINDOWWIDTH - XMARGIN or y <= YMARGIN or y >= WINDOWHEIGHT - YMARGIN:
        return None, None
    return (x - XMARGIN) // BOXSIZE, (y - YMARGIN) // BOXSIZE

def drawBoard(board):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            if board[boxy][boxx] != 0:
                left, top = leftTopCoordsOfBox(boxx, boxy)
                boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
                DISPLAYSURF.blit(POKEMON_DICT[board[boxy][boxx]], boxRect)

def drawHighlightBox(board, boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 2, top - 2,
                                                   BOXSIZE + 4, BOXSIZE + 4), 2)

def drawClickedBox(board, clickedBoxes):
    for boxx, boxy in clickedBoxes:
        left, top = leftTopCoordsOfBox(boxx, boxy)
        boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
        image = POKEMON_DICT[board[boxy][boxx]].copy()

        # Darken the clicked image
        image.fill((50, 50, 50), special_flags=pygame.BLEND_RGB_SUB)
        DISPLAYSURF.blit(image, boxRect)

        # Draw a red border line around to easily identify
        pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left, top,
                                                       BOXSIZE,
                                                       BOXSIZE), 2)

def bfs(board, boxy1, boxx1, boxy2, boxx2):
    def backtrace(parent, boxy1, boxx1, boxy2, boxx2):
        start = (boxy1, boxx1, 0, 'no_direction')
        end = 0
        for node in parent:
            if node[:2] == (boxy2, boxx2):
                end = node

        path = [end]
        while path[-1] != start:
            path.append(parent[path[-1]])
        path.reverse()

        for i in range(len(path)):
            path[i] = path[i][:2]
        return path

    if board[boxy1][boxx1] != board[boxy2][boxx2]:
        return []

    n = len(board)
    m = len(board[0])

    import collections
    q = collections.deque()
    q.append((boxy1, boxx1, 0, 'no_direction'))
    visited = set()
    visited.add((boxy1, boxx1, 0))
    parent = {}

    while len(q) > 0:
        r, c, num_turns, direction = q.popleft()
        if (r, c) != (boxy1, boxx1) and (r, c) == (boxy2, boxx2):
            return backtrace(parent, boxy1, boxx1, boxy2, boxx2)

        dict_directions = {(r + 1, c): 'down', (r - 1, c): 'up', (r, c - 1): 'left',
                           (r, c + 1): 'right'}
        for neiborX, neiborY in dict_directions:
            if 0 <= neiborX <= n - 1 and 0 <= neiborY <= m - 1 and (
                    board[neiborX][neiborY] == 0 or (neiborX, neiborY) == (boxy2, boxx2)):
                if direction == 'no_direction':
                    q.append((neiborX, neiborY, num_turns, dict_directions[(neiborX, neiborY)]))
                    visited.add((neiborX, neiborY, num_turns))
                    parent[(neiborX, neiborY, num_turns, dict_directions[(neiborX, neiborY)])] = (
                    r, c, num_turns, direction)
                elif direction == dict_directions[(neiborX, neiborY)] and (
                        neiborX, neiborY, num_turns) not in visited:
                    q.append((neiborX, neiborY, num_turns, dict_directions[(neiborX, neiborY)]))
                    visited.add((neiborX, neiborY, num_turns))
                    parent[(neiborX, neiborY, num_turns, dict_directions[(neiborX, neiborY)])] = (
                    r, c, num_turns, direction)
                elif direction != dict_directions[(neiborX, neiborY)] and num_turns < 2 and (
                        neiborX, neiborY, num_turns + 1) not in visited:
                    q.append((neiborX, neiborY, num_turns + 1, dict_directions[(neiborX, neiborY)]))
                    visited.add((neiborX, neiborY, num_turns + 1))
                    parent[
                        (neiborX, neiborY, num_turns + 1, dict_directions[(neiborX, neiborY)])] = (
                    r, c, num_turns, direction)
    return []

def getCenterPos(pos): # pos is coordinate of a box in mainBoard
    left, top = leftTopCoordsOfBox(pos[1], pos[0])
    return tuple([left + BOXSIZE // 2, top + BOXSIZE // 2])

def drawPath(board, path):
    for i in range(len(path) - 1):
        startPos = getCenterPos(path[i])
        endPos = getCenterPos(path[i + 1])
        pygame.draw.line(DISPLAYSURF, RED, startPos, endPos, 4)
    pygame.display.update()
    pygame.time.wait(300)

def drawTimeBar():
    progress = 1 - ((time.time() - STARTTIME - TIMEBONUS) / GAMETIME)

    pygame.draw.rect(DISPLAYSURF, borderColor, (barPos, barSize), 1)
    innerPos = (barPos[0] + 2, barPos[1] + 2)
    innerSize = ((barSize[0] - 4) * progress, barSize[1] - 4)
    pygame.draw.rect(DISPLAYSURF, barColor, (innerPos, innerSize))

def showGameOverScreen():
    playAgainFont = pygame.font.Font('freesansbold.ttf', 50)
    playAgainSurf = playAgainFont.render('Play Again?', True, PURPLE)
    playAgainRect = playAgainSurf.get_rect()
    playAgainRect.center = (WINDOWWIDTH // 2, WINDOWHEIGHT // 2)
    DISPLAYSURF.blit(playAgainSurf, playAgainRect)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if playAgainRect.collidepoint((mousex, mousey)):
                    return

def getHint(board):
    boxPokesLocated = collections.defaultdict(list)
    hint = []
    for boxy in range(BOARDHEIGHT):
        for boxx in range(BOARDWIDTH):
            if board[boxy][boxx] != 0:
                boxPokesLocated[board[boxy][boxx]].append((boxy, boxx))
    for boxy in range(BOARDHEIGHT):
        for boxx in range(BOARDWIDTH):
            if board[boxy][boxx] != 0:
                for otherBox in boxPokesLocated[board[boxy][boxx]]:
                    if otherBox != (boxy, boxx) and bfs(board, boxy, boxx, otherBox[0], otherBox[1]):
                        hint.append((boxy, boxx))
                        hint.append(otherBox)
                        return hint
    return []

def drawHint(hint):
    for boxy, boxx in hint:
        left, top = leftTopCoordsOfBox(boxx, boxy)
        pygame.draw.rect(DISPLAYSURF, GREEN, (left, top,
                                                       BOXSIZE, BOXSIZE), 2)

def resetBoard(board):
    pokesOnBoard = []
    for boxy in range(BOARDHEIGHT):
        for boxx in range(BOARDWIDTH):
            if board[boxy][boxx] != 0:
                pokesOnBoard.append(board[boxy][boxx])
    referencedList = pokesOnBoard[:]
    while referencedList == pokesOnBoard:
        random.shuffle(pokesOnBoard)

    i = 0
    for boxy in range(BOARDHEIGHT):
        for boxx in range(BOARDWIDTH):
            if board[boxy][boxx] != 0:
                board[boxy][boxx] = pokesOnBoard[i]
                i += 1
    return board

def isGameComplete(board):
    for boxy in range(BOARDHEIGHT):
        for boxx in range(BOARDWIDTH):
            if board[boxy][boxx] != 0:
                return False
    return True

def alterBoardWithLevel(board, boxy1, boxx1, boxy2, boxx2, level):

    # Level 2: All the pokemons move up to the top boundary
    if level == 2:
        for boxx in (boxx1, boxx2):
            # rearrange pokes into a current list
            cur_list = [0]
            for i in range(BOARDHEIGHT):
                if board[i][boxx] != 0:
                    cur_list.append(board[i][boxx])
            while len(cur_list) < BOARDHEIGHT:
                cur_list.append(0)

            # add the list into the board
            j = 0
            for num in cur_list:
                board[j][boxx] = num
                j += 1

    # Level 3: All the pokemons move down to the bottom boundary
    if level == 3:
        for boxx in (boxx1, boxx2):
            # rearrange pokes into a current list
            cur_list = []
            for i in range(BOARDHEIGHT):
                if board[i][boxx] != 0:
                    cur_list.append(board[i][boxx])
            cur_list.append(0)
            cur_list = [0] * (BOARDHEIGHT - len(cur_list)) + cur_list

            # add the list into the board
            j = 0
            for num in cur_list:
                board[j][boxx] = num
                j += 1

    # Level 4: All the pokemons move left to the left boundary
    if level == 4:
        for boxy in (boxy1, boxy2):
            # rearrange pokes into a current list
            cur_list = [0]
            for i in range(BOARDWIDTH):
                if board[boxy][i] != 0:
                    cur_list.append(board[boxy][i])
            while len(cur_list) < BOARDWIDTH:
                cur_list.append(0)

            # add the list into the board
            j = 0
            for num in cur_list:
                board[boxy][j] = num
                j += 1

    # Level 5: All the pokemons move right to the right boundary
    if level == 5:
        for boxy in (boxy1, boxy2):
            # rearrange pokes into a current list
            cur_list = []
            for i in range(BOARDWIDTH):
                if board[boxy][i] != 0:
                    cur_list.append(board[boxy][i])
            cur_list.append(0)
            cur_list = [0] * (BOARDWIDTH - len(cur_list)) + cur_list

            # add the list into the board
            j = 0
            for num in cur_list:
                board[boxy][j] = num
                j += 1

    return board

def drawLives():
    aegisRect = pygame.Rect(10, 10, BOXSIZE, BOXSIZE)
    DISPLAYSURF.blit(aegis, aegisRect)
    livesSurf = LIVESFONT.render(str(LIVES), True, WHITE)
    livesRect = livesSurf.get_rect()
    livesRect.topleft = (65, 0)
    DISPLAYSURF.blit(livesSurf, livesRect)

if __name__ == '__main__':
    main()



