'''Main game. Why would you want to import this?'''

import modes as m
import time as t
from modes import basic as b
from pygame import *
from collections.abc import Callable
from os.path import join

type Piece=b.Piece
type Tile=b.Tile
type Path=str
type Coord=tuple[int,int]
type BoardCoord=tuple[int,int]
type BoardLayout=list[list[Tile]]
type Colour=tuple[int,int,int]

display.init()
key.set_repeat(500,125)

class Game():
    def __init__(self):
        self.clock=time.Clock()
        #self.screen=display.set_mode((WIN_WIDTH,WIN_HEIGHT))
        self.screen=b.screen
        self.screen.fill((b.SHADES[0]))
        self.FPS=60
        self.running:bool=True
        self.menu:str="main"
        self.submenu:str="main"
        self.last_menu:str=None
        self.mode=None
        self.board:b.Board|None=None
        self.mode_infos:dict[str,b.Info]={}
        self.mode_info_buttons:list[Button]=[]
        self.mode_choose_buttons:list[Button]=[]
        self.piece_infos:dict[str,b.Info]={}
        self.piece_info_buttons:list[Button]=[]
        self.additional=None
        self.mode:Gamemode=None
        self.connect:bool=False
        self.incoming:str=''
        self.outgoing:str=''
        self.a_m_offset=0
        self.a_p_offset=0
        self.timer:tuple[int,int,int]=(0,0,0)
        self.selected:Tile|None=None
        self.prev_selected:Tile|None=None

    def begin(self):
        self.timer=(int(time_field.text),int(inc_field.text),int(del_field.text))
        self.mode.board.construct((10,b.WIN_HEIGHT/2-(self.mode.board.tile_dim[1]*self.mode.board.height)/2))
        self.mode.board.populate()
        self.mode.board.construct_img(b.CREAM_TILE,b.GREEN_TILE,None)

v=Game()

def contrast(colour:tuple[int,int,int]):
    brightness=0.299*colour[0] + 0.587*colour[1] + 0.114*colour[2]
    if brightness < 100:
        return (255,255,255)
    else:
        return (0,0,0)

class Gamemode():
    '''Placeholder class for properties of game modes so intellisense can check my code. Not supposed to be instantiated.'''
    def __init__(self):
        self.board:b.Board
        self.lock:Callable
        self.win:Callable
        self.info:b.Info
        self.piece_infos:list[b.Info]
        self.interpret:Callable
        self.local_play:bool
        self.online_play:bool
        raise RuntimeError("This is a utility placeholder class that is not supposed to be instantiated. This is why you shouldn't try.")

class Button():
    def __init__(self, centre:Coord, size:Coord, clickfunc:Callable, text:str, font:font.Font, text_colour:Colour=b.WHITE, colour:Color=b.GREENS[1], hover_colour:Color=b.GREENS[3], mousedown_colour:Colour=b.GREENS[2], shadow_colour:Colour=b.GREENS[0], toggle:bool=False, toggled_colour:Colour=None, toggled_shadow:Colour=None, unusable_colour:Colour=b.SHADES[3], unusable_shadow:Colour=b.SHADES[2]):
        self.shad_offset:int=int(0.15*size[1])
        self.rect=Rect(centre[0]-size[0]/2,centre[1]-size[1]/2,size[0],size[1])
        self.shad_rect=Rect(centre[0]-size[0]/2,centre[1]-size[1]/2+self.shad_offset,size[0],size[1])
        self.text=font.render(text,True,text_colour)
        self.text_pos=self.text.get_rect(center=centre).topleft
        self.centre=centre
        self.colour=colour
        self.hover_col=hover_colour
        self.md_col=mousedown_colour
        self.shad_col=shadow_colour
        self.toggled_colour= toggled_colour if toggled_colour != None else self.hover_col
        self.toggled_shad= toggled_shadow if toggled_shadow != None else self.shad_col
        self.on_click=clickfunc
        self.toggle=toggle
        self.unusable_col=unusable_colour
        self.unusable_shad=unusable_shadow

    def display(self, surface:Surface, mouse_pos:Coord, mouse_down:bool, mouse_up:bool, toggle:bool=False, unusable:bool=False):
        if self.rect.collidepoint(mouse_pos) and not unusable:
            if mouse_down:
                colour=self.md_col
            else:
                colour=self.hover_col
            if mouse_up and ((self.toggle and not toggle) or not toggle):
                self.on_click()
        else:
            colour=self.colour
        shad_col=self.shad_col
        if self.toggle and toggle:
            colour=self.toggled_colour
            shad_col=self.toggled_shad
        if unusable:
            colour=self.unusable_col
            shad_col=self.unusable_shad
        if (self.rect.collidepoint(mouse_pos) and mouse_down) or (self.toggle and toggle):
            draw.rect(surface,shad_col,self.rect,border_radius=b.ROUNDNESS)
            draw.rect(surface,colour,Rect(self.shad_rect.topleft,(self.shad_rect.width,self.shad_rect.height-self.shad_offset)),border_radius=b.ROUNDNESS)
            surface.blit(self.text,(self.text_pos[0],self.text_pos[1]+self.shad_offset))
        else:
            draw.rect(surface,shad_col,self.shad_rect,border_radius=b.ROUNDNESS)
            draw.rect(surface,colour,self.rect,border_radius=b.ROUNDNESS)
            surface.blit(self.text,self.text_pos)

class Text():
    def __init__(self, text:str, font:font.Font, colour:Colour, centre:Coord):
        self.raw_text=text
        self.text=font.render(text,True,colour)
        self.pos=self.text.get_rect(center=centre).topleft

    def display(self,surface:Surface):
        surface.blit(self.text,self.pos)

class Input():
    def __init__(self,colour:Colour,size:Coord,centre:Coord,font:font.Font,plc_text:str=None,control:Callable=lambda s: s):
        self.colour=colour
        self.text=plc_text
        self.centre=centre
        self.plc_text=plc_text
        self.font=font
        self.control=control
        self.active=False
        self.size=size
        self.rect=Rect(centre[0]-size[0]/2,centre[1]-size[1]/2,size[0],size[1])
        self.text_render:Surface=font.render(plc_text,True,b.WHITE)

    def display(self,surface:Surface,mp:Coord,md:bool,key:event.Event=None):
        if md:
            if self.rect.collidepoint(mp):
                self.active=True
            else:
                self.active=False
        draw.rect(surface,contrast(self.colour),Rect(self.rect.x-2,self.rect.y-2,self.rect.width+4,self.rect.height+4),border_radius=b.ROUNDNESS)
        draw.rect(surface,self.colour,self.rect,border_radius=b.ROUNDNESS)
        surface.blit(self.text_render,(self.rect.x+10,self.rect.y+self.rect.height/2-self.font.get_height()/2))
        if self.active:
            if t.time()%1 <= 0.5:
                draw.rect(surface,b.WHITE,Rect(self.rect.x+10+self.text_render.get_width(),self.rect.y+self.rect.height/2-self.font.get_height()/2,4,self.font.get_height()))
            if isinstance(key,event.Event):
                if key.key == K_BACKSPACE:
                    if len(self.text) == 1:
                        self.text=self.plc_text
                        self.text_render=self.font.render(self.plc_text,True,contrast(self.colour))
                    else:
                        self.text=self.control(self.text[:-1])
                        self.text_render=self.font.render(self.text,True,contrast(self.colour))
                elif key.key in [K_RETURN,K_TAB,K_ESCAPE]:
                    self.active=False
                else:
                    self.text += key.unicode
                    self.text=self.control(self.text)
                    self.text_render=self.font.render(self.text,True,contrast(self.colour))

def gen_change_menu(final:str, sub:str):
    def change_menu(final_menu=final, sub=sub):
        v.additional=None
        v.last_menu=v.menu
        v.menu=final_menu
        v.submenu=sub
    return change_menu

def gen_change_submenu(final:str):
    def change_submenu(final_menu=final):
        v.submenu=final_menu
        v.additional=None
    return change_submenu

def gen_set_gamemode(mode):
    def set_gamemode(mode=mode):
        v.mode=mode
    return set_gamemode

def gen_change_additional(final:str):
    def set_additional(final=final):
        v.additional=final
    return set_additional

def gen_change_single(var:str,final:str):
    def single_set(var=var,final=final):
        exec(f"{var}={final}")
    return single_set

def gen_change_many(values:dict):
    def many_set(values=values):
        for value in values:
            exec(f"{value}={values[value]}")
    return many_set

def back_button_func():
    if v.additional == None:
        v.menu=v.last_menu
        v.last_menu=None
    else:
        v.additional=None

def gen_compound_func(*funcs):
    def compound_func(funcs=funcs):
        for func in funcs:
            func()
    return compound_func

def int_check(input:str) -> str:
    try:
        temp=int(input)
        if temp > 999999999:
            return input[:-1]
        else:
            return str(temp)
    except:
        return input[:-1]
    
def gen_func(instr:str):
    def res_func(instr=instr):
        exec(instr)
    return res_func

font.init()
msrt_title=font.Font(join(b.FNT_IMG_DIR,"bold++.ttf"),100)
msrt_norm=font.Font(join(b.FNT_IMG_DIR,"bold+.ttf"),40)
msrt_small=font.Font(join(b.FNT_IMG_DIR,"bold.ttf"),30)
msrt_vsmall=font.Font(join(b.FNT_IMG_DIR,"thin.ttf"),20)

title_text=Text("Chess+",msrt_title,b.WHITE,(b.WIN_WIDTH/2,100))
almanac_text=Text("Almanac",msrt_title,b.WHITE,(b.WIN_WIDTH/2,80))
copyright_text=Text("© 2025 JEHR. Most rights not reserved.",msrt_vsmall,b.WHITE,(b.WIN_WIDTH/2,b.WIN_HEIGHT-50))
choose_mode_text=Text("Choose Mode",msrt_title,b.WHITE,(b.WIN_WIDTH/2,100))
timer_text=Text("Timer:",msrt_norm,b.WHITE,(b.WIN_WIDTH/6,350))
seconds_text=Text("Seconds",msrt_norm,b.WHITE,(2*b.WIN_WIDTH/6,430))
increment_text=Text("Increment",msrt_norm,b.WHITE,(3*b.WIN_WIDTH/6,430))
delay_text=Text("Delay",msrt_norm,b.WHITE,(4*b.WIN_WIDTH/6,430))

modes_button=Button((b.WIN_WIDTH/2,300),(800,100),gen_change_menu("modes","main"),"Select gamemode",msrt_norm)
almanac_button=Button((b.WIN_WIDTH/2,500),(800,100),gen_change_menu("almanac","modes"),"Almanac",msrt_norm)
back_button=Button((b.WIN_WIDTH/2,b.WIN_HEIGHT-90),(300,70),back_button_func,"Back",msrt_norm)
almanac_modes_button=Button((250,40),(150,35),gen_change_submenu("modes"),"Modes",msrt_small,toggle=True)
almanac_pieces_button=Button((250,100),(150,35),gen_change_submenu("pieces"),"Pieces",msrt_small,toggle=True)
multiplayer_button=Button((b.WIN_WIDTH/3,250),(400,70),gen_change_single("v.connect","True"),"Multiplayer",msrt_norm,toggle=True)
singleplayer_button=Button((2*b.WIN_WIDTH/3,250),(400,70),gen_change_single("v.connect","False"),"Singleplayer",msrt_norm,toggle=True)
to_game_button=Button((b.WIN_WIDTH/2,b.WIN_HEIGHT-190),(300,70),gen_compound_func(gen_change_menu("game",None),v.begin),"Play",msrt_norm)
m_next_button=Button((2*b.WIN_WIDTH/3,b.WIN_HEIGHT-90),(200,70),gen_func("v.a_m_offset += 1"),"Next",msrt_norm)
m_prev_button=Button((b.WIN_WIDTH/3,b.WIN_HEIGHT-90),(200,70),gen_func("v.a_m_offset -= 1"),"Prev",msrt_norm)
p_next_button=Button((2*b.WIN_WIDTH/3,b.WIN_HEIGHT-90),(200,70),gen_func("v.a_p_offset += 1"),"Next",msrt_norm)
p_prev_button=Button((b.WIN_WIDTH/3,b.WIN_HEIGHT-90),(200,70),gen_func("v.a_p_offset -= 1"),"Prev",msrt_norm)

time_field=Input(b.SHADES[1],(200,70),(2*b.WIN_WIDTH/6,350),msrt_small,"0",int_check)
inc_field=Input(b.SHADES[1],(200,70),(3*b.WIN_WIDTH/6,350),msrt_small,"0",int_check)
del_field=Input(b.SHADES[1],(200,70),(4*b.WIN_WIDTH/6,350),msrt_small,"0",int_check)

module_count=0
piece_count=0
for module in m.__all__:
    temp=__import__("modes",fromlist=[module])
    temp:Gamemode=getattr(temp,module)
    try:
        v.mode_infos[module]=temp.info
        v.mode_info_buttons.append(Button((b.WIN_WIDTH/2,200+module_count%5 *100),(b.INFO_BORDERS[1]-b.INFO_BORDERS[0],100),gen_change_additional(module),temp.info.name,msrt_norm))
        v.mode_choose_buttons.append(Button((b.WIN_WIDTH/2,200+module_count%5 *100),(b.INFO_BORDERS[1]-b.INFO_BORDERS[0],100),gen_compound_func(gen_change_submenu("players"),gen_set_gamemode(temp)),temp.info.name,msrt_norm))
    except AttributeError:
        v.mode_info_buttons.append(Button((b.WIN_WIDTH/2,200+module_count%5 *100),(b.INFO_BORDERS[1]-b.INFO_BORDERS[0],100),gen_change_additional(None),"Incorrect Format",msrt_norm))
    module_count += 1
    try:
        temp_i:b.Info=getattr(temp,"piece_infos")
        for piece in temp_i:
            if piece.name not in v.piece_infos:
                v.piece_infos[piece.name]=piece
                v.piece_info_buttons.append(Button((b.WIN_WIDTH/2,200+piece_count%5 *120),(b.INFO_BORDERS[1]-b.INFO_BORDERS[0],100),gen_change_additional(piece.name),piece.name,msrt_norm))
                piece_count += 1
    except AttributeError:
        v.piece_info_buttons.append(Button((b.WIN_WIDTH/2,200+piece_count%5 *100),(b.INFO_BORDERS[1]-b.INFO_BORDERS[0],100),gen_change_additional(None),"Incorrect Format",msrt_norm))
        piece_count += 1

md:bool=False
while v.running:
    v.screen.fill((b.SHADES[1]))
    mp:Coord=mouse.get_pos()
    mu:bool=False
    kp:event=None
    for e in event.get():
        if e.type == QUIT:
            v.running=False
        if e.type == MOUSEBUTTONDOWN:
            md=True
        if e.type == MOUSEBUTTONUP:
            md=False
            mu=True
        if e.type == KEYDOWN:
            kp=e

    if v.menu == "main":
        title_text.display(v.screen)
        modes_button.display(v.screen,mp,md,mu)
        almanac_button.display(v.screen,mp,md,mu)
        copyright_text.display(v.screen)
    elif v.menu == "almanac":
        if v.additional == None:
            almanac_text.display(v.screen)
            almanac_modes_button.display(v.screen,mp,md,mu,v.submenu == "modes")
            almanac_pieces_button.display(v.screen,mp,md,mu,v.submenu == "pieces")
            if v.submenu == "modes":
                for button in v.mode_info_buttons[v.a_m_offset*5:min(5,len(v.mode_info_buttons)-5*v.a_m_offset)+5*v.a_m_offset]:
                    button.display(v.screen,mp,md,mu)
                m_next_button.display(v.screen,mp,md,mu,unusable=5*(v.a_m_offset+1) >= len(v.mode_info_buttons))
                m_prev_button.display(v.screen,mp,md,mu,unusable=v.a_m_offset == 0)
            elif v.submenu == "pieces":
                for button in v.piece_info_buttons[v.a_p_offset*5:min(5,len(v.piece_info_buttons)-5*v.a_p_offset)+5*v.a_p_offset]:
                    button.display(v.screen,mp,md,mu)
                p_next_button.display(v.screen,mp,md,mu,unusable=5*(v.a_p_offset+1) >= len(v.piece_info_buttons))
                p_prev_button.display(v.screen,mp,md,mu,unusable=v.a_p_offset == 0)
        else:
            if v.submenu == "modes":
                v.mode_infos[v.additional].display(v.screen)
            elif v.submenu == "pieces":
                v.piece_infos[v.additional].display(v.screen)
        back_button.display(v.screen,mp,md,mu)
    elif v.menu == "modes":
        choose_mode_text.display(v.screen)
        if v.submenu == "main":
            for button in v.mode_choose_buttons[v.a_m_offset*5:min(5,len(v.mode_info_buttons)-5*v.a_m_offset)+5*v.a_m_offset]:
                button.display(v.screen,mp,md,mu)
            m_next_button.display(v.screen,mp,md,mu,unusable=5*(v.a_m_offset+1) >= len(v.mode_info_buttons))
            m_prev_button.display(v.screen,mp,md,mu,unusable=v.a_m_offset == 0)
        elif v.submenu == "players":
            singleplayer_button.display(v.screen,mp,md,mu,unusable=not v.mode.local_play,toggle=not v.connect)
            multiplayer_button.display(v.screen,mp,md,mu,unusable=not v.mode.online_play,toggle=v.connect)
            time_field.display(v.screen,mp,md,kp)
            seconds_text.display(v.screen)
            inc_field.display(v.screen,mp,md,kp)
            increment_text.display(v.screen)
            del_field.display(v.screen,mp,md,kp)
            delay_text.display(v.screen)
            to_game_button.display(v.screen,mp,md,mu)
            timer_text.display(v.screen)
        back_button.display(v.screen,mp,md,mu)
    
    elif v.menu == "game":
        v.prev_selected=v.selected
        temp=v.mode.board.display(v.screen,mp,mu)
        if temp != None or mu:
            v.selected=temp
        if mu:
            if v.selected != None and v.selected.move_target:
                v.prev_selected.piece.move_to(v.selected)
                v.prev_selected=None
                v.selected=None
            v.mode.board.scrub()
            if v.selected != None:
                if isinstance(v.selected.piece,b.Piece):
                    for tile in v.selected.piece.moves(v.mode.board):
                        v.mode.board.full_layout[tile[1]][tile[0]].move_target=True
                    for tile in v.selected.piece.capture_squares(v.mode.board):
                        v.mode.board.full_layout[tile[1]][tile[0]].capture_target=True
    
    display.update()
    v.clock.tick(60)