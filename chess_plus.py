'''Main game. Why would you want to import this?'''

from modes.basic import *

display.init()

class Game():
    def __init__(self):
        self.clock=time.Clock()
        self.screen=display.set_mode((WIN_WIDTH,WIN_HEIGHT))
        self.screen.fill((SHADES[0]))
        self.FPS=60
        self.running:bool=True
        self.menu:Literal["main","modes","almanac","game","settings"]="main"
        self.mode=None
        self.almanac_state:Info|None=None

def gen_change_menu(final:str):
    def change_menu(final_menu=final):
        v.menu=final_menu
    return change_menu

class Button():
    def __init__(self, centre:Coord, size:Coord, clickfunc:Callable, text:str, font:font.Font, text_colour:Colour=WHITE, colour:Color=GREENS[1], hover_colour:Color=GREENS[3], mousedown_colour:Colour=GREENS[2], shadow_colour:Colour=GREENS[0]):
        self.rect=Rect(centre[0]-size[0]/2,centre[1]-size[1]/2,size[0],size[1])
        self.shad_rect=Rect(centre[0]-size[0]/2,centre[1]-size[1]/2+15,size[0],size[1])
        self.text=font.render(text,True,text_colour)
        self.text_pos=self.text.get_rect(center=centre).topleft
        self.centre=centre
        self.colour=colour
        self.hover_col=hover_colour
        self.md_col=mousedown_colour
        self.shad_col=shadow_colour
        self.on_click=clickfunc

    def display(self, surface:Surface, mouse_pos:Coord, mouse_down:bool, mouse_up:bool):
        if self.rect.collidepoint(mouse_pos):
            if mouse_down:
                colour=self.md_col
            else:
                colour=self.hover_col
            if mouse_up:
                self.on_click()
        else:
            colour=self.colour
        draw.rect(surface,self.shad_col,self.shad_rect,border_radius=ROUNDNESS)
        draw.rect(surface,colour,self.rect,border_radius=ROUNDNESS)
        surface.blit(self.text,self.text_pos)

class Text():
    def __init__(self, text:str, font:font.Font, colour:Colour, centre:Coord):
        self.raw_text=text
        self.text=font.render(text,True,colour)
        self.pos=self.text.get_rect(center=centre).topleft

    def display(self,surface:Surface):
        surface.blit(self.text,self.pos)

v=Game()

font.init()
msrt_title=font.Font(join(FNT_IMG_DIR,"bold++.ttf"),100)
msrt_norm=font.Font(join(FNT_IMG_DIR,"bold+.ttf"),40)
msrt_vsmall=font.Font(join(FNT_IMG_DIR,"thin.ttf"),20)

title_text=Text("Chess+",msrt_title,WHITE,(WIN_WIDTH/2,100))
copyright_text=Text("© 2025 JEHR. Some rights reserved.",msrt_vsmall,WHITE,(WIN_WIDTH/2,WIN_HEIGHT-50))

modes_button=Button((WIN_WIDTH/2,300),(800,100),gen_change_menu("modes"),"Select gamemode",msrt_norm)
almanac_button=Button((WIN_WIDTH/2,500),(800,100),gen_change_menu("almanac"),"Almanac",msrt_norm)
while v.running:
    mouse_pos:Coord=mouse.get_pos()
    md:bool=False
    mu:bool=False
    for e in event.get():
        if e.type == QUIT:
            v.running=False
        if e.type == MOUSEBUTTONDOWN:
            md=True
        if e.type == MOUSEBUTTONUP:
            mu=True

    if v.menu == "main":
        title_text.display(v.screen)
        modes_button.display(v.screen,mouse_pos,md,mu)
        almanac_button.display(v.screen,mouse_pos,md,mu)
        copyright_text.display(v.screen)
    
    display.update()
    v.clock.tick(60)