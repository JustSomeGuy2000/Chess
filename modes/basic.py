from __future__ import annotations
from math import copysign, ceil
from os.path import join
from typing import Literal
from pygame import *
from collections.abc import Generator, Callable, Iterable

type Path=str
type Coord=tuple[int,int]
type BoardCoord=tuple[int,int]
type BoardLayout=list[list[Tile]]

numbers=["0","1","2","3","4","5","6","7","8","9"]
letters=["","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]

INFO=display.Info()

STD_TILEDIM=(100,100)
PCS_IMG_DIR=join("assets","sprites","pieces")
POCKET_ANCHORS=([100,1000],[100,100])
SELECT_COLOUR=(150,190,0)
SHADES=[(55, 55, 55),(92, 92, 92),(131, 131, 131),(177, 177, 177),(233, 233, 233)]
#SHADES=[(17,17,17),(51,51,51),(85,85,85),(119,119,119),(153,153,153)]
ROUNDNESS=25

INFO_BORDERS=(INFO.current_w/6,5*INFO.current_w/6)
INFO_PADDING=(10,20,40,20) #left-right, top, bottom, split
INFO_IMG_DIM=(200,200)
INFO_MINI_DIM=(200,200)
LINK_SPACING=50
INFO_TITLE_FONT:font.Font=None #replace
INFO_ALIAS_FONT:font.Font=None #replace
INFO_BODY_FONT:font.Font=None #replace

GREEN_TILE=Surface(STD_TILEDIM).fill((119,148,85))
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
        self.image=transform.scale(image.load(join(PCS_IMG_DIR,sprite)),STD_TILEDIM)
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
    
    def lines_of_sight(self, board:Board) -> list[Generator]:
        '''Returns a list of generators, each representing a line of sight of the piece (a way along which the Piece may move and capture at the end of). May be a good idea to have moves() call this and unpack all the generators.'''
        pass

class Tile():
    '''A container for tile information'''
    def __init__(self, boardcoord:BoardCoord, base:Literal["empty", "void"], rect:Rect, colour:Literal[0,1]|None=None, piece:Piece=None):
        self.boardpos=boardcoord
        self.base=base
        self.piece:Piece|None=piece
        self.image:Surface=None
        self.colour=colour
        self.rect:Rect=rect
        self.move_target:bool=False
        self.capture_target:bool=False
        self.locked:list[bool]=[False,False,False,False] #whether this Tile is locked for certain conditions. Incominblack, outgoing black, incoming white, outgoing white, in that order.

    def __repr__(self):
        return f"<Tile at {str(self.boardpos)} containing {self.piece.__repr__()}>"
    
    def __str__(self):
        return f"<Tile at ({str(self.boardpos[0]+1)},{str(self.boardpos[1]+1)}) containing {str(self.piece)}>"

    def display(self, surface:Surface):
        surface.blit(self.piece.image, (self.rect.x,self.rect.y))
        if self.move_target:
            draw.circle(surface,SELECT_COLOUR,self.rect.center,3)
        if self.capture_target:
            draw.rect(surface,SELECT_COLOUR,self.rect,5)

class Board():
    '''Everything to do with the construction and management of boards.'''
    def __init__(self, height:int, width:int, layout:list[list[str]]=None, tile_dim:int=STD_TILEDIM, initpos:list[list[str]]=None, piecesdict:dict[str,type]=None):
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
                            temp.append(Tile((x_count+1,i+1),"empty",1 if count%2 == 0 else 0,Rect(anchor[0]+(x_count*self.tile_dim),anchor[1]+(i*self.tile_dim),self.tile_dim,self.tile_dim)))
                            x_count += 1
                            count += 1
                    elif code in letters:
                        for k in range(letters.index(code)):
                            temp.append(Tile((x_count+1,i+1),"void",Rect(anchor[0]+(x_count*self.tile_dim),anchor[1]+(i*self.tile_dim),self.tile_dim,self.tile_dim)))
                            x_count += 1
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
                        full_board[i][cur_pos].piece=self.piecesdict[code]()
                        full_board[i][cur_pos].piece.parent=full_board[i][cur_pos]
                        full_board[i][cur_pos].piece.initpos=(cur_pos,i)
                        cur_pos += 1
                    else:
                        raise TypeError(f"Invalid value: {code}")
        self.full_layout=full_board
    
    def construct_img(self, light:Surface, dark:Surface, void:Surface, whole:Surface|None=None) -> Surface:
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
            self.image=base
        else:
            self.image=whole

    def display(self, surface:Surface):
        if not isinstance(self.image, Surface):
            raise TypeError("No display image has been set.")
        surface.blit(self.image,self.anchor)
        for row in self.full_layout:
            for tile in row:
                tile.display(surface)
        if isinstance(self.active_options, OptionsBar):
            self.active_options.display(surface, (self.anchor[0]+self.tile_dim*self.width+10,self.anchor[1]+self.tile_dim*self.height/2-self.active_options.height/2))
    
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
    def forward(max_height:int, limit:int, coord:BoardCoord, board:Board) -> Generator:
        count=0
        while (coord[1]+count+1) <= max_height and count <= limit and board.full_layout[coord[1]+count+1][coord[0]].piece == None:
            count += 1
            yield (coord[0],coord[1]+count)
        return

    @staticmethod
    def backward(max_depth:int, limit:int, coord:BoardCoord, board:Board) -> Generator:
        count=0
        while (coord[1]-count-1) >= max_depth and count <= limit and board.full_layout[coord[1]-count-1][coord[0]].piece == None:
            count += 1
            yield (coord[0],coord[1]-count)
        return

    @staticmethod
    def left(max_left:int, limit:int, coord:BoardCoord, board:Board) -> Generator:
        count=0
        while (coord[0]-count-1) >= max_left and count <= limit and board.full_layout[coord[1]][coord[0]-count-1].piece == None:
            count += 1
            yield (coord[0]-count,coord[1])
        return

    @staticmethod
    def right(max_right:int, limit:int, coord:BoardCoord, board:Board) -> Generator:
        count=0
        while (coord[0]+count+1) <= max_right and count <= limit and board.full_layout[coord[1]][coord[0]+count+1].piece == None:
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
    def compound(maxx:int, maxy:int, limitx:int, limity:int, coord:BoardCoord, genx:Callable, geny:Callable, board:Board) -> Generator:
        '''Take the x values from genx and the y values from geny'''
        list1=Movement.to_list(genx(maxx,limitx,coord,board))
        list2=Movement.to_list(geny(maxy,limity,coord,board))
        for i in range(min(len(list1),len(list2))):
            yield list1[i][0], list2[i][1]

    @staticmethod
    def orthogonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:BoardCoord, board:Board) -> Generator:
        '''Forward, backward, left, right, in that order'''
        for entry in Movement.forward(maxes[0],limits[0],coord,board):
            yield entry
        for entry in Movement.backward(maxes[1],limits[1],coord,board):
            yield entry
        for entry in Movement.left(maxes[2],limits[2],coord,board):
            yield entry
        for entry in Movement.right(maxes[3],limits[3],coord,board):
            yield entry

    @staticmethod
    def diagonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:BoardCoord, board:Board) -> Generator:
        '''Inputs: top, bottom, left, right\n
        Outputs: top-right, top-left, bottom-left, bottom-right'''
        for entry in Movement.compound(maxes[3],maxes[0],limits[3],limits[0],coord,Movement.right,Movement.forward, board):
            yield entry
        for entry in Movement.compound(maxes[2],maxes[0],limits[2],limits[0],coord,Movement.left,Movement.forward, board):
            yield entry
        for entry in Movement.compound(maxes[2],maxes[1],limits[2],limits[1],coord,Movement.left,Movement.backward, board):
            yield entry
        for entry in Movement.compound(maxes[3],maxes[1],limits[3],limits[1],coord,Movement.right,Movement.backward, board):
            yield entry
    
    @staticmethod
    def l_shape(max:tuple[int,int,int,int], limit:int, coord:BoardCoord, board:Board, lenx:int, leny:int) -> Generator:
        '''Maxes are forward, backward, left, right, in that order.'''
        units=[(leny,lenx),(leny,-lenx),(-leny,lenx),(-leny,-lenx),(lenx,leny),(lenx,-leny),(-lenx,leny),(-lenx,-leny)]
        for i in range(limit):
            for combo in units:
                if max[2] <= coord[0]+combo[0]*i <= max[3] and max[1] <= coord[1]+combo[1]*i <= max[0] and board.full_layout[coord[1]+combo[1]*i][coord[0]+combo[0]*i].piece == None:
                    yield (coord[0]+combo[0]*i,coord[1]+combo[1]*i)
        return

    @staticmethod
    def anywhere(board:Board):
        height=len(board.full_layout)
        width=len(board.full_layout[0])
        for y in range(height):
            for x in range(width):
                if board.full_layout[y][x].piece == None:
                    yield board.full_layout[y][x].boardpos

class Capture():
    @staticmethod
    def forward(max_height:int, limit:int, coord:BoardCoord, board:Board, hypo:bool=False) -> Generator:
        count=0
        while (coord[1]+count+1) <= max_height and count <= limit:
            count += 1
            if hypo:
                yield (coord[0],coord[1]+count)
            if board.full_layout[coord[1]+count][coord[0]].piece != None:
                yield (coord[0],coord[1]+count)
                break
        return

    @staticmethod
    def backward(max_depth:int, limit:int, coord:BoardCoord, board:Board, hypo:bool=False) -> Generator:
        count=0
        while (coord[1]-count-1) >= max_depth and count <= limit:
            count += 1
            if hypo:
                yield (coord[0],coord[1]-count)
            if board.full_layout[coord[1]-count][coord[0]].piece != None:
                yield (coord[0],coord[1]-count)
                break
        return

    @staticmethod
    def left(max_left:int, limit:int, coord:BoardCoord, board:Board, hypo:bool=False) -> Generator:
        count=0
        while (coord[0]-count-1) >= max_left and count <= limit:
            count += 1
            if hypo:
                yield (coord[0]-count,coord[1])
            if board.full_layout[coord[1]][coord[0]-count].piece != None:
                yield (coord[0]-count,coord[1])
                break
        return

    @staticmethod
    def right(max_right:int, limit:int, coord:BoardCoord, board:Board, hypo:bool=False) -> Generator:
        count=0
        while (coord[0]+count+1) <= max_right and count <= limit:
            count += 1
            if hypo:
                yield (coord[0]+count,coord[1])
            if board.full_layout[coord[1]][coord[0]+count].piece == None:
                yield (coord[0]+count,coord[1])
                break
        return

    @staticmethod
    def compound(maxx:int, maxy:int, limitx:int, limity:int, coord:BoardCoord, genx:Callable, geny:Callable, board:Board, hypo:bool=False) -> Generator:
        '''Take the x values from genx and the y values from geny'''
        list1=Movement.to_list(genx(maxx,limitx,coord,board,hypo))
        list2=Movement.to_list(geny(maxy,limity,coord,board,hypo))
        for i in range(min(len(list1),len(list2))):
            yield list1[i][0], list2[i][1]

    @staticmethod
    def orthogonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:BoardCoord, board:Board, hypo:bool=False) -> Generator:
        '''Forward, backward, left, right, in that order'''
        for entry in Capture.forward(maxes[0],limits[0],coord,board,hypo):
            yield entry
        for entry in Capture.backward(maxes[1],limits[1],coord,board,hypo):
            yield entry
        for entry in Capture.left(maxes[2],limits[2],coord,board,hypo):
            yield entry
        for entry in Capture.forward(maxes[3],limits[3],coord,board,hypo):
            yield entry

    @staticmethod
    def diagonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:BoardCoord, board:Board, hypo:bool=False) -> Generator:
        '''Inputs: top, bottom, left, right\n
        Outputs: top-right, top-left, bottom-left, bottom-right'''
        for entry in Capture.compound(maxes[3],maxes[0],limits[3],limits[0],coord,Capture.right,Capture.forward, board,hypo):
            yield entry
        for entry in Capture.compound(maxes[2],maxes[0],limits[2],limits[0],coord,Capture.left,Capture.forward, board,hypo):
            yield entry
        for entry in Capture.compound(maxes[2],maxes[1],limits[2],limits[1],coord,Capture.left,Capture.backward, board,hypo):
            yield entry
        for entry in Capture.compound(maxes[3],maxes[1],limits[3],limits[1],coord,Capture.right,Capture.backward, board,hypo):
            yield entry
    
    @staticmethod
    def l_shape(max:tuple[int,int,int,int], limit:int, coord:BoardCoord, board:Board, lenx:int, leny:int, hypo:bool=False) -> Generator:
        '''Maxes are forward, backward, left, right, in that order.'''
        units=[(leny,lenx),(leny,-lenx),(-leny,lenx),(-leny,-lenx),(lenx,leny),(lenx,-leny),(-lenx,leny),(-lenx,-leny)]
        for i in range(limit):
            for combo in units:
                if max[2] <= coord[0]+combo[0]*i <= max[3] and max[1] <= coord[1]+combo[1]*i <= max[0]:
                    if hypo or (board.full_layout[coord[1]+combo[1]*i][coord[0]+combo[0]*i].piece != None):
                        yield (coord[0]+combo[0]*i,coord[1]+combo[1]*i)
        return

    @staticmethod
    def anywhere(board:Board, hypo:bool=False):
        height=len(board.full_layout)
        width=len(board.full_layout[0])
        for y in range(height):
            for x in range(width):
                if board.full_layout[y][x].piece != None:
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
            temp += word
        elif temp == "":
            lines.append(" "+word)
        else:
            lines.append(temp)
            temp=[]
    return [line[1:] for line in lines]

class ModeInfo():
    def __init__(self, name:str, abstract:str, info:str, image:Surface, links:list[ModeInfo]):
        self.name=wrap_text(name, INFO_BORDERS[1]-INFO_BORDERS[0]-3*INFO_PADDING[0]-INFO_IMG_DIM[0], INFO_TITLE_FONT)
        self.abstract=wrap_text(abstract,INFO_BORDERS[1]-INFO_BORDERS[0]-2*INFO_PADDING[0], INFO_ALIAS_FONT)
        self.body=wrap_text(info, INFO_BORDERS[1]-INFO_BORDERS[0]-2*INFO_PADDING[0], INFO_BODY_FONT)
        self.image=image
        self.links=links

        self.scroll_offset=0
        self.scrollable=False

        self.name_height=INFO_TITLE_FONT.get_height()*len(self.name)
        self.abstract_height=INFO_ALIAS_FONT.get_height()*len(self.abstract)
        self.body_height=INFO_BODY_FONT.get_height()*len(self.body)

        self.image_pos:Coord=(INFO_BORDERS[0]+INFO_PADDING[0],INFO_PADDING[1]+self.name_height/2-INFO_IMG_DIM[1]/2)
        self.title_anchor:Coord=(INFO_BORDERS[0]+INFO_PADDING[0]*2+INFO_IMG_DIM[0])
        self.abstract_anchor:Coord=(INFO_BORDERS[0]+INFO_PADDING[0],INFO_PADDING[1]+self.name_height+INFO_PADDING[3])
        self.body_anchor:Coord=(self.abstract_anchor[0],self.abstract_anchor[1]+self.abstract_height+2*INFO_PADDING[2])

        self.display_base:Surface=Surface((INFO_BORDERS[1]-INFO_BORDERS[0],self.body_anchor[1]+self.body_height+INFO_PADDING[2]+2*INFO_PADDING[3]+INFO_BODY_FONT.get_height()+(INFO_MINI_DIM[1]+INFO_PADDING[3])*ceil(len(self.links)/4)),SRCALPHA,32)
        self.scrollable=self.display_base.get_height() > INFO.current_h
        self.display_base.fill(SHADES[0])
        draw.rect(self.display_base,SHADES[1],Rect(0,0,INFO_BORDERS[1]-INFO_BORDERS[0],self.body_anchor[1]+self.body_height+INFO_PADDING[2]),border_radius=ROUNDNESS) #first rounded rect layer
        draw.rect(self.display_base,SHADES[2],Rect(0,0,INFO_BORDERS[1]-INFO_BORDERS[0],self.abstract_anchor[1]+self.abstract_height+INFO_PADDING[2]),border_radius=ROUNDNESS) #second rounded rect layer, for title and abstract
        self.display_base.blit(self.image,self.image_pos)
        for i in range(len(self.name)):
            self.display_base.blit(INFO_TITLE_FONT.render(self.name[i],True,(255,255,255)),(self.title_anchor[0],self.title_anchor[1]+INFO_TITLE_FONT.get_height()*i))
        for i in range(len(self.abstract)):
            self.display_base.blit(INFO_ALIAS_FONT.render(self.abstract[i],True,(255,255,255)),(self.abstract_anchor[0],self.abstract_anchor[1]+INFO_ALIAS_FONT.get_height()*i))
        for i in range(len(self.body)):
            self.display_base.blit(INFO_BODY_FONT.render(self.body[i],True,(255,255,255)),(self.body_anchor[0],self.body_anchor[1]+INFO_BODY_FONT.get_height()*i))
            self.links_anchor=(self.body_anchor[0],self.body_anchor[1]+INFO_BODY_FONT.get_height()*i+INFO_PADDING[3])
        self.display_base.blit(INFO_BODY_FONT.render("Pieces:"),self.links_anchor)
        self.links_anchor=(self.links_anchor[0],self.links_anchor+INFO_PADDING[3]+INFO_BODY_FONT.get_height())
        carry_over_height=[0]
        for i in range(ceil(len(self.links)/4)): #rows
            words_height=0
            for j in range(min(4,len(self.links)-4*i)): #individual links
                target=self.links[4*i+j]
                self.display_base.blit(transform.scale(target.image,INFO_MINI_DIM),(self.links_anchor[0]+(INFO_MINI_DIM+LINK_SPACING)*j,self.links_anchor[1]+(INFO_MINI_DIM[1]*INFO_PADDING[3])*i+sum(carry_over_height)))
                words=wrap_text(target.name,INFO_MINI_DIM[0])
                for k in len(words):
                    self.display_base.blit(INFO_BODY_FONT.render(words[k],True,(255,255,255)),(self.links_anchor[0]+j*(INFO_MINI_DIM[0]+LINK_SPACING)+INFO_MINI_DIM/2-INFO_BODY_FONT.size(words[k])[0]/2,))
                words_height=max(words_height, INFO_BODY_FONT.get_height()*len(words))
            carry_over_height.append(words_height)

    def display(self, surface:Surface):
        surface.blit(self.display_base, (INFO_BORDERS[0],-self.scroll_offset))
        
    def display_mini(self):
        pass

class PieceInfo():
    def __init__(self, name:str, alias:str, info:str, included_in:list[ModeInfo], moves:Surface):
        self.name=wrap_text(name, INFO_BORDERS[1]-INFO_BORDERS[0]-3*INFO_PADDING[0]-INFO_IMG_DIM[0], INFO_TITLE_FONT)
        self.alias=wrap_text(alias, INFO_BORDERS[1]-INFO_BORDERS[0]-2*INFO_PADDING[0], INFO_BODY_FONT)
        self.info=wrap_text(info, INFO_BORDERS[1]-INFO_BORDERS[0]-2*INFO_PADDING[0], INFO_BODY_FONT)
        self.included_in=included_in
        self.moves=moves

    def display(self):
        pass

    def display_mini(self):
        pass

print("")
'''
To-do:
Checkmate checking
Extra move options (for variants like beirut chess, where there is an option to detonate)
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