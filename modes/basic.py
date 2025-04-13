import abc
import copy
from typing import Literal
from pygame import sprite
from collections.abc import Generator, Callable

type Path=str
type Coord=tuple[int,int]
type BoardLayout=list[list[str]]

numbers=["0","1","2","3","4","5","6","7","8","9"]
letters=["","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]

class Piece(sprite.Sprite, abc.ABC):
    def __init__(self, name:str, value:int, colour:Literal["black","white"], image:Path):
        super().__init__()
        self.name=name
        self.value=value
        self.colour=colour
        self.image=image #first value is if white, second is if black

    @abc.abstractmethod
    def display(self):
        pass

    @abc.abstractmethod
    def moves(self):
        pass

    @abc.abstractmethod
    def captures(self):
        pass

    @abc.abstractmethod
    def capture(self):
        pass

    @abc.abstractmethod
    def remove(self):
        pass

class Board():
    def __init__(self, height:int, width:int, layout:list[list[str]]=None, initpos:list[list[str]]=None, piecesdict:dict[str,Piece]=None):
        self.height=height #difference between highest and lowest point
        self.width=width #difference between rightmost and leftmost point
        self.layout=layout #specific tile layout. If None, a square is assumed. Numbers for full spaces, letters for empty ones.
        self.initpos=initpos #a similar format to layout, with numbers indicating piceless squares and letters according to pieceswhite and piecesblack indicating pieces
        self.piecesdict=piecesdict#dictionary containing the pieces that go on the board, and the letters that represent them.

    def construct(self) -> list[list[str]]:
        '''Returns a list of lists representing the full board without intial pieces placed. Spaces with tiles are called "empty". For non-quadrilateral boards, non-tile spaces are called "void".'''
        result=[]
        if self.layout == None:
            for i in range(self.height):
                temp=[]
                for j in range(self.width):
                    temp.append("empty")
                result.append(temp)
        else:
            for row in self.layout:
                temp=[]
                for code in row:
                    if code in numbers:
                        for i in range(int(code)):
                            temp.append("empty")
                    elif code in letters:
                        for i in range(letters.index(code)):
                            temp.append("void")
                    else:
                        raise TypeError(f"Invalid value: {code}")
                result.append(temp)
        return result
    
    def populate(self, full_board:list[list[str]]) -> BoardLayout:
        '''Takes in a constructed board and populates it with pieces.'''
        if self.initpos != None and self.piecesdict != None:
            for i in len(self.initpos):
                cur_pos=0
                for code in self.initpos[i]:
                    if code in numbers:
                        cur_pos += int(code)
                    elif code in self.piecesdict:
                        full_board[i][cur_pos]=copy.copy(self.piecesdict[code])
                        cur_pos += 1
                    else:
                        raise TypeError(f"Invalid value: {code}")
        return full_board
    
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
    def forward(max_height:int,limit:int,coord:Coord, layout:BoardLayout=None):
        count=0
        while (coord[1]+count+1) <= max_height and count <= limit:
            count += 1
            yield (coord[0],coord[1]+count)

    @staticmethod
    def backward(max_depth:int,limit:int,coord:Coord):
        count=0
        while (coord[1]-count-1) >= max_depth and count <= limit:
            count += 1
            yield (coord[0],coord[1]-count)

    @staticmethod
    def left(max_left:int,limit:int,coord:Coord):
        count=0
        while (coord[0]-count-1) >= max_left and count <= limit:
            count += 1
            yield (coord[0]-count,coord[1])

    @staticmethod
    def right(max_right:int,limit:int,coord:Coord):
        count=0
        while (coord[0]+count+1) <= max_right and count <= limit:
            count += 1
            yield (coord[0]+count,coord[1])

    @staticmethod
    def compound(maxx:int,maxy:int,limitx:int,limity:int,coord:Coord,genx:Callable,geny:Callable):
        '''Take the x values from genx and the y values from geny'''
        list1=Movement.to_list(genx(maxx,limitx,coord))
        list2=Movement.to_list(geny(maxy,limity,coord))
        for i in range(min(len(list1),len(list2))):
            yield list1[i][0], list2[i][1]

    @staticmethod
    def orthogonals(maxes:tuple[int,int,int,int],limits:tuple[int,int,int,int],coord:Coord):
        '''Forward, backward, left, right, in that order'''
        for entry in Movement.forward(maxes[0],limits[0],coord):
            yield entry
        for entry in Movement.backward(maxes[1],limits[1],coord):
            yield entry
        for entry in Movement.left(maxes[2],limits[2],coord):
            yield entry
        for entry in Movement.forward(maxes[3],limits[3],coord):
            yield entry

    @staticmethod
    def diagonals(maxes:tuple[int,int,int,int],limits:tuple[int,int,int,int],coord:Coord):
        '''Inputs: top, bottom, left, right\n
        Outputs: top-right, top-left, bottom-left, bottom-right'''
        for entry in Movement.compound(maxes[3],maxes[0],limits[3],limits[0],coord,Movement.right,Movement.forward):
            yield entry
        for entry in Movement.compound(maxes[2],maxes[0],limits[2],limits[0],coord,Movement.left,Movement.forward):
            yield entry
        for entry in Movement.compound(maxes[2],maxes[1],limits[2],limits[1],coord,Movement.left,Movement.backward):
            yield entry
        for entry in Movement.compound(maxes[3],maxes[1],limits[3],limits[1],coord,Movement.right,Movement.backward):
            yield entry

    @staticmethod
    def l_shape():
        pass

    @staticmethod
    def anywhere():
        pass

'''
To-do:
Promotion attribute (pieces it can promote to)
Promotion_pos attribute (positions it can promote in)
Extra move options (for variants like beirut chess, where there is an option to detonate)
Add class for tiles (for variants like portal chess)
init_pos attribute for pieces (for some variants)
Jump parameter (stop iteration if a piece is in the way)
Teleport method (anywhere)
Custom positions (loaded in from PNG or FEN)
Specifiable win condition
Manual piece-placing option? (for certain variants)
Manual army choosing? (for some variants)
Custom board images (can be per tile or wholesale)
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