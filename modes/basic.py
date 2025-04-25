'''Foundation classes and methods for chess modes. Includes:
Piece template, Board template, Tile object, Movement methods, Capture methods, Rules template, OptionBar object, Pocket object, and Info template.'''

from __future__ import annotations
from math import copysign, ceil
from os.path import join
from typing import Literal
from pygame import *
from collections.abc import Generator, Callable, Iterable
import itertools

type Path=str
type Coord=tuple[int,int]
type BoardCoord=tuple[int,int]
type BoardLayout=list[list[Tile]]
type Colour=tuple[int,int,int]

numbers=["0","1","2","3","4","5","6","7","8","9"]
letters=["","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]

display.init()
INFO=display.Info()
WIN_WIDTH=INFO.current_w
WIN_HEIGHT=INFO.current_h-80
screen=display.set_mode((WIN_WIDTH,WIN_HEIGHT))

STD_TILEDIM=(100,100)
PCS_IMG_DIR=join("assets","sprites","pieces")
TIL_IMG_DIR=join("assets","sprites","tiles")
FNT_IMG_DIR=join("assets","montserrat")
POCKET_ANCHORS=([100,1000],[100,100])

SHADES:list[Colour]=[(40,40,40),(55, 55, 55),(92, 92, 92),(131, 131, 131),(177, 177, 177),(233, 233, 233)]
GREENS:list[Colour]=[(69,117,60),(129,182,76),(152,193,91),(160,210,96)]
ORANGE:Colour=(252,175,0)
WHITE:Colour=(255,255,255)
BLACK:Colour=(0,0,0)
#SHADES=[(17,17,17),(51,51,51),(85,85,85),(119,119,119),(153,153,153)]
ROUNDNESS=25
SELECT_COLOUR=ORANGE

INFO_BORDERS=(INFO.current_w/6,5*INFO.current_w/6)
INFO_PAD_LR=10
INFO_PAD_TOP=20
INFO_PAD_BOTTOM=40
INFO_PAD_SPLIT=20
INFO_IMG_DIM=(150,150)
INFO_MINI_DIM=(75,75)
INFO_WIDTH=INFO_BORDERS[1]-INFO_BORDERS[0]
LINK_SPACING=50
font.init()
INFO_TITLE_FONT:font.Font=font.Font(join(FNT_IMG_DIR,"bold++.ttf"),70)
INFO_ALIAS_FONT:font.Font=font.Font(join(FNT_IMG_DIR,"bold+.ttf"),35)
INFO_BODY_FONT:font.Font=font.Font(join(FNT_IMG_DIR,"regular.ttf"),30)

GREEN_TILE=Surface(STD_TILEDIM)
GREEN_TILE.fill((119,148,85))
CREAM_TILE=Surface(STD_TILEDIM)
CREAM_TILE.fill((234,234,208))
EMPTY_TILE=Surface(STD_TILEDIM,SRCALPHA,32)
EMPTY_TILE.fill((0,0,0,0))

class Piece(sprite.Sprite):
    '''A piece. Does not display itself, that's the Tile's job.'''
    def __init__(self, name:str, value:int, colour:Literal[0,1,2], sprite:str, check_target:bool=False, initpos:BoardCoord|None=None):
        '''Attributes common to all pieces'''
        super().__init__()
        self.name=name
        self.value=value
        self.colour=colour
        self.initpos=initpos
        self.image=transform.scale(image.load(sprite),STD_TILEDIM).convert_alpha()
        self.check_target=check_target #whether the piece is a target for check-like conditions
        self.parent:Tile|None=None
        self.promotion:OptionsBar|None=None
        self.promote_pos:list[BoardCoord]|None=None

    def __repr__(self):
        return f"<{self.colour} coloured {self.name} at {self.parent.boardpos}>"

    def __str__(self):
        if self.colour == 0:
            str_name="Black"
        elif self.colour == 1:
            str_name="White"
        elif self.colour == 2:
            str_name="Anyone's"
        else:
            str_name="Colourless"
        return f"{str_name} {self.name}"

    def moves(self, board:Board) -> list[BoardCoord]:
        '''Every square the piece can move to (excluding captures). Most of the time, a few calls to Movement functions are enough.'''
        pass

    def capture_squares(self, board:Board, hypo:bool=False) -> list[BoardCoord]:
        '''Every square the piece can capture on, factoring in the board. If hypo is True, returns every square the piece can capture on hypothetically.'''
        pass

    def move_to(self, final:Tile, board:Board|None=None):
        '''Move to a Tile. Set its parent's piece to None and set the final Tile's piece to this.'''
        self.parent.piece=None
        final.piece=self
        self.parent=final
    
    def lines_of_sight(self, board:Board) -> list[Generator]:
        '''Returns a list of generators, each representing a line of sight of the piece (a way along which the Piece may move and capture at the end of). May be a good idea to have moves() call this and unpack all the generators.'''
        pass

class Tile():
    '''A container for tile information. Is True if there it contains a piece, is False otherwise'''
    def __init__(self, boardcoord:BoardCoord, base:Literal["empty", "void"], rect:Rect, colour:Literal[0,1]|None=None, piece:Piece=None):
        self.boardpos=boardcoord
        self.base=base
        self.piece:Piece|None=piece
        self.image:Surface=None
        self.colour=colour
        self.rect:Rect=rect
        self.move_target:bool=False
        self.capture_target:bool=False
        self.locked:list[bool]=[False,False,False,False] #whether this Tile is locked for certain conditions. Incoming black, outgoing black, incoming white, outgoing white, in that order.
        self.selected=False

    def __repr__(self):
        return f"<Tile at {str(self.boardpos)} containing {self.piece.__repr__()}>"
    
    def __str__(self):
        return f"<Tile at ({str(self.boardpos[0]+1)},{str(self.boardpos[1]+1)}) containing {str(self.piece)}>"
    
    def __bool__(self) -> bool:
        if isinstance(self.piece,Piece):
            return True
        else:
            return False

    def display(self, surface:Surface, mp:Coord, mu:Coord) -> Tile|None:
        '''Display the piece at its position. Returns itself if clicked, or False if deselected. Returns None otherwise.'''
        if isinstance(self.piece, Piece): #show piece
            surface.blit(self.piece.image, (self.rect.x,self.rect.y))
        if self.move_target: #if target for move
            draw.circle(surface,SELECT_COLOUR,self.rect.center,9)
        if self.capture_target or self.rect.collidepoint(mp) or self.selected: #if selected or target for capture
            draw.rect(surface,SELECT_COLOUR,self.rect,5)

        if mu and not self.rect.collidepoint(mp): #if smtg else was clicked
            self.selected=False
        if mu and self.rect.collidepoint(mp) and self.selected: #if clicked again
            self.selected=False
            return False
        if self.rect.collidepoint(mp) and mu and (isinstance(self.piece,Piece) or self.capture_target or self.move_target): #if clicked
            self.selected=True
            return self
        else:
            return None

class Board():
    '''Everything to do with the construction and management of boards.'''
    def __init__(self, height:int, width:int, layout:list[str]=None, tile_dim:int=STD_TILEDIM, initpos:list[str]=None, piecesdict:dict[str,type]=None):
        self.height=height #difference between highest and lowest point
        self.width=width #difference between rightmost and leftmost point
        self.layout:list[list[str]]=layout #specific tile layout. If None, a square is assumed. Numbers for full spaces, letters for empty ones.
        self.initpos=initpos #a similar format to layout, with numbers indicating piceless squares and letters according to piecesdict indicating pieces
        self.piecesdict=piecesdict#dictionary containing the pieces that go on the board, and the letters that represent them.
        self.tile_dim=tile_dim
        self.full_layout:BoardLayout=None #full layout, the one that is used for everything
        self.image:Surface|None=None #what the board looks like
        self.active_options:OptionsBar|None=None #the active set of options, represented by an OptionsBar
        self.anchor:Coord|None=None #the display anchor
        self.blackpocket:Pocket=Pocket(POCKET_ANCHORS[1],STD_TILEDIM)
        self.whitepocket:Pocket=Pocket(POCKET_ANCHORS[0],STD_TILEDIM)
        self.turn:int=0
        self.turn_number:int=0

    def construct(self, anchor:Coord):
        '''Creates a list of lists representing the full board without intial pieces placed. Spaces with tiles are called "empty". For non-quadrilateral boards, non-tile spaces are called "void".'''
        self.anchor=anchor
        result=[]
        count=0
        if self.layout == None:
            for y in range(self.height):
                temp=[]
                for x in range(self.width):
                    temp.append(Tile((x,y),"empty",Rect(anchor[0]+(x*self.tile_dim),anchor[1]+(y*self.tile_dim),self.tile_dim,self.tile_dim)))
                result.append(temp)
        else:
            for i in range(len(self.layout)):
                temp=[]
                x_count=0
                for j in range(len(self.layout[i])):
                    code=self.layout[i][j]
                    if code in numbers:
                        for k in range(int(code)):
                            temp.append(Tile((x_count,i),"empty",Rect(anchor[0]+(x_count*self.tile_dim[0]),anchor[1]+(i*self.tile_dim[1]),self.tile_dim[0],self.tile_dim[1]),1 if count%2 == 0 else 0,))
                            x_count += 1
                            count += 1
                    elif code in letters:
                        for k in range(letters.index(code)):
                            temp.append(Tile((x_count+1,i+1),"void",Rect(anchor[0]+(x_count*self.tile_dim),anchor[1]+(i*self.tile_dim),self.tile_dim,self.tile_dim)))
                            x_count += 1
                            count += 1
                    else:
                        raise TypeError(f"Invalid value: {code}")
                count=i+1
                result.append(temp)
        self.full_layout=result
        self.rect=Rect(anchor[0],anchor[1],self.tile_dim[0]*self.width,self.tile_dim[1]*self.height)
    
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
                        full_board[i][cur_pos].piece=self.piecesdict[code]()
                        full_board[i][cur_pos].piece.parent=full_board[i][cur_pos]
                        full_board[i][cur_pos].piece.initpos=(cur_pos,i)
                        cur_pos += 1
                    else:
                        raise TypeError(f"Invalid value: {code}")
        self.full_layout=full_board
    
    def construct_img(self, light:Surface, dark:Surface, void:Surface, whole:Surface|None=None):
        tile_dim=self.tile_dim[0]
        if whole == None:
            layout=self.full_layout
            height=len(layout)
            width=len(layout[0])
            base=Surface((tile_dim*width,tile_dim*height))
            for y in range(height):
                for x in range(width):
                    target=layout[y][x]
                    if target.base == "void":
                        base.blit(void,(tile_dim*x,tile_dim*y))
                    elif target.base == "empty":
                        if target.colour == 0:
                            base.blit(light,(tile_dim*x,tile_dim*y))
                        elif target.colour == 1:
                            base.blit(dark,(tile_dim*x,tile_dim*y))
            self.image=base.convert_alpha()
        else:
            self.image=whole.convert_alpha()

    def display(self, surface:Surface, mp:Coord, mu:Coord) -> Tile|None:
        '''Display all tiles and option bars. Returns a Tile if one was clicked.'''
        if not isinstance(self.image, Surface):
            raise TypeError("No display image has been set.")
        surface.blit(self.image,self.anchor)
        perm=None
        for row in self.full_layout:
            for tile in row:
                temp=tile.display(surface,mp,mu)
                if temp != None:
                    perm=temp
        if isinstance(self.active_options, OptionsBar):
            self.active_options.display(surface, (self.anchor[0]+self.tile_dim*self.width+10,self.anchor[1]+self.tile_dim*self.height/2-self.active_options.height/2))
        return perm
    
    def scrub(self):
        for row in self.full_layout:
            for tile in row:
                tile.move_target=False
                tile.capture_target=False
                tile.locked=[False,False,False,False]

    def progress_turn(self):
        self.turn_number += 1
        self.turn=self.turn_number%2

    def get(self, coord:BoardCoord|int, coord2:int=None) -> Tile|Literal[False]:
        '''Get a board tile using its board coordinates. Returns False if the Tile deson't.'''
        if isinstance(coord,BoardCoord):
            try:
                return self.full_layout[coord[1]][coord[0]]
            except IndexError:
                return False
        elif isinstance(coord,int) and isinstance(coord2,int):
            try:
                return self.full_layout[coord2][coord]
            except IndexError:
                return False
        else:
            raise TypeError("Cannot access board position based on these arguments.")
    
class Movement():
    @staticmethod
    def out_of_bounds(board:list[list[str]], coord:Coord) -> bool:
        '''Check if a coordinate is outside the bounds of the board'''
        try:
            if board[coord[1]][coord[0]] != "void" and copysign(1,coord[0]) != -1 and copysign(1,coord[1]) != -1:
                return False
            else:
                return True
        except IndexError:
            return True
        except:
            raise
        
    @staticmethod
    def to_list(gen:Iterable) -> list:
        '''Convert a movement generator to a list'''
        return [entry for entry in gen]
    
    @staticmethod
    def line(dir:int, step:int, max:int, limit:int, coord:BoardCoord, board:Board) -> Generator:
        if board.turn != board.full_layout[coord[1]][coord[0]].piece.colour:
            return
        count=0
        max+=copysign(1,step)
        coord=list(coord)
        coord[dir] += step
        while coord[dir] != max and count < limit and board.full_layout[coord[1]][coord[0]].piece == None:
            count+=1
            yield coord
            coord[dir] += step
    
    @staticmethod
    def diagonal(step_x:int, step_y:int, max_x:int, max_y:int, limit:int, coord:BoardCoord, board:Board) -> Generator:
        if board.turn != board.full_layout[coord[1]][coord[0]].piece.colour:
            return
        count=0
        max_x+=int(copysign(1,step_x))
        max_y+=int(copysign(1,step_y))
        next_x=coord[0]+int(copysign(count+1,step_x))
        next_y=coord[1]+int(copysign(count+1,step_y))
        while next_x != max_x and next_y != max_y and count < limit and board.full_layout[next_y][next_x].piece == None:
            count += 1
            yield (next_x,next_y)
            next_x=coord[0]+int(copysign(count+1,step_x))
            next_y=coord[1]+int(copysign(count+1,step_y))
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
    def compound(maxx:int, maxy:int, limitx:int, limity:int, coord:BoardCoord, genx:Callable, geny:Callable, board:Board) -> Generator:
        '''Take the x values from genx and the y values from geny'''
        list1=Movement.to_list(genx(maxx,limitx,coord,board))
        list2=Movement.to_list(geny(maxy,limity,coord,board))
        for i in range(min(len(list1),len(list2))):
            yield list1[i][0], list2[i][1]

    @staticmethod
    def orthogonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:BoardCoord, board:Board) -> Generator:
        '''Forward, backward, left, right, in that order'''
        return itertools.chain(Movement.line(1,-1,maxes[0],limits[0],coord,board),Movement.line(1,1,maxes[1],limits[1],coord,board),Movement.line(0,-1,maxes[2],limits[2],coord,board),Movement.line(0,1,maxes[3],limits[3],coord,board))

    @staticmethod
    def diagonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:BoardCoord, board:Board) -> Generator:
        '''Inputs: top, bottom, left, right\n
        Outputs: top-right, top-left, bottom-left, bottom-right'''
        return itertools.chain(Movement.diagonal(1,-1,maxes[3],maxes[0],limits[0],coord,board),Movement.diagonal(-1,-1,maxes[2],maxes[0],limits[1],coord,board),Movement.diagonal(-1,1,maxes[2],maxes[1],limits[2],coord,board),Movement.diagonal(1,1,maxes[3],maxes[1],limits[3],coord,board))
    
    @staticmethod
    def l_shape(max:tuple[int,int,int,int], limit:int, coord:BoardCoord, board:Board, lenx:int, leny:int) -> Generator:
        '''Maxes are forward, backward, left, right, in that order.'''
        if board.turn != board.full_layout[coord[1]][coord[0]].piece.colour:
            return
        units=[(leny,lenx),(leny,-lenx),(-leny,lenx),(-leny,-lenx),(lenx,leny),(lenx,-leny),(-lenx,leny),(-lenx,-leny)]
        for combo in units:
            for i in range(limit):
                next_val=(coord[0]+combo[0]*i,coord[1]+combo[1]*i)
                if max[2] <= next_val[0] <= max[3] and max[0] <= next_val[1] <= max[1] and board.full_layout[next_val[0]][next_val[1]].piece == None:
                    yield next_val

    @staticmethod
    def anywhere(board:Board, coord:BoardCoord):
        if board.turn != board.full_layout[coord[1]][coord[0]].piece.colour:
            return
        height=len(board.full_layout)
        width=len(board.full_layout[0])
        for y in range(height):
            for x in range(width):
                if board.full_layout[y][x].piece == None:
                    yield board.full_layout[y][x].boardpos

class Capture():
    @staticmethod
    def line(dir:int, step:int, max:int, limit:int, coord:BoardCoord, board:Board, col:int, hypo:bool=False) -> Generator:
        if board.turn != board.full_layout[coord[1]][coord[0]].piece.colour:
            return
        count=0
        max+=copysign(1,step)
        coord=list(coord)
        coord[dir] += step
        while coord[dir] != max and count < limit:
            count+=1
            if (board.full_layout[coord[1]][coord[0]].piece != None and board.full_layout[coord[1]][coord[0]].piece.colour != col) or hypo:
                yield coord
                return
            elif board.full_layout[coord[1]][coord[0]].piece != None and board.full_layout[coord[1]][coord[0]].piece.colour == col:
                return
            coord[dir] += step
    
    @staticmethod
    def diagonal(step_x:int, step_y:int, max_x:int, max_y:int, limit:int, coord:BoardCoord, board:Board, col:int, hypo:bool=False) -> Generator:
        if board.turn != board.full_layout[coord[1]][coord[0]].piece.colour:
            return
        count=0
        max_x+=int(copysign(1,step_x))
        max_y+=int(copysign(1,step_y))
        next_x=coord[0]+int(copysign(count+1,step_x))
        next_y=coord[1]+int(copysign(count+1,step_y))
        while next_x != max_x and next_y != max_y and count < limit:
            count += 1
            if (board.full_layout[next_y][next_x].piece != None and board.full_layout[next_y][next_x].piece.colour != col) or hypo:
                yield (next_x,next_y)
                return
            elif board.full_layout[next_y][next_x].piece != None and board.full_layout[next_y][next_x].piece.colour == col:
                return
            next_x=coord[0]+int(copysign(count+1,step_x))
            next_y=coord[1]+int(copysign(count+1,step_y))

    @staticmethod
    def compound(maxx:int, maxy:int, limitx:int, limity:int, coord:BoardCoord, genx:Callable, geny:Callable, board:Board, col:int, hypo:bool=False) -> Generator:
        '''Take the x values from genx and the y values from geny'''
        list1=Movement.to_list(genx(maxx,limitx,coord,board,col,hypo))
        list2=Movement.to_list(geny(maxy,limity,coord,board,col,hypo))
        for i in range(min(len(list1),len(list2))):
            yield list1[i][0], list2[i][1]

    @staticmethod
    def orthogonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:BoardCoord, board:Board, col:int, hypo:bool=False) -> Generator:
        '''Forward, backward, left, right, in that order'''
        return itertools.chain(Capture.line(1,-1,maxes[0],limits[0],coord,board,col,hypo),Capture.line(1,1,maxes[1],limits[1],coord,board,col,hypo),Capture.line(0,-1,maxes[2],limits[2],coord,board,col,hypo),Capture.line(0,1,maxes[3],limits[3],coord,board,col,hypo))

    @staticmethod
    def diagonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:BoardCoord, board:Board, col:int, hypo:bool=False) -> Generator:
        '''Inputs: top, bottom, left, right\n
        Outputs: top-right, top-left, bottom-left, bottom-right'''
        return itertools.chain(Capture.diagonal(1,-1,maxes[3],maxes[0],limits[0],coord,board,col,hypo),Capture.diagonal(-1,-1,maxes[2],maxes[0],limits[1],coord,board,col,hypo),Capture.diagonal(-1,1,maxes[2],maxes[1],limits[2],coord,board,col,hypo),Capture.diagonal(1,1,maxes[3],maxes[1],limits[3],coord,board,col,hypo))
    
    @staticmethod
    def l_shape(max:tuple[int,int,int,int], limit:int, coord:BoardCoord, board:Board, lenx:int, leny:int, col:int, hypo:bool=False) -> Generator:
        '''Maxes are forward, backward, left, right, in that order.'''
        if board.turn != board.full_layout[coord[1]][coord[0]].piece.colour:
            return
        units=[(leny,lenx),(leny,-lenx),(-leny,lenx),(-leny,-lenx),(lenx,leny),(lenx,-leny),(-lenx,leny),(-lenx,-leny)]
        for combo in units:
            for i in range(limit):
                next_val=(coord[0]+combo[0]*i,coord[1]+combo[1]*i)
                if max[2] <= next_val[0] <= max[3] and max[0] <= next_val[1] <= max[1] and ((board.full_layout[next_val[0]][next_val[1]].piece != None and board.full_layout[next_val[0]][next_val[1]].piece.colour != col) or hypo):
                    yield next_val

    @staticmethod
    def anywhere(board:Board, col:int, coord:BoardCoord, hypo:bool=False):
        if board.turn != board.full_layout[coord[1]][coord[0]].piece.colour:
            return
        height=len(board.full_layout)
        width=len(board.full_layout[0])
        for y in range(height):
            for x in range(width):
                if board.full_layout[y][x].piece != None and board.full_layout[y][x].piece.colour != col:
                    yield board.full_layout[y][x].boardpos

class Rules():
    '''Gamerules that can be altered. Includes win conditions and check-like conditions'''
    @staticmethod
    def win(board:Board, yourpieces:list[Piece], enemypieces:list[Piece], target:Piece) -> tuple[bool,str]:
        '''A generalisation of checkmate. Returns whether or not a win has occurred, and which side has won. Is checkmate by default. pieces is a list of movable Pieces.'''
        '''By default, calls lock() on the current board, then checks for '''
        info=Rules.lock(board, enemypieces, target, True)
        colour=enemypieces[0].colour
        if info != None:
            squares_to_occlude=info[1]
            possible_moves=info[2]
            if possible_moves != []:
                return False, colour
            else:
                for piece in yourpieces:
                    possible_moves.extend(piece.capture_squares(board, True))
                for square in possible_moves:
                    if square not in squares_to_occlude:
                        possible_moves.remove(square)

        if possible_moves == []:
            return True, colour
        else:
            return False, colour

    @staticmethod
    def lock(board:Board, enemypieces:list[Piece], target:Piece, returnall:bool=False) -> list[BoardCoord]|None|list[list[BoardCoord]]:
        '''A generalisation of checks. Returns a list of board positions to lock down. Is check by default. This function is quite intensive (I think), so only call it when it is absolutely needed.'''
        '''Entering check:
        The King is in check if any piece can capture it. This is detected by calling Piece.capture_squares() on every piece and seeing if the King is in one of them. Alternatively, a virtual copy of every piece could be instantiated on the King's position, then their moves detected. If a piece can capture the same type of piece (assuming move and capture symmetry), the King is in check. This is faster but mentally costlier. It is also less general, not applying in variants where moves and captures are not symmetrical across positions and/or colours. The first solution will be implemented.'''
        '''Squares that can be moved to during check:
        Check is exited if the King moves into an un-attacked square, if the attacking piece is blocked, or if the attaking piece is captured. Thus, the squares that can be moved to are the safe moves for the checked piece, line-of-sight squares of all the attacking pieces, and the attacking piece itself.'''

        check=False #whether the target is in check
        possible_moves=target.moves(board.full_layout) #the target's possible moves when not checked
        attacking_pieces:list[Piece]=[] #the pieces attacking the target
        not_locked=[] #board spaces that are not locked

        for piece in enemypieces: #check if the target is in check and which pieces are checking it
            for square in piece.capture_squares(board.full_layout):
                if board.full_layout[square[1]][square[0]].piece == target:
                    check=True
                    attacking_pieces.append(piece)
     
        if not check:
            return None
        else:
            attacked_squares=[] #unsafe squares for the target
            for piece in enemypieces:
                attacked_squares.extend(piece.capture_squares(board.full_layout,True))
            for square in attacked_squares:
                if square in possible_moves:
                    possible_moves.remove(square)
            not_locked.extend(possible_moves) #squares that are not under attack that the target can move to are not locked

            if len(attacking_pieces) == 1:
                not_locked.append(attacking_pieces[0].parent.boardpos) #if only one piece is attacking, it can be captured to end the check.

            occlude=[] #squares that can occlude the check if one of your pieces were there
            attacking_lines=[] #the generators that generate potentially occludable squares
            for piece in attacking_pieces:
                for line in piece.lines_of_sight(board.full_layout):
                    for square in line:
                        if board.full_layout[square[1]][square[0]].piece == target:
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

            all_squares=[square for square in [row for row in board.full_layout]]
            if not returnall:
                return [square for square in all_squares if square not in not_locked]
            else:
                return ([square for square in all_squares if square not in not_locked], occlude, possible_moves)
            
    @staticmethod
    def interpret():
        pass

class OptionsBar():
    def __init__(self, parent:object, contains:list[Tile], clickfunc:Callable, board_for:Board):
        self.parent=parent
        self.contains=contains
        self.on_click:Callable=clickfunc #takes in the tile that that called it and the option that was called.
        self.height:int=0
        for tile in self.contains:
            self.height += tile.rect.height
        for i in range(len(self.contains)):
            self.contains[i].rect.x=board_for.anchor[0]+board_for.tile_dim[0]+10
            self.contains[i].rect.y=board_for.anchor[1]+board_for.tile_dim[1]*board_for.height/2-self.height/2+STD_TILEDIM*i

    def display(self, surface):
        for tile in self.contains:
            tile.display(surface)

class Pocket():
    def __init__(self, anchor:Coord, tile_size:int, inittiles:list[Tile]=None):
        self.contains:list[Tile]=inittiles
        self.anchor:Coord=anchor
        self.tile_size=tile_size
        self.height=tile_size
        self.width=0

    def display(self, surface:Surface):
        for tile in self.contains:
            tile.display(surface)

    def add(self, piece:Piece):
        self.contains.append(Tile(None,"empty",Rect((self.anchor[0]+self.tile_size*len(self.contains),self.anchor[1]),(self.tile_size,self.tile_size))))
        self.contains[-1].piece=piece
        piece.parent=self.contains[-1]
        self.width += self.tile_size

def wrap_text(text:str, max:int, font:font.Font) -> list[str]:
    words=text.split(" ")
    lines=[]
    temp=""
    for word in words:
        if font.size(temp+" "+word)[0] <= max:
            temp += " "+word
        elif temp == "":
            lines.append(" "+word)
        else:
            lines.append(temp)
            temp=" "+word
        if words.index(word)+1 == len(words):
            lines.append(temp)
    return [line[1:] for line in lines]

class Info():
    def __init__(self, name:str, abstract:str, info:str, img:str, img_bg:str|Surface, covers:Literal["mode","piece"], links:list[Info]=None):
        self.name=name
        self.abstract=abstract
        self.body=info
        self.covers=covers
        if isinstance(img_bg, str):
            self.image:Surface=transform.scale(image.load(img_bg),INFO_IMG_DIM).convert_alpha()
        else:
            self.image:Surface=transform.scale(img_bg,INFO_IMG_DIM).convert_alpha()
        self.image.blit(transform.scale(image.load(img),INFO_IMG_DIM).convert_alpha(),(0,0))
        self.links=links
        self.scroll_offset=0
        self.scrollable=False

    def set_links(self, links:list[Info]):
        self.links=links

    def construct(self):
        components:dict[str,Surface]={}
        components["image"]=self.image
        wrapped_title=wrap_text(self.name,INFO_WIDTH-INFO_IMG_DIM[0]-2*INFO_PAD_LR-INFO_PAD_SPLIT,INFO_TITLE_FONT)
        components["title"]=Surface((INFO_WIDTH-INFO_IMG_DIM[0]-2*INFO_PAD_LR-INFO_PAD_SPLIT,len(wrapped_title)*INFO_TITLE_FONT.get_height()),SRCALPHA,32)
        for i in range(len(wrapped_title)):
            components["title"].blit(INFO_TITLE_FONT.render(wrapped_title[i],True,WHITE),(0,INFO_TITLE_FONT.get_height()*i))
        wrapped_abstract=wrap_text(self.abstract,INFO_WIDTH-2*INFO_PAD_LR,INFO_ALIAS_FONT)
        components["abstract"]=Surface((INFO_WIDTH-2*INFO_PAD_LR,len(wrapped_abstract)*INFO_ALIAS_FONT.get_height()),SRCALPHA,32)
        for i in range(len(wrapped_abstract)):
            components["abstract"].blit(INFO_ALIAS_FONT.render(wrapped_abstract[i],True,WHITE),(0,INFO_ALIAS_FONT.get_height()*i))
        components["top bg"]=Surface((INFO_WIDTH,INFO_PAD_TOP+max(INFO_IMG_DIM[1],components["title"].get_height())+INFO_PAD_SPLIT+components["abstract"].get_height()+INFO_PAD_BOTTOM),SRCALPHA,32)
        components["top bg"].fill(SHADES[1])
        draw.rect(components["top bg"],SHADES[2],components["top bg"].get_rect(),border_radius=ROUNDNESS)
        wrapped_body=wrap_text(self.body,INFO_WIDTH-2*INFO_PAD_LR,INFO_BODY_FONT)
        components["body"]=Surface((INFO_WIDTH-2*INFO_PAD_LR,len(wrapped_body)*INFO_BODY_FONT.get_height()),SRCALPHA,32)
        for i in range(len(wrapped_body)):
            components["body"].blit(INFO_BODY_FONT.render(wrapped_body[i],True,WHITE),(0,INFO_BODY_FONT.get_height()*i))
        if self.covers == "mode":
            components["qualifier"]=INFO_BODY_FONT.render("Contains:",True,WHITE)
        else:
            components["qualifier"]=INFO_BODY_FONT.render("Is included in:",True,WHITE)
        components["link rows"]=[]
        for i in range(ceil(len(self.links)/8)):
            num_in_row=min(8,len(self.links)-8*i)
            max_text_height=0
            for j in range(num_in_row):
                max_text_height=max(max_text_height,len(wrap_text(self.links[8*i+j].name,INFO_MINI_DIM[0],INFO_BODY_FONT))*INFO_BODY_FONT.get_height())
            row_surface=Surface((INFO_WIDTH-2*INFO_PAD_LR,INFO_MINI_DIM[1]+max_text_height))
            row_surface.fill(SHADES[1])
            for j in range(num_in_row):
                row_surface.blit(transform.scale(self.links[8*i+j].image,INFO_MINI_DIM),((INFO_MINI_DIM[0]+LINK_SPACING)*j,0))
                wrapped_name=wrap_text(self.links[8*i+j].name,INFO_MINI_DIM[0],INFO_BODY_FONT)
                for k in range(len(wrapped_name)):
                    row_surface.blit(INFO_BODY_FONT.render(wrapped_name[k],True,WHITE),((INFO_MINI_DIM[0]+LINK_SPACING)*j,INFO_MINI_DIM[1]+INFO_BODY_FONT.get_height()*k))
            components["link rows"].append(row_surface)
        self.display_base=Surface((INFO_WIDTH,components["top bg"].get_height()+INFO_PAD_BOTTOM+components["body"].get_height()+2*INFO_PAD_SPLIT+components["qualifier"].get_height()+sum([row.get_height() for row in components["link rows"]])+INFO_PAD_SPLIT*len(components["link rows"])+INFO_PAD_BOTTOM),SRCALPHA,32)
        self.display_base.fill(SHADES[1])
        self.display_base.blit(components["top bg"],(0,0))
        if components["title"].get_height() <= INFO_IMG_DIM[1]:
            self.display_base.blit(self.image,(INFO_PAD_LR,INFO_PAD_TOP))
            self.display_base.blit(components["title"],(INFO_PAD_LR+INFO_IMG_DIM[0]+INFO_PAD_SPLIT,INFO_PAD_TOP+INFO_IMG_DIM[1]/2-components["title"].get_height()/2))
        else:
            self.display_base.blit(components["title"],(INFO_PAD_LR+INFO_IMG_DIM[0]+INFO_PAD_SPLIT,INFO_PAD_TOP))
            self.display_base.blit(self.image,(INFO_PAD_LR,INFO_PAD_TOP+components["title"].get_height()/2-INFO_IMG_DIM[1]/2))
        self.display_base.blit(components["abstract"],(INFO_PAD_LR,INFO_PAD_TOP+max(INFO_IMG_DIM[1],components["title"].get_height())+INFO_PAD_SPLIT))
        body_y_anchor=components["top bg"].get_height()+INFO_PAD_SPLIT
        self.display_base.blit(components["body"],(INFO_PAD_LR,body_y_anchor))
        body_y_anchor += components["body"].get_height()+INFO_PAD_SPLIT
        self.display_base.blit(components["qualifier"],(INFO_PAD_LR,body_y_anchor))
        body_y_anchor += components["qualifier"].get_height()+INFO_PAD_SPLIT
        for i in range(len(components["link rows"])):
            self.display_base.blit(components["link rows"][i],(INFO_PAD_LR,body_y_anchor))
            body_y_anchor += components["link rows"][i].get_height()+INFO_PAD_SPLIT

    def display(self, surface:Surface):
        surface.blit(self.display_base, (INFO_BORDERS[0],-self.scroll_offset))

print('Module "basic" (game foundations) loaded.')