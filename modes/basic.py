from __future__ import annotations
import abc
import copy
from typing import Literal
from pygame import sprite, Surface, Rect
from collections.abc import Generator, Callable

type Path=str
type Coord=tuple[int,int]
type BoardCoord=tuple[int,int]
type BoardLayout=list[list[Tile]]

numbers=["0","1","2","3","4","5","6","7","8","9"]
letters=["","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]

class Piece(sprite.Sprite, abc.ABC):
    '''A piece. Does not display itself, that's the Tile's job.'''
    def __init__(self, name:str, value:int, colour:Literal["black","white","any"], initpos:BoardCoord, imagewhite:Surface, imageblack:Surface|None=None):
        '''Attributes common to all pieces'''
        super().__init__()
        self.name=name
        self.value=value
        self.colour=colour
        self.initpos=initpos
        if self.colour == "black":
            self.image=imageblack
        else:
            self.image=imagewhite
        self.parent:Tile|None=None
        self.promotes_to:list[Piece]|None=None
        self.promote_pos:list[BoardCoord]|None=None

    @abc.abstractmethod
    def moves(self) -> list[BoardCoord]:
        pass

    @abc.abstractmethod
    def capture_squares(self) -> list[BoardCoord]:
        pass

    @abc.abstractmethod
    def move_to(self, final:Tile) -> Piece:
        '''Move to a Tile. What really happens is that it removes itself from the previous Tile and returns what should be in the Tile it moves to. Actually setting the Tile's piece to that is handled by the game.'''
        return

class Tile():
    '''A container for tile information'''
    def __init__(self, boardcoord:BoardCoord, base:Literal["empty", "void"], colour:Literal["dark","light"]|None=None):
        self.boardcoord=boardcoord
        self.base=base
        self.coord:Coord|None=None
        self.piece:Piece|None=None
        self.image:Surface|None=None
        self.colour=colour
        self.rect:Rect|None=None

    def display(self, surface:Surface):
        surface.blit(self.piece.image, self.coord)

class Board():
    '''Everything to do with the construction and management of boards.'''
    def __init__(self, height:int, width:int, layout:list[list[str]]=None, initpos:list[list[str]]=None, piecesdict:dict[str,Piece]=None):
        self.height=height #difference between highest and lowest point
        self.width=width #difference between rightmost and leftmost point
        self.layout=layout #specific tile layout. If None, a square is assumed. Numbers for full spaces, letters for empty ones.
        self.initpos=initpos #a similar format to layout, with numbers indicating piceless squares and letters according to piecesdict indicating pieces
        self.piecesdict=piecesdict#dictionary containing the pieces that go on the board, and the letters that represent them.
        self.full_layout:BoardLayout|None=None #full layout, the one that is used for everything
        self.image:Surface|None=None #what the board looks like

    def construct(self) -> BoardLayout:
        '''Returns a list of lists representing the full board without intial pieces placed. Spaces with tiles are called "empty". For non-quadrilateral boards, non-tile spaces are called "void".'''
        result=[]
        count=0
        if self.layout == None:
            for i in range(self.height):
                temp=[]
                for j in range(self.width):
                    temp.append(Tile((j,i),"empty"))
                result.append(temp)
        else:
            for i in range(len(self.layout)):
                temp=[]
                for j in len(self.layout[i]):
                    code=self.layout[i][j]
                    if code in numbers:
                        for k in range(int(code)):
                            temp.append(Tile((j,i),"empty","light" if count%2 == 0 else "dark"))
                            count += 1
                    elif code in letters:
                        for k in range(letters.index(code)):
                            temp.append(Tile((j,i),"void"))
                            count += 1
                    else:
                        raise TypeError(f"Invalid value: {code}")
                result.append(temp)
        self.full_layout=None
    
    def populate(self) -> BoardLayout:
        full_board=self.full_layout
        '''Takes in a constructed board and populates it with pieces.'''
        if self.initpos != None and self.piecesdict != None:
            for i in len(self.initpos):
                cur_pos=0
                for code in self.initpos[i]:
                    if code in numbers:
                        cur_pos += int(code)
                    elif code in self.piecesdict:
                        full_board[i][cur_pos].piece=copy.copy(self.piecesdict[code])
                        full_board[i][cur_pos].piece.parent=full_board[i][cur_pos]
                        full_board[i][cur_pos].piece.initpos=(cur_pos,i)
                        cur_pos += 1
                    else:
                        raise TypeError(f"Invalid value: {code}")
        self.full_layout=full_board
    
    def construct_img(self, light:Surface, dark:Surface, void:Surface, whole:Surface|None=None) -> Surface:
        if whole == None:
            layout=self.full_layout
            height=len(layout)
            width=len(layout[0])
            base=Surface((100*width,100*height))
            for i in range(height):
                for j in range(width):
                    if layout[i][j].base == "void":
                        base.blit(void,(100*j,100*i))
                    elif layout[i][j].base == "empty":
                        if layout[i][j].colour == "light":
                            base.blit(light,(100*j,100*i))
                        elif layout[i][j].colour == "dark":
                            base.blit(dark,(100*j,100*i))
            self.image=base
        else:
            self.image=whole

    def make_tile_hitboxes(self, anchor:Coord, rect_size:Coord):
        height=len(self.full_layout)
        width=len(self.full_layout[0])
        for y in range(len(height)):
            for x in range(len(width)):
                target=self.full_layout[y][x]
                if target.base != "void":
                    target.rect=Rect(anchor[0]+(target.boardcoord[0]*rect_size[0]),anchor[1]+(target.boardcoord[1]*rect_size[1]))
    
class Movement():
    @staticmethod
    def out_of_bounds(board:list[list[str]], coord:Coord) -> bool:
        '''Check if a coordinate is outside the bounds of the board'''
        if board[coord[1]][coord[0]] != "void":
            return False
        else:
            return True
        
    @staticmethod
    def to_list(gen:Generator) -> list:
        '''Convert a movement generator to a list'''
        return [entry for entry in gen]
    
    @staticmethod
    def forward(max_height:int, limit:int, coord:Coord, layout:BoardLayout):
        count=0
        while (coord[1]+count+1) <= max_height and count <= limit and layout[coord[1]+count+1][coord[0]].piece == None:
            count += 1
            yield (coord[0],coord[1]+count)

    @staticmethod
    def backward(max_depth:int, limit:int, coord:Coord, layout:BoardLayout):
        count=0
        while (coord[1]-count-1) >= max_depth and count <= limit and layout[coord[1]-count-1][coord[0]].piece == None:
            count += 1
            yield (coord[0],coord[1]-count)

    @staticmethod
    def left(max_left:int, limit:int, coord:Coord, layout:BoardLayout):
        count=0
        while (coord[0]-count-1) >= max_left and count <= limit and layout[coord[1]][coord[0]-count-1].piece == None:
            count += 1
            yield (coord[0]-count,coord[1])

    @staticmethod
    def right(max_right:int, limit:int, coord:Coord, layout:BoardLayout):
        count=0
        while (coord[0]+count+1) <= max_right and count <= limit and layout[coord[1]][coord[0]+count+1].piece == None:
            count += 1
            yield (coord[0]+count,coord[1])

    @staticmethod
    def compound(maxx:int, maxy:int, limitx:int, limity:int, coord:Coord, genx:Callable, geny:Callable, layout:BoardLayout):
        '''Take the x values from genx and the y values from geny'''
        list1=Movement.to_list(genx(maxx,limitx,coord,layout))
        list2=Movement.to_list(geny(maxy,limity,coord,layout))
        for i in range(min(len(list1),len(list2))):
            yield list1[i][0], list2[i][1]

    @staticmethod
    def orthogonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:Coord, layout:BoardLayout):
        '''Forward, backward, left, right, in that order'''
        for entry in Movement.forward(maxes[0],limits[0],coord,layout):
            yield entry
        for entry in Movement.backward(maxes[1],limits[1],coord,layout):
            yield entry
        for entry in Movement.left(maxes[2],limits[2],coord,layout):
            yield entry
        for entry in Movement.forward(maxes[3],limits[3],coord,layout):
            yield entry

    @staticmethod
    def diagonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:Coord, layout:BoardLayout):
        '''Inputs: top, bottom, left, right\n
        Outputs: top-right, top-left, bottom-left, bottom-right'''
        for entry in Movement.compound(maxes[3],maxes[0],limits[3],limits[0],coord,Movement.right,Movement.forward, layout):
            yield entry
        for entry in Movement.compound(maxes[2],maxes[0],limits[2],limits[0],coord,Movement.left,Movement.forward, layout):
            yield entry
        for entry in Movement.compound(maxes[2],maxes[1],limits[2],limits[1],coord,Movement.left,Movement.backward, layout):
            yield entry
        for entry in Movement.compound(maxes[3],maxes[1],limits[3],limits[1],coord,Movement.right,Movement.backward, layout):
            yield entry

    @staticmethod
    def l_shape():
        pass

    @staticmethod
    def anywhere(layout:BoardLayout):
        height=len(layout)
        width=len(layout[0])
        for y in range(height):
            for x in range(width):
                if layout[y][x].piece == None:
                    yield layout[y][x].boardcoord

'''
To-do:
Check and checkmate checking
Extra move options (for variants like beirut chess, where there is an option to detonate)
init_pos attribute for pieces (for some variants)
Custom positions (loaded in from PNG or FEN)
Specifiable win condition
Manual piece-placing option? (for certain variants)
Manual army choosing? (for some variants)
Pocket-like space (for some variants)

Modes:
Duck chess (the duck)
Fischer random
Atomic chess
Conway chess (every move, pieces are generated based on Conway's Game of Life rules according to the average of the pieces that created it, adding for your colour and subtracting gor the other. These pieces are considere virtual and disappear when the virtual pieces are recalculated.)
Chinese chess
Fairy chess
Different board shapes and sizes
Random capture chess
Occidental standard chess (search it up)
Shogi
Checkers
Fog of war
Undercover queen?
Three-check
King of the Hill
Endgame chess
Los Alamos chess
Pre-chess
Omega chess
Transcendental chess
Dunsany's chess
Peasant's revolt
Really bad chess
Baroque chess
Berolina chess
Chess different armies
2000 AD chess
Kung-fu chess
Pocket mutation chess
Super-X chess
Way of the knight
Etchessera
Cannibal chess
Andernach chess
Circe chess
Benedict chess
Chad
Overpopulation chess
Checkers chess
Prohibition chess
Gravity chess
Einstein chess
Grid chess
Knight relay
Monochromatic chess
Portal chess
Portal-edge chess (only left and right sides)
Racing kings
Beirut chess
Panic chess
Synchronous chess?
Viennese chess
Taikyoku shogi
'''