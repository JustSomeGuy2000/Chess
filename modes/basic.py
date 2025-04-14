from __future__ import annotations
import abc
import copy
from math import copysign
from typing import Literal
from pygame import sprite, Surface, Rect, draw
from collections.abc import Generator, Callable, Iterable

type Path=str
type Coord=tuple[int,int]
type BoardCoord=tuple[int,int]
type BoardLayout=list[list[Tile]]

numbers=["0","1","2","3","4","5","6","7","8","9"]
letters=["","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]

class Piece(sprite.Sprite, abc.ABC):
    '''A piece. Does not display itself, that's the Tile's job.'''
    def __init__(self, name:str, value:int, colour:Literal["black","white","any"], initpos:BoardCoord, imagewhite:Surface, check_target:bool, imageblack:Surface|None=None):
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
        self.check_target=check_target #whether the piece is a target for check-like conditions
        self.parent:Tile|None=None
        self.promotes_to:list[Piece]|None=None
        self.promote_pos:list[BoardCoord]|None=None

    @abc.abstractmethod
    def moves(self, layout:BoardLayout) -> list[BoardCoord]:
        '''Every square the piece can move to (excluding captures). Most of the time, a few calls to Movement functions are enough.'''
        pass

    @abc.abstractmethod
    def capture_squares(self, layout:BoardLayout, hypo:bool=False) -> list[BoardCoord]:
        '''Every square the piece can capture on, factoring in the board. If hypo is True, returns every square the piece can capture on hypothetically.'''
        pass

    @abc.abstractmethod
    def move_to(self, final:Tile, board:Board|None=None) -> Piece:
        '''Move to a Tile. What really happens is that it removes itself from the previous Tile and returns what should be in the Tile it moves to. Actually setting the Tile's piece to that is handled by the game.'''
        pass
    
    @abc.abstractmethod
    def lines_of_sight(self, layout:BoardLayout) -> list[Generator]:
        '''Returns a list of generators, each representing a line of sight of the piece. May be a good idea to have moves() call this and unpack all the generators.'''
        pass

class Tile():
    '''A container for tile information'''
    def __init__(self, boardcoord:BoardCoord, base:Literal["empty", "void"], colour:Literal["dark","light"]|None=None):
        self.boardpos=boardcoord
        self.base=base
        self.pos:Coord=None
        self.piece:Piece|None=None
        self.image:Surface=None
        self.colour=colour
        self.rect:Rect=None
        self.move_target:bool=False
        self.capture_target:bool=False
        self.locked:list[bool]=[False,False,False,False] #whether this Tile is locked for certain conditions. Incominblack, outgoing black, incoming white, outgoing white, in that order.

    def display(self, surface:Surface):
        surface.blit(self.piece.image, self.pos)

class Board():
    '''Everything to do with the construction and management of boards.'''
    def __init__(self, height:int, width:int, layout:list[list[str]]=None, initpos:list[list[str]]=None, piecesdict:dict[str,Piece]=None):
        self.height=height #difference between highest and lowest point
        self.width=width #difference between rightmost and leftmost point
        self.layout:list[list[str]]=layout #specific tile layout. If None, a square is assumed. Numbers for full spaces, letters for empty ones.
        self.initpos=initpos #a similar format to layout, with numbers indicating piceless squares and letters according to piecesdict indicating pieces
        self.piecesdict=piecesdict#dictionary containing the pieces that go on the board, and the letters that represent them.
        self.full_layout:BoardLayout=None #full layout, the one that is used for everything
        self.image:Surface|None=None #what the board looks like

    def construct(self):
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
                for j in range(len(self.layout[i])):
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
        self.full_layout=result
    
    def populate(self):
        full_board=self.full_layout
        '''Takes in a constructed board and populates it with pieces.'''
        if self.initpos != None and self.piecesdict != None:
            for i in range(len(self.initpos)):
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
                    target.rect=Rect(anchor[0]+(target.boardpos[0]*rect_size[0]),anchor[1]+(target.boardpos[1]*rect_size[1]))
    
class Movement():
    @staticmethod
    def out_of_bounds(board:list[list[str]], coord:Coord) -> bool:
        '''Check if a coordinate is outside the bounds of the board'''
        if board[coord[1]][coord[0]] != "void":
            return False
        else:
            return True
        
    @staticmethod
    def to_list(gen:Iterable) -> list:
        '''Convert a movement generator to a list'''
        return [entry for entry in gen]
    
    @staticmethod
    def forward(max_height:int, limit:int, coord:Coord, layout:BoardLayout) -> Generator:
        count=0
        while (coord[1]+count+1) <= max_height and count <= limit and layout[coord[1]+count+1][coord[0]].piece == None:
            count += 1
            yield (coord[0],coord[1]+count)
        return

    @staticmethod
    def backward(max_depth:int, limit:int, coord:Coord, layout:BoardLayout) -> Generator:
        count=0
        while (coord[1]-count-1) >= max_depth and count <= limit and layout[coord[1]-count-1][coord[0]].piece == None:
            count += 1
            yield (coord[0],coord[1]-count)
        return

    @staticmethod
    def left(max_left:int, limit:int, coord:Coord, layout:BoardLayout) -> Generator:
        count=0
        while (coord[0]-count-1) >= max_left and count <= limit and layout[coord[1]][coord[0]-count-1].piece == None:
            count += 1
            yield (coord[0]-count,coord[1])
        return

    @staticmethod
    def right(max_right:int, limit:int, coord:Coord, layout:BoardLayout) -> Generator:
        count=0
        while (coord[0]+count+1) <= max_right and count <= limit and layout[coord[1]][coord[0]+count+1].piece == None:
            count += 1
            yield (coord[0]+count,coord[1])
        return
    
    @staticmethod
    def skip_entries(limit:int, jump_value:int, original:Iterable) -> Generator:
        '''Yields every nth entry, where n is jump_value'''
        count=1
        for coord in original:
            if (count % jump_value) == 0 and count != (limit+1):
                yield coord
            count+=1
        return

    @staticmethod
    def compound(maxx:int, maxy:int, limitx:int, limity:int, coord:Coord, genx:Callable, geny:Callable, layout:BoardLayout) -> Generator:
        '''Take the x values from genx and the y values from geny'''
        list1=Movement.to_list(genx(maxx,limitx,coord,layout))
        list2=Movement.to_list(geny(maxy,limity,coord,layout))
        for i in range(min(len(list1),len(list2))):
            yield list1[i][0], list2[i][1]

    @staticmethod
    def orthogonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:Coord, layout:BoardLayout) -> Generator:
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
    def diagonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:Coord, layout:BoardLayout) -> Generator:
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
    def l_shape(max:tuple[int,int,int,int], limit:int, coord:Coord, layout:BoardLayout, lenx:int, leny:int) -> Generator:
        '''Maxes are forward, backward, left, right, in that order.
        Yields values counter-clockwise from forward.'''
        count=0
        top_bottom=1 #1 is top, -1 is bottom
        left_right=-1 #1 is right, -1 is left
        first_len=0 #0 is y, 1 is x
        len_list=[leny,lenx]
        next_value=(coord[0]+copysign(len_list[first_len],left_right),coord[1]+copysign(len_list[0 if first_len == 1 else 1],top_bottom))
        while count != limit and max[2] <= next_value[0] <= max[3] and max[1] <= next_value[1] <= max[0] and layout[next_value[1]][next_value[0]].piece == None:
            yield next_value
            count += 1
            top_bottom *= -1
            left_right *= -1
            first_len=(first_len+1)%2
            next_value=(coord[0]+copysign(len_list[first_len],left_right),coord[1]+copysign(len_list[0 if first_len == 1 else 1],top_bottom))
        return

    @staticmethod
    def anywhere(layout:BoardLayout):
        height=len(layout)
        width=len(layout[0])
        for y in range(height):
            for x in range(width):
                if layout[y][x].piece == None:
                    yield layout[y][x].boardpos

class Rules():
    '''Gamerules that can be altered. Includes win conditions and check-like conditions'''
    @staticmethod
    def win(layout:BoardLayout, pieces:list[Piece]) -> bool|tuple[bool,str]:
        '''A generalisation of checkmate. Returns whether or not a win has occurred, and which side has won. Is checkmate by default. pieces is a list of movable Pieces.'''
        '''By default, calls lock() on the current board, then checks for '''
        return

    @staticmethod
    def lock(layout:BoardLayout, enemypieces:list[Piece], target:Piece) -> list[BoardCoord]|None:
        '''A generalisation of checks. Returns a list of board positions to lock down. Is check by default. This function is quite intensive (I think), so only call it when it is absolutely needed.'''
        '''Entering check:
        The King is in check if any piece can capture it. This is detected by calling Piece.capture_squares() on every piece and seeing if the King is in one of them. Alternatively, a virtual copy of every piece could be instantiated on the King's position, then their moves detected. If a piece can capture the same type of piece (assuming move and capture symmetry), the King is in check. This is faster but mentally costlier. It is also less general, not applying in variants where moves and captures are not symmetrical across positions and/or colours. The first solution will be implemented.'''
        '''Squares that can be moved to during check:
        Check is exited if the King moves into an un-attacked square, if the attacking piece is blocked, or if the attaking piece is captured. Thus, the squares that can be moved to are the safe moves for the checked piece, line-of-sight squares of all the attacking pieces, and the attacking piece itself.'''

        check=False #whether the target is in check
        possible_moves=target.moves(layout) #the target's possible moves when not checked
        attacking_pieces:list[Piece]=[] #the pieces attacking the target
        not_locked=[] #board spaces that are not locked

        for piece in enemypieces: #check if the target is in check and which pieces are checking it
            for square in piece.capture_squares(layout):
                if layout[square[1]][square[0]].piece == target:
                    check=True
                    attacking_pieces.append(piece)
     
        if not check:
            return None
        else:
            attacked_squares=[] #unsafe squares for the target
            for piece in enemypieces:
                attacked_squares.extend(piece.capture_squares(layout,True))
            for square in attacked_squares:
                if square in possible_moves:
                    possible_moves.remove(square)
            not_locked.extend(possible_moves) #the target can move to squares that are not under attack are not locked

            if len(attacking_pieces) == 1:
                not_locked.append(attacking_pieces[0].parent.boardpos) #if only one piece is attacking, it can be captured to end the check.

            occlude=[] #squares that can occlude the check if one of your pieces were there
            attacking_lines=[] #the generators that generate potentially occludable squares
            for piece in attacking_pieces:
                for line in piece.lines_of_sight(layout):
                    for square in line:
                        if layout[square[1]][square[0]].piece == target:
                            attacking_lines.append(line) #collect all the generators
                            break
            for line in attacking_lines:
                temp_occlude:list[list[BoardCoord]]=[]
                temp_occlude.append(Movement.to_list(line))
            for line in temp_occlude:
                for square in line:
                    if all([square in line for line in temp_occlude]):
                        occlude.append(square) #only squares all checking pieces must cross can remove the check if occluded
            not_locked.extend(occlude)

            all_squares=[square for square in [row for row in layout]]
            return [square for square in all_squares if square not in not_locked]

class OptionsBar():
    def __init__(self, parent:object, contains:list[Tile], anchor:Coord):
        self.parent=parent
        self.contains=contains
        self.anchor=anchor

    def display(self, surface):
        for tile in self.contains:
            draw.rect(surface, (255,255,255), Rect(self.contains[0].rect.x-5,self.contains[0].rect.y-5,self.contains[0].rect.width+10, self.contains[0].rect.height+10))
            tile.display(surface)

class Pocket():
    def __init__(self, anchor_black, anchor_white, tile_size:int):
        self.contains_white:list[Tile]=None
        self.contains_black:list[Tile]=None
        self.anchor_black:Coord=anchor_black
        self.anchor_white:Coord=anchor_white
        self.tile_size=tile_size

    def display(self, surface:Surface):
        for piece in self.contains_white+self.contains_black:
            piece.display(surface)

    def on_click(self):
        pass

    def add(self, piece:Piece):
        if piece.colour == "black":
            self.contains_black.append(Tile(None,"empty","dark"))
            self.contains_black[-1].rect=Rect(self.anchor_black[0], self.anchor_black[1]+self.tile_size*(len(self.contains_black)-1),self.tile_size,self.tile_size)
            self.contains_black[-1].piece=piece
        else:
            self.contains_white.append(Tile(None,"empty","dark"))
            self.contains_white[-1].rect=Rect(self.anchor_white[0], self.anchor_white[1]-self.tile_size*(len(self.contains_black)-1),self.tile_size,self.tile_size)
            self.contains_white[-1].piece=piece

print("")
'''
To-do:
URGENT: Figure out how Pocket and OptionsBar are supposed to work
Checkmate checking
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