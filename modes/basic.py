'''Foundation classes and methods for chess modes. Includes:
Piece template, Board template, Tile object, Movement methods, Capture methods, Rules template, OptionBar object, Pocket object, and Info template.'''

from __future__ import annotations
from math import copysign, ceil
from os.path import join
from typing import Literal
from pygame import *
from collections.abc import Generator, Callable, Iterable, Container
import itertools
import math as ma
import time as t
import copy

type Path=str
type Coord=tuple[int,int]
type BoardCoord=tuple[int,int]
type BoardLayout=list[list[Tile]]
type Colour=tuple[int,int,int]

hidden=True
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
OTR_TIL_DIR=join("assets","sprites","other")
FNT_IMG_DIR=join("assets","montserrat")
POCKET_ANCHORS=([100,1000],[100,100])

SHADES:list[Colour]=[(40,40,40),(55, 55, 55),(92, 92, 92),(131, 131, 131),(177, 177, 177),(233, 233, 233)]
GREENS:list[Colour]=[(69,117,60),(129,182,76),(152,193,91),(160,210,96)]
ORANGE:Colour=(252,175,0)
WHITE:Colour=(255,255,255)
BLACK:Colour=(0,0,0)
#SHADES=[(17,17,17),(51,51,51),(85,85,85),(119,119,119),(153,153,153)]
RED=(255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
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
ARROWHEAD=Surface((40,40),SRCALPHA,32)
draw.rect(ARROWHEAD,SELECT_COLOUR,Rect(0,0,40,10))
draw.rect(ARROWHEAD,SELECT_COLOUR,Rect(30,0,10,40))
ARROWHEAD=transform.rotate(ARROWHEAD,45)

def denest(source:Container, depth:int=999) -> list:
    result=[]
    for item in source:
        if isinstance(item, Container) and depth != 0:
            result.extend(denest(item, depth-1))
        else:
            result.append(item)
    return result

class Game():
    '''Placeholder class for properties of game modes so intellisense can check my code. Not supposed to be instantiated.'''
    def __init__(self):
        self.clock:time.Clock
        #self.screen=display.set_mode((WIN_WIDTH,WIN_HEIGHT))
        self.screen:Surface
        self.FPS:int
        self.running:bool
        self.menu:str
        self.submenu:str
        self.last_menu:str
        self.mode
        self.additional=None
        self.mode:...
        self.connect:bool
        self.incoming:str
        self.outgoing:str
        self.a_m_offset:int
        self.a_p_offset:int
        self.timer:tuple[int,int,int]
        self.selected:Tile|None
        self.prev_selected:Tile|None
        self.board:Board|None
        raise RuntimeError("This is a utility placeholder class that is not supposed to be instantiated. This is why you shouldn't try.")
    
class Arrow():
    def __init__(self,start:Coord,end:Coord,colour:Colour=SELECT_COLOUR):
        self.start=start
        self.end=end
        self.colour=colour
        mag_x=end[0]-start[0]
        mag_y=end[1]-start[1]
        if mag_x != 0:
            angle=ma.atan(abs(mag_y)/abs(mag_x))*180/ma.pi
        else:
            angle=180 if mag_y > 0 else 0
        if mag_x < 0 and mag_y < 0:
            angle = 270-angle
        elif mag_x < 0:
            angle = 180-angle
        elif mag_y < 0 and mag_x != 0:
            angle = 360-angle
        self.arrow=transform.rotate(ARROWHEAD,angle)

    def display(self, surface:Surface):
        draw.line(surface,self.colour,self.start,self.end,10)
        surface.blit(self.arrow,(self.end[0]-27,self.end[1]-20))

def contrast(colour:tuple[int,int,int]):
    brightness=0.299*colour[0] + 0.587*colour[1] + 0.114*colour[2]
    if brightness < 100:
        return (255,255,255)
    else:
        return (0,0,0)

class Timer():
    def __init__(self, amount:int|float, incr:int, delay:int, anchor:Coord, textfont:font.Font, active_colour:Colour=WHITE, inactive_colour:Colour=SHADES[2], active=False, trip_colour:Colour=RED):
        self.increment=incr
        self.delay=delay
        self.countdown=delay
        self.anchor=anchor
        self.active=active
        self.internal_time:float=float(amount)
        self.active_col=active_colour
        self.inactive_col=inactive_colour
        self.trip_colour=trip_colour
        self.tripped=False
        self.textfont=textfont
        self.activatable=True
        if self.internal_time > 0:
            self.text:Surface=self.textfont.render(self.prettify(),True,contrast(self.active_col) if self.active else contrast(self.inactive_col))
        else:
            self.text:Surface=self.textfont.render("--:--",True,contrast(self.inactive_col))
            self.activatable=False
            self.active=False
        self.rect=Rect(anchor[0],anchor[1],self.text.get_width()+20,self.text.get_height()+10)
        self.lasttime=t.time()
        self.inc_text=textfont.render(f"+{self.increment//60}:{self.increment%60}",True,WHITE)
        self.inc_text_timer=0
    
    def display(self, surface:Surface):
        if not self.tripped:
            if self.active and self.delay > 0:
                draw.rect(surface,RED,Rect(self.rect.x-5,self.rect.y-5,(self.rect.width+10)*(self.countdown/self.delay),self.rect.height+10))
            draw.rect(surface,self.active_col if self.active else self.inactive_col,self.rect,border_radius=ROUNDNESS)
        else:
            draw.rect(surface,self.trip_colour,self.rect,border_radius=ROUNDNESS)
        if self.inc_text_timer > 0:
            surface.blit(self.inc_text,(self.rect.x+10,self.rect.y+copysign(15+self.textfont.get_height(),surface.get_height()/2-self.rect.y)))
            self.inc_text_timer -= (t.time()-self.lasttime)
        surface.blit(self.text,(self.rect.x+10,self.rect.y+5))
        if self.active and not self.tripped:
            if self.countdown > 0:
                self.countdown -= (t.time()-self.lasttime)
            else:
                self.internal_time -= (t.time()-self.lasttime)
            self.lasttime=t.time()
            self.text=self.textfont.render(self.prettify(),True,contrast(self.active_col))
            self.rect.width=self.text.get_width()+20
        if self.internal_time <= 0 and self.activatable:
            self.tripped=True
            self.text=self.textfont.render("00:00",True,contrast(self.trip_colour))
            self.rect.width=self.text.get_width()+20

    def switch(self):
        if not self.tripped and self.activatable:
            self.active=not self.active
            if self.active:
                self.lasttime=t.time()
                self.text=self.textfont.render(self.prettify(),True,contrast(self.active_col))
                self.countdown=self.delay
            else:
                self.internal_time += self.increment
                self.text=self.textfont.render(self.prettify(),True,contrast(self.inactive_col))
                if self.increment > 0:
                    self.inc_text_timer=60

    def prettify(self):
        minutes=str(max(ma.floor(self.internal_time/60),0))
        seconds=str(max(ma.floor(self.internal_time%60),0))
        if int(seconds) < 10:
            seconds="0"+seconds
        return f"{minutes}:{seconds}"

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
        self.royal=check_target #whether the piece is a target for check-like conditions
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

    def moves(self, game:Game) -> list[BoardCoord]:
        '''Every square the piece can move to (excluding captures). Most of the time, a few calls to Movement functions are enough.'''
        pass

    def capture_squares(self, game:Game, hypo:bool=False) -> list[BoardCoord]:
        '''Every square the piece can capture on, factoring in the board. If hypo is True, returns every square the piece can capture on hypothetically.'''
        pass

    def move_to(self, final:Tile, game:Game|None=None):
        '''Move to a Tile. Set its parent's piece to None and set the final Tile's piece to this.'''
        self.parent.piece=None
        final.piece=self
        self.parent=final

    def get_options(self) -> OptionsBar:
        return

class Tile():
    '''A container for tile information. Is True if there it contains a piece, is False otherwise'''
    def __init__(self, boardcoord:BoardCoord, base:Literal["empty", "void"], rect:Rect, parent:object, colour:Literal[0,1]|None=None, piece:Piece=None):
        self.boardpos=boardcoord
        self.base=base
        self.piece:Piece|None=piece
        self.image:Surface=None
        self.colour=colour
        self.parent=parent
        self.rect:Rect=rect
        self.move_target:bool=False
        self.capture_target:bool=False
        self.locked:bool=False #whether this Tile can be moved to.
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

    def display(self, surface:Surface, mp:Coord, mu:bool) -> Tile|None|False:
        '''Display the piece at its position. Returns itself if clicked, or False if deselected. Returns None otherwise.'''
        if isinstance(self.piece, Piece): #show piece
            surface.blit(self.piece.image, (self.rect.x,self.rect.y))
        if self.move_target: #if target for move
            draw.circle(surface,SELECT_COLOUR,self.rect.center,9)
        if self.capture_target or self.rect.collidepoint(mp) or self.selected: #if selected or target for capture
            draw.rect(surface,SELECT_COLOUR,self.rect,5)
        if self.locked:
            draw.line(surface,SELECT_COLOUR,self.rect.topleft,self.rect.bottomright,5)

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
        
    def propagate_options(self, options:OptionsBar):
        if isinstance(self.parent, Board):
            self.parent.active_options=options
        else:
            raise TypeError("And what exactly are you propagating to?")

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
        self.arrows:list[Arrow]|list[None]=[]
        self.timers:list[Timer]=[]

    def construct(self, anchor:Coord, amt:int|float, inc:int, delay:int, timerfont:font.Font):
        '''Creates a list of lists representing the full board without intial pieces placed. Spaces with tiles are called "empty". For non-quadrilateral boards, non-tile spaces are called "void".'''
        self.anchor=anchor
        result=[]
        count=0
        if self.layout == None:
            for y in range(self.height):
                temp=[]
                for x in range(self.width):
                    temp.append(Tile((x,y),"empty",Rect(anchor[0]+(x*self.tile_dim),anchor[1]+(y*self.tile_dim),self.tile_dim,self.tile_dim),self))
                result.append(temp)
        else:
            for i in range(len(self.layout)):
                temp=[]
                x_count=0
                for j in range(len(self.layout[i])):
                    code=self.layout[i][j]
                    if code in numbers:
                        for k in range(int(code)):
                            temp.append(Tile((x_count,i),"empty",Rect(anchor[0]+(x_count*self.tile_dim[0]),anchor[1]+(i*self.tile_dim[1]),self.tile_dim[0],self.tile_dim[1]),self,1 if count%2 == 0 else 0,))
                            x_count += 1
                            count += 1
                    elif code in letters:
                        for k in range(letters.index(code)):
                            temp.append(Tile((x_count+1,i+1),"void",Rect(anchor[0]+(x_count*self.tile_dim),anchor[1]+(i*self.tile_dim),self.tile_dim,self.tile_dim),self))
                            x_count += 1
                            count += 1
                    else:
                        raise TypeError(f"Invalid value: {code}")
                count=i+1
                result.append(temp)
        self.full_layout=result
        self.rect=Rect(anchor[0],anchor[1],self.tile_dim[0]*self.width,self.tile_dim[1]*self.height)
        self.timers=(Timer(amt,inc,delay,(self.get_width()+20,self.anchor[0]+timerfont.get_height()),timerfont),Timer(amt,inc,delay,(self.get_width()+20,self.get_height()-10-timerfont.get_height()),timerfont,active=True))
    
    def populate(self, custom_initpos:str|None=None):
        full_board=self.full_layout
        '''Takes in a constructed board and populates it with pieces.'''
        extras=False
        if custom_initpos != None:
            try:
                args=custom_initpos.split(" ")
                temp=self.human_to_internal(args.pop(0))
            except TypeError:
                pass
            else:
                self.initpos=temp
                try:
                    self.check_extras(args,temp)
                except TypeError:
                    pass
                else:
                    extras=True
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
        if extras:
            self.extras_human_to_internal(args)
    
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
                if temp != None and (self.active_options == None or (isinstance(self.active_options, OptionsBar) and self.active_options.optional)):
                    perm=temp
        if isinstance(self.active_options, OptionsBar):
            if not self.active_options.anchored:
                self.active_options.anchor(self.anchor[0]+self.get_width()+10,self.anchor[1]+self.get_height()/2)
            remove_options=self.active_options.display(surface, mp, mu, perm)
            if remove_options:
                self.active_options=None
        if isinstance(self.whitepocket, Pocket):
            self.whitepocket.display(surface, mp, mu, perm)
        if isinstance(self.blackpocket, Pocket):
            self.blackpocket.display(surface, mp, mu, perm)
        for arrow in self.arrows:
            arrow.display(surface)
        for timer in self.timers:
            timer.display(surface)
        return perm
    
    def scrub(self):
        for row in self.full_layout:
            for tile in row:
                tile.move_target=False
                tile.capture_target=False
                tile.locked=False
        if isinstance(self.active_options, OptionsBar) and self.active_options.optional:
            self.active_options=None
        self.arrows=[]

    def progress_turn(self):
        self.turn_number += 1
        self.turn=self.turn_number%2
        for timer in self.timers:
            timer.switch()

    def get(self, coord:BoardCoord|int, coord2:int=None) -> Tile|Literal[False]:
        '''Get a board tile using its board coordinates. Returns False if the Tile doesn't exist.'''
        try:
            coord=tuple(coord)
        except:
            pass
        if isinstance(coord,tuple) and len(coord) == 2 and isinstance(coord[0],int) and isinstance(coord[1],int):
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
            raise TypeError(f"Cannot access board position based on these arguments: {coord},{coord2}")
        
    def get_matching(self, match:Callable[[Tile],bool]) -> list[Tile]:
        result=[]
        for row in self.full_layout:
            for tile in row:
                if match(tile) and tile.colour != None:
                    result.append(tile)
        return result
        
    def board_to_coord(self, pos:BoardCoord) -> Coord:
        return (pos[0]*self.tile_dim[0]+self.tile_dim[0]/2+self.anchor[0],pos[1]*self.tile_dim[1]+self.tile_dim[1]/2+self.anchor[1])
    
    def get_width(self) -> int:
        return self.width*self.tile_dim[0]+self.anchor[0]
    
    def get_height(self) -> int:
        return self.height*self.tile_dim[1]+self.anchor[1]

    def human_to_internal(self, arg:str) -> list[str]:
        arg=arg.split("/")
        if len(arg) != self.height:
            raise TypeError("Translation failed.")
        pieceslist=list(self.piecesdict.keys())
        for row in arg:
            row_length=0
            for char in row:
                if char in numbers:
                    row_length += int(char)
                elif char in pieceslist:
                    row_length += 1
                else:
                    raise TypeError("Translation failed.")
            if row_length != self.width:
                raise TypeError("Translation failed.")
        return arg

    def internal_to_human(self) -> str:
        result=''
        reverse_piecedict={self.piecesdict[value]:value for value in self.piecesdict}
        for row in self.full_layout:
            empty_counter=0
            for tile in row:
                if isinstance(tile.piece, Piece):
                    if empty_counter > 0:
                        result += str(empty_counter)
                        empty_counter=0
                    result += reverse_piecedict[type(tile.piece)]
                else:
                    empty_counter += 1
            if empty_counter > 0:
                result += str(empty_counter)
            empty_counter=0
            if row != self.full_layout[-1]:
                result += "/"
        result += " "
        result += "w " if self.turn == 0 else "b "
        result += "KQkq "
        tiles = self.get_matching(lambda t: True if t.piece == None and hasattr(t.piece,"en_passantable") and t.piece.en_passantable else False)
        for tile in tiles:
            result += letters.index(tile.boardpos[1]+1)
            result += str(tile.boardpos[0])+" "
        if tiles == []:
            result += "- "
        result += "0 "
        result += str(self.turn_number)
        return result
    
    def check_extras(self, arg:list[str], layout:list[str]):
        if arg == []:
            return
        if arg[0] not in ["w","b"]:
            raise TypeError
        if "K" in arg[1] and (layout[7][4] != "K" or layout[7][7] != "R"):
            raise TypeError
        if "Q" in arg[1] and (layout[7][4] != "K" or layout[7][0] != "R"):
            raise TypeError
        if "k" in arg[1] and (layout[0][4] != "k" or layout[0][7] != "r"):
            raise TypeError
        if "q" in arg[1] and (layout[0][4] != "k" or layout[0][0] != "r"):
            raise TypeError
        if arg[2] != "-" and layout[int(arg[2][1])-1][letters.index(arg[2][0])-1] not in ["P","p"]:
            raise TypeError
        try:
            int(arg[3])
            int(arg[4])
        except:
            raise TypeError

    def extras_human_to_internal(self, arg:list[str]):
        if arg == []:
            return
        self.turn=0 if arg[0] == "w" else 1
        if "K" not in arg[1]:
            self.get(7,7).has_moved=True
        if "Q" not in arg[1]:
            self.get(0,7).has_moved=True
        if "k" not in arg[1]:
            self.get(7,0).has_moved=True
        if "q" not in arg[1]:
            self.get(0,0).has_moved=True
        if arg[2] != "-":
            self.get(letters.index(arg[2][0])-1,int(arg[2][1])-1).en_passantable=True
        self.turn_number=int(arg[4])

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
    def line(dir:int, step:int, max:int, limit:int, coord:BoardCoord, game:Game) -> Generator:
        if game.board.turn != game.board.full_layout[coord[1]][coord[0]].piece.colour:
            return
        count=0
        max+=copysign(1,step)
        coord=list(coord)
        coord[dir] += step
        while coord[dir] != max and count < limit and game.board.get(coord).piece == None:
            count+=1
            if not game.board.get(coord).locked:
                yield copy.deepcopy((coord[0],coord[1]))
            coord[dir] += step
    
    @staticmethod
    def diagonal(step_x:int, step_y:int, max_x:int, max_y:int, limit:int, coord:BoardCoord, game:Game) -> Generator:
        if game.board.turn != game.board.full_layout[coord[1]][coord[0]].piece.colour:
            return
        count=0
        max_x+=int(copysign(1,step_x))
        max_y+=int(copysign(1,step_y))
        next_x=coord[0]+int(copysign(count+1,step_x))
        next_y=coord[1]+int(copysign(count+1,step_y))
        while next_x != max_x and next_y != max_y and count < limit and game.board.full_layout[next_y][next_x].piece == None:
            count += 1
            if not game.board.get(next_x,next_y).locked:
                yield copy.deepcopy((next_x,next_y))
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
    def compound(maxx:int, maxy:int, limitx:int, limity:int, coord:BoardCoord, genx:Callable, geny:Callable, game:Game) -> Generator:
        '''Take the x values from genx and the y values from geny'''
        list1=Movement.to_list(genx(maxx,limitx,coord,game))
        list2=Movement.to_list(geny(maxy,limity,coord,game))
        for i in range(min(len(list1),len(list2))):
            yield list1[i][0], list2[i][1]

    @staticmethod
    def orthogonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:BoardCoord, game:Game) -> Generator:
        '''Forward, backward, left, right, in that order'''
        return itertools.chain(Movement.line(1,-1,maxes[0],limits[0],coord,game),Movement.line(1,1,maxes[1],limits[1],coord,game),Movement.line(0,-1,maxes[2],limits[2],coord,game),Movement.line(0,1,maxes[3],limits[3],coord,game))

    @staticmethod
    def diagonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:BoardCoord, game:Game) -> Generator:
        '''Inputs: top, bottom, left, right\n
        Outputs: top-right, top-left, bottom-left, bottom-right'''
        return itertools.chain(Movement.diagonal(1,-1,maxes[3],maxes[0],limits[0],coord,game),Movement.diagonal(-1,-1,maxes[2],maxes[0],limits[1],coord,game),Movement.diagonal(-1,1,maxes[2],maxes[1],limits[2],coord,game),Movement.diagonal(1,1,maxes[3],maxes[1],limits[3],coord,game))
    
    @staticmethod
    def l_shape(max:tuple[int,int,int,int], limit:int, coord:BoardCoord, game:Game, lenx:int, leny:int) -> Generator:
        '''Maxes are forward, backward, left, right, in that order.'''
        if game.board.turn != game.board.get(coord).piece.colour:
            return
        units=[(leny,lenx),(leny,-lenx),(-leny,lenx),(-leny,-lenx),(lenx,leny),(lenx,-leny),(-lenx,leny),(-lenx,-leny)]
        for combo in units:
            for i in range(limit):
                next_val=(coord[0]+combo[0]*(i+1),coord[1]+combo[1]*(i+1))
                if max[2] <= next_val[0] <= max[3] and max[0] <= next_val[1] <= max[1] and game.board.full_layout[next_val[1]][next_val[0]].piece == None and not game.board.get(next_val).locked:
                    yield copy.deepcopy(next_val)

    @staticmethod
    def anywhere(game:Game, coord:BoardCoord):
        if game.board.turn != game.board.full_layout[coord[1]][coord[0]].piece.colour:
            return
        height=len(game.board.full_layout)
        width=len(game.board.full_layout[0])
        for y in range(height):
            for x in range(width):
                if game.board.full_layout[y][x].piece == None and not game.board.get(x,y).locked:
                    yield game.board.full_layout[y][x].boardpos

class Capture():
    @staticmethod
    def line(dir:int, step:int, max:int, limit:int, coord:BoardCoord, game:Game, col:int, hypo:bool=False) -> Generator:
        if game.board.turn != game.board.full_layout[coord[1]][coord[0]].piece.colour and not hypo:
            return
        count=0
        max+=copysign(1,step)
        coord=list(coord)
        coord[dir] += step
        while coord[dir] != max and count < limit:
            count+=1
            if (game.board.get(coord).piece != None and game.board.get(coord).piece.colour != col) or hypo:
                if not game.board.get(coord).locked:
                    yield tuple(coord)
                if (game.board.get(coord).piece != None and game.board.get(coord).piece.colour != col):
                    return
            if game.board.get(coord).piece != None and game.board.get(coord).piece.colour == col:
                return
            coord[dir] += step
    
    @staticmethod
    def diagonal(step_x:int, step_y:int, max_x:int, max_y:int, limit:int, coord:BoardCoord, game:Game, col:int, hypo:bool=False) -> Generator:
        if game.board.turn != game.board.full_layout[coord[1]][coord[0]].piece.colour and not hypo:
            return
        count=0
        max_x+=int(copysign(1,step_x))
        max_y+=int(copysign(1,step_y))
        next_x=coord[0]+int(copysign(count+1,step_x))
        next_y=coord[1]+int(copysign(count+1,step_y))
        while next_x != max_x and next_y != max_y and count < limit:
            count += 1
            if (game.board.get(next_x,next_y).piece != None and game.board.get(next_x,next_y).piece.colour != col) or hypo:
                if not game.board.get(next_x,next_y).locked:
                    yield (next_x,next_y)
                if game.board.get(next_x,next_y).piece != None and game.board.get(next_x,next_y).piece.colour != col:
                    return
            if game.board.get(next_x,next_y).piece != None and game.board.get(next_x,next_y).piece.colour == col:
                return
            next_x=coord[0]+int(copysign(count+1,step_x))
            next_y=coord[1]+int(copysign(count+1,step_y))

    @staticmethod
    def compound(maxx:int, maxy:int, limitx:int, limity:int, coord:BoardCoord, genx:Callable, geny:Callable, game:Game, col:int, hypo:bool=False) -> Generator:
        '''Take the x values from genx and the y values from geny'''
        list1=Movement.to_list(genx(maxx,limitx,coord,game,col,hypo))
        list2=Movement.to_list(geny(maxy,limity,coord,game,col,hypo))
        for i in range(min(len(list1),len(list2))):
            yield list1[i][0], list2[i][1]

    @staticmethod
    def orthogonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:BoardCoord, game:Game, col:int, hypo:bool=False) -> Generator:
        '''Forward, backward, left, right, in that order'''
        return itertools.chain(Capture.line(1,-1,maxes[0],limits[0],coord,game,col,hypo),Capture.line(1,1,maxes[1],limits[1],coord,game,col,hypo),Capture.line(0,-1,maxes[2],limits[2],coord,game,col,hypo),Capture.line(0,1,maxes[3],limits[3],coord,game,col,hypo))

    @staticmethod
    def diagonals(maxes:tuple[int,int,int,int], limits:tuple[int,int,int,int], coord:BoardCoord, game:Game, col:int, hypo:bool=False) -> Generator:
        '''Inputs: top, bottom, left, right\n
        Outputs: top-right, top-left, bottom-left, bottom-right'''
        return itertools.chain(Capture.diagonal(1,-1,maxes[3],maxes[0],limits[0],coord,game,col,hypo),Capture.diagonal(-1,-1,maxes[2],maxes[0],limits[1],coord,game,col,hypo),Capture.diagonal(-1,1,maxes[2],maxes[1],limits[2],coord,game,col,hypo),Capture.diagonal(1,1,maxes[3],maxes[1],limits[3],coord,game,col,hypo))
    
    @staticmethod
    def l_shape(max:tuple[int,int,int,int], limit:int, coord:BoardCoord, game:Game, lenx:int, leny:int, col:int, hypo:bool=False) -> Generator:
        '''Maxes are forward, backward, left, right, in that order.'''
        if game.board.turn != game.board.full_layout[coord[1]][coord[0]].piece.colour and not hypo:
            return
        units=[(leny,lenx),(leny,-lenx),(-leny,lenx),(-leny,-lenx),(lenx,leny),(lenx,-leny),(-lenx,leny),(-lenx,-leny)]
        for combo in units:
            for i in range(limit):
                next_val=(coord[0]+combo[0]*(i+1),coord[1]+combo[1]*(i+1))
                if max[2] <= next_val[0] <= max[3] and max[0] <= next_val[1] <= max[1] and ((game.board.get(next_val).piece != None and game.board.get(next_val).piece.colour != col) or hypo) and not game.board.get(next_val).locked:
                    yield next_val
                    if (game.board.get(next_val).piece != None and game.board.get(next_val).piece.colour != col):
                        break

    @staticmethod
    def anywhere(game:Game, col:int, coord:BoardCoord, hypo:bool=False):
        if game.board.turn != game.board.full_layout[coord[1]][coord[0]].piece.colour and not hypo:
            return
        height=len(game.board.full_layout)
        width=len(game.board.full_layout[0])
        for y in range(height):
            for x in range(width):
                if game.board.full_layout[y][x].piece != None and game.board.full_layout[y][x].piece.colour != col and not game.board.get(x,y).locked:
                    yield game.board.full_layout[y][x].boardpos

BRICK_WALL=Piece("Brick Wall",-1,-1,join(PCS_IMG_DIR,"pawn_w.png"))
class Rules():
    '''Gamerules that can be altered or used unchanged depending on the gamemode's requirements. Includes win conditions and check-like conditions (more generally, functions that return the list of board positions to lock)'''
    @staticmethod
    def win(game:Game) -> tuple[list[BoardCoord],bool,str]:
        '''A generalisation of checkmate. Returns whether or not a win has occurred, and which side has won. Is checkmate by default. pieces is a list of movable Pieces.'''
        '''If the piece is in check, it can be unchecked by movement, occulsion or capturing the checking piece. If the piece has no possible moves, none of your pieces can move to occlusion squares, and none of your pieces can capture the checking piece, checkmate is reached.'''
        info=Rules.lock(game,True)
        if info == []:
            return [], False, game.board.turn
        locked, squares_to_occlude, possible_moves, attacking_pieces, target=info
        squares_to_occlude=denest(squares_to_occlude,1)
        colour=game.board.turn
        yourpieces=[tile.piece for tile in game.board.get_matching(lambda t: True if t.piece != None and t.piece.colour == colour else False)]

        if info != None:
            if possible_moves != []: #check if no possible moves. If there are none, proceed to next check
                return locked, False, colour
            else:
                your_capture_squares:list[BoardCoord]=[]
                your_move_squares:list[BoardCoord]=[]
                for piece in yourpieces:
                    your_move_squares.extend(piece.moves(game))
                    your_capture_squares.extend(piece.capture_squares(game))
                for square in your_move_squares:
                    if square in squares_to_occlude:
                        possible_moves.append(square)
                for square in your_capture_squares:
                    if square in attacking_pieces:
                        possible_moves.append(square)

        if possible_moves == []:
            return locked, True, colour
        else:
            return locked, False, colour
        
    @staticmethod
    def gen_capture_squares(game:Game, pcs:list[Piece]) -> list[BoardCoord]:
        '''Return the list of squares that the specified pieces can currently capture on'''
        squares:list[BoardCoord]=[]
        for piece in pcs:
            temp=piece.capture_squares(game,True)
            if temp != None:
                squares.extend(piece.capture_squares(game,True))
        return squares

    @staticmethod
    def lock(game:Game, returnall:bool=False):
        '''A generalisation of checks. Returns a list of board positions to lock down. Is check by default. Takes around one hundredth of a second to complete with check, and half that without check, so it chould be fine to call a lot.'''
        '''Entering check:
        The King is in check if any piece can capture it. This is detected by calling Piece.capture_squares() on every piece and seeing if the King is in one of them. Alternatively, a virtual copy of every piece could be instantiated on the King's position, then their moves detected. If a piece can capture the same type of piece (assuming move and capture symmetry), the King is in check. This is faster but mentally costlier. It is also less general, not applying in variants where moves and captures are not symmetrical across positions and/or colours. The first solution will be implemented.'''
        '''Squares that can be moved to during check:
        Check is exited if the King moves into an un-attacked square, if the attacking piece is blocked, or if the attaking piece is captured. Thus, the squares that can be moved to are the safe moves for the checked piece, line-of-sight squares of all the attacking pieces, and the attacking piece itself.'''

        colour=game.board.turn
        target=game.board.get_matching(lambda t: True if t.piece != None and t.piece.royal and t.piece.colour == colour else False)[0].piece
        if target == []:
            return []
        check=False #whether the target is in check
        possible_moves=target.moves(game) #the target's possible moves when not checked
        attacking_pieces:list[Piece]=[] #the pieces attacking the target
        not_locked=[] #board spaces that are not locked
        enemypieces=[tile.piece for tile in game.board.get_matching(lambda t: True if t.piece != None and t.piece.colour != target.colour else False)]

        for piece in enemypieces: #check if the target is in check and which pieces are checking it
            for square in piece.capture_squares(game,True):
                if game.board.get(square).piece == target:
                    check=True
                    attacking_pieces.append(piece)
     
        if not check:
            return []
        else:
            not_locked.extend(target.moves(game)) #squares the target can move to are not locked (obviously)

            if len(attacking_pieces) == 1:
                not_locked.append(attacking_pieces[0].parent.boardpos) #if only one piece is attacking, it can be captured to end the check.

            occlude=[]
            occludable_line=[]
            '''
            Every square that is being attacked by a piece that is attacking the target is checked. The square is filled with a placeholder Brick Wall and it is checked if the piece can still attack the target. If it cannot, the square is added to occludable_lines. Occludable_lines is a list of lists, each list belonging to one attacking piece. If there is only one attacking piece, occluding any of its hypothetical capture squares can block the check. Otherwise, only sqaures belonging to all the attacking pieces can be occluded to block the check. This is accomplished using set intersection.
            '''
            for piece in attacking_pieces:
                for square in piece.capture_squares(game,True):
                    original_piece=game.board.get(square).piece
                    game.board.get(square).piece=BRICK_WALL
                    occludable=True
                    for square_2 in piece.capture_squares(game,True):
                        if game.board.get(square_2).piece == target or square_2 == target.parent.boardpos:
                            occludable=False
                    if occludable:
                        occludable_line.append(square)
                    game.board.get(square).piece=original_piece
                occlude.append(set(occludable_line))
                occludable_line=[]
            if len(attacking_pieces) != 1:
                real_occlude=occlude[0]
                for line in occlude:
                    real_occlude=real_occlude&line
                occlude=real_occlude
                not_locked.extend(list(occlude))
            else:
                not_locked.extend(list(occlude[0]))

            result=[]
            for row in game.board.full_layout:
                for square in row:
                    if square.boardpos not in not_locked:
                        result.append(square.boardpos)
            if not returnall:
                return result
            else:
                return (result, [list(line) for line in occlude], possible_moves, [piece.parent.boardpos for piece in attacking_pieces], target)
            
    @staticmethod
    def interpret():
        pass

class OptionsBar():
    def __init__(self, parent:Piece, contains:list[Tile], clickfunc:Callable[[Tile, OptionsBar, None|Tile], None], choose_tile:bool=False, message:Surface=None, optional:bool=False):
        self.parent=parent
        self.contains=contains
        self.on_click=clickfunc #takes in the tile and optionsbar that called it, also takes the tile that was chosen if choose_tile is True.
        self.choose_tile=choose_tile
        self.active_choice:Tile|None=None
        self.message=message
        self.optional=optional
        self.anchored:bool=False
        self.height:int=0
        for i in range(len(self.contains)):
            self.contains[i].rect.width=STD_TILEDIM[0]
            self.contains[i].rect.height=STD_TILEDIM[1]
        for tile in self.contains:
            self.height += tile.rect.height
        self.selected:Tile|None=None

    def anchor(self, edge_x:int, centre_y:int):
        for i in range(len(self.contains)):
            self.contains[i].rect.x=edge_x
            self.contains[i].rect.y=centre_y-self.height/2+STD_TILEDIM[0]*i
        if isinstance(self.message, Surface):
            self.message_anchor=(self.contains[0].rect.x+self.contains[0].rect.width+10, centre_y-self.message.get_height()/2)
        self.anchored=True

    def display(self, surface:Surface, mp:Coord, mu:bool, clicked_tile:Tile|None) -> bool:
        if isinstance(self.message, Surface):
            surface.blit(self.message, self.message_anchor)
        for tile in self.contains:
            clicked=tile.display(surface,mp,mu)
            if isinstance(clicked, Tile):
                self.selected=clicked
            elif clicked == False:
                self.selected=None
        if isinstance(self.selected,Tile):
            if not self.choose_tile:
                self.on_click(self.selected, self)
                return True
            else:
                if isinstance(clicked_tile,Tile):
                    self.on_click(self.selected, self, clicked_tile)
                    return True
        return False

class Pocket():
    def __init__(self, anchor:Coord, tile_size:Coord, inittiles:list[Tile]=[], clickfunc:None|Callable[[Tile, Tile], None]=None):
        self.contains:list[Tile]=inittiles
        self.anchor:Coord=anchor
        self.tile_size=tile_size[0]
        self.height=tile_size[1]
        self.width=0
        self.clickfunc=clickfunc #takes in the selected pocket tile, and the clicked board tile
        self.selected:Tile|None=None

    def display(self, surface:Surface, mp:Coord, mu:bool, clicked_tile:Tile|None):
        for tile in self.contains:
            selected=tile.display(surface,mp,mu)
            if isinstance(selected, Tile):
                self.selected=selected
            elif selected == False:
                self.selected=None
        if isinstance(self.selected, Tile) and isinstance(clicked_tile, Tile):
            self.clickfunc(self.selected, clicked_tile)

    def add(self, piece:Piece):
        self.contains.append(Tile(None,"empty",Rect((self.anchor[0]+self.tile_size*len(self.contains),self.anchor[1]),(self.tile_size,self.tile_size)),self))
        self.contains[-1].piece=piece
        piece.parent=self.contains[-1]
        self.width += self.tile_size

def wrap_text(text:str, max:int, font:font.Font) -> list[str]:
    words=text.split(" ")
    lines=[]
    temp=""
    for word in words:
        if word == "[RETURN]":
            lines.append(temp)
            temp=""
            continue
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
    def __init__(self, name:str, abstract:str, info:str, img:str, img_bg:str|Surface, covers:Literal["mode","piece"], links:list[Info]=None, internal_name:str=None):
        self.name=name
        self.internal_name=internal_name
        self.abstract=abstract
        self.body=info
        self.covers=covers
        if isinstance(img_bg, str):
            self.image:Surface=transform.scale(image.load(img_bg),INFO_IMG_DIM).convert_alpha()
        else:
            self.image:Surface=transform.scale(img_bg,INFO_IMG_DIM).convert_alpha()
        self.image.blit(transform.scale(image.load(img),INFO_IMG_DIM).convert_alpha(),(0,0))
        self.links=links
        self.link_names:list[str]=[]
        self.link_rects:list[Rect]=[]
        self.scroll_offset=0
        self.scrollable=False

    def set_links(self, links:list[Info]):
        self.links=links

    def construct(self):
        temp_link_list:list[int]=[]
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
            temp_link_list.append(num_in_row)
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
                click_rect=Rect(((INFO_MINI_DIM[0]+LINK_SPACING)*j+INFO_PAD_LR+INFO_BORDERS[0],0),INFO_MINI_DIM)
                if self.links[8*i+j].internal_name != None:
                    self.link_names.append(self.links[8*i+j].internal_name)
                else:
                    self.link_names.append(self.links[8*i+j].name)
                self.link_rects.append(click_rect)
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
            for j in range(temp_link_list[i]):
                self.link_rects[i*8+j].top=body_y_anchor
            body_y_anchor += components["link rows"][i].get_height()+INFO_PAD_SPLIT
        if self.display_base.get_height() > WIN_HEIGHT-100:
            self.scrollable=True

    def display(self, surface:Surface, ms:int, mp:Coord, md:bool) -> str|None:
        if ms != 0 and self.scrollable:
            self.scroll_offset = min(max(0, self.scroll_offset-25*ms), self.display_base.get_height()-50)
        surface.blit(self.display_base, (INFO_BORDERS[0],-self.scroll_offset))
        for hitbox in self.link_rects:
            temp=hitbox.copy()
            temp.top=hitbox.top-self.scroll_offset
            if hitbox.collidepoint((mp[0],mp[1]+self.scroll_offset)):
                draw.rect(surface,SELECT_COLOUR,temp,5)
                if md:
                    return self.link_names[self.link_rects.index(hitbox)]

print('Module "basic" (game foundations) loaded.')