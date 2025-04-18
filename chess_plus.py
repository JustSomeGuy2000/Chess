'''Main game. Why would you want to import this?'''

from modes import *
from modes.basic import *
import modes.standard as s

display.init()

class Game():
    def __init__(self):
        self.clock=time.Clock()
        #self.screen=display.set_mode((WIN_WIDTH,WIN_HEIGHT))
        self.screen=screen
        self.screen.fill((SHADES[0]))
        self.FPS=60
        self.running:bool=True
        self.menu:str="main"
        self.submenu:str="main"
        self.last_menu:str=None
        self.mode=None
        self.almanac_state:Info|None=None
v=Game()

class Button():
    def __init__(self, centre:Coord, size:Coord, clickfunc:Callable, text:str, font:font.Font, text_colour:Colour=WHITE, colour:Color=GREENS[1], hover_colour:Color=GREENS[3], mousedown_colour:Colour=GREENS[2], shadow_colour:Colour=GREENS[0], toggle:bool=False, toggled_colour:Colour=None, toggled_shadow:Colour=None, unusable_colour:Colour=SHADES[3], unusable_shadow:Colour=SHADES[2]):
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
            draw.rect(surface,shad_col,self.rect,border_radius=ROUNDNESS)
            draw.rect(surface,colour,self.shad_rect,border_radius=ROUNDNESS)
            surface.blit(self.text,(self.text_pos[0],self.text_pos[1]+self.shad_offset))
        else:
            draw.rect(surface,shad_col,self.shad_rect,border_radius=ROUNDNESS)
            draw.rect(surface,colour,self.rect,border_radius=ROUNDNESS)
            surface.blit(self.text,self.text_pos)

class Text():
    def __init__(self, text:str, font:font.Font, colour:Colour, centre:Coord):
        self.raw_text=text
        self.text=font.render(text,True,colour)
        self.pos=self.text.get_rect(center=centre).topleft

    def display(self,surface:Surface):
        surface.blit(self.text,self.pos)

def gen_change_menu(final:str, sub:str):
    def change_menu(final_menu=final, sub=sub):
        v.last_menu=v.menu
        v.menu=final_menu
        v.submenu=sub
    return change_menu

def gen_change_submenu(final:str):
    def change_submenu(final_menu=final):
        v.submenu=final_menu
    return change_submenu

def gen_set_gamemode(mode:str):
    def set_gamemode(mode=mode):
        return __import__(mode)
    return set_gamemode

def back_button_func():
    v.menu=v.last_menu
    v.last_menu=None

font.init()
msrt_title=font.Font(join(FNT_IMG_DIR,"bold++.ttf"),100)
msrt_norm=font.Font(join(FNT_IMG_DIR,"bold+.ttf"),40)
msrt_small=font.Font(join(FNT_IMG_DIR,"bold.ttf"),30)
msrt_vsmall=font.Font(join(FNT_IMG_DIR,"thin.ttf"),20)

title_text=Text("Chess+",msrt_title,WHITE,(WIN_WIDTH/2,100))
almanac_text=Text("Almanac",msrt_title,WHITE,(WIN_WIDTH/2,80))
copyright_text=Text("© 2025 JEHR. Most rights not reserved.",msrt_vsmall,WHITE,(WIN_WIDTH/2,WIN_HEIGHT-50))

modes_button=Button((WIN_WIDTH/2,300),(800,100),gen_change_menu("modes","main"),"Select gamemode",msrt_norm)
almanac_button=Button((WIN_WIDTH/2,500),(800,100),gen_change_menu("almanac","modes"),"Almanac",msrt_norm)
back_button=Button((WIN_WIDTH/2,WIN_HEIGHT-100),(300,70),back_button_func,"Back",msrt_norm)
almanac_modes_button=Button((250,40),(150,35),gen_change_submenu("modes"),"Modes",msrt_small,toggle=True)
almanac_pieces_button=Button((250,100),(150,35),gen_change_submenu("pieces"),"Pieces",msrt_small,toggle=True)

md:bool=False
while v.running:
    v.screen.fill((SHADES[0]))
    mouse_pos:Coord=mouse.get_pos()
    mu:bool=False
    for e in event.get():
        if e.type == QUIT:
            v.running=False
        if e.type == MOUSEBUTTONDOWN:
            md=True
        if e.type == MOUSEBUTTONUP:
            md=False
            mu=True

    if v.menu == "main":
        title_text.display(v.screen)
        modes_button.display(v.screen,mouse_pos,md,mu)
        almanac_button.display(v.screen,mouse_pos,md,mu)
        copyright_text.display(v.screen)
    elif v.menu == "almanac":
        almanac_text.display(v.screen)
        back_button.display(v.screen,mouse_pos,md,mu)
        almanac_modes_button.display(v.screen,mouse_pos,md,mu,v.submenu == "modes")
        almanac_pieces_button.display(v.screen,mouse_pos,md,mu,v.submenu == "pieces")
    
    display.update()
    v.clock.tick(60)