import modes.basic as b
import modes.standard as s
from pygame import *
from itertools import chain

font.init()
msrt_small=font.Font(b.join(b.FNT_IMG_DIR,"bold.ttf"),30)

def improve_choice(tile:b.Tile, options:b.OptionsBar):
    if options.contains.index(tile) == 0:
        options.parent.alignment="k"
    else:
        options.parent.alignment="b"
    options.parent.change_costume()

def no_win(game):
    return [],False,0

sprites:dict[int,dict[int|None,str]]={1:{None:'pawn'},2:{"b":'AD',"k":'WfD'},3:{"b":'bishop',"k":'knight'},4:{"b":'DB',"k":'NW'},5:{None:'rook'},6:{"b":'FLD',"k":'Nr'},7:{None:'BN'},8:{"b":'queen',"k":'C'},9:{None:'NrB'},10:{None:'NrR'},11:{None:'king'}}

class WhiteAdventurer(b.Piece):
    def __init__(self):
        super().__init__("Adventurer",1,0,b.join(b.PCS_IMG_DIR,"pawn_w.png"))
        self.level:int=1
        self.alignment:b.Literal["k","b",None]=None
        self.moved=False

    def moves(self, game):
        if game.board.turn != self.colour:
            return []
        if self.level == 1:
            if self.colour == 0:
                return s.WhitePawn.moves(self,game)
            else:
                return s.BlackPawn.moves(self,game)
        elif self.level == 2:
            if self.alignment == "k":
                temp=b.Movement.orthogonals((0,7,0,7),(1,1,1,1),self.parent.boardpos,game)
                if self.parent.boardpos[1] >= 2:
                    temp=chain(temp,[(self.parent.boardpos[0],self.parent.boardpos[1]-2)])
                if self.parent.boardpos[1] <= 5:
                    temp=chain(temp,[(self.parent.boardpos[0],self.parent.boardpos[1]+2)])
                return temp
            elif self.alignment == "b":
                return b.Movement.from_list(game, self.parent.boardpos,[(2,0),(-2,0),(0,2),(0,-2),(2,2),(-2,2),(2,-2),(-2,-2)])
        elif self.level == 3:
            if self.alignment == "k":
                return s.WhiteKnight.moves(self, game)
            elif self.alignment == "b":
                return s.WhiteBishop.moves(self, game)
        elif self.level == 4:
            if self.alignment == "k":
                return chain(s.WhiteKnight.moves(self,game),b.Movement.orthogonals((0,7,0,7),(1,1,1,1),self.parent.boardpos,game))
            elif self.alignment == "b":
                temp=[]
                for coord in [(0,2),(0,-2),(2,0),(-2,0)]:
                    target=(self.parent.boardpos[0]-coord[0],self.parent.boardpos[1]-coord[1])
                    if isinstance(game.board.get(target),b.Tile) and not isinstance(game.board.get(target).piece,b.Piece):
                        temp.append(target)
                return chain(s.WhiteBishop.moves(self,game),temp)
        elif self.level == 5:
            return s.WhiteRook.moves(self,game)
        elif self.level == 6:
            if self.alignment == "k":
                return b.Movement.l_shape((0,7,0,7),(s.inf,s.inf,s.inf,s.inf),self.parent.boardpos,game,2,1)
            elif self.alignment == "b":
                temp=[]
                for coord in [(1,1),(-1,1),(1,-1),(-1,-1),(2,0),(-2,0),(0,2),(0,-2),(1,3),(-1,3),(1,-3),(-1,-3),(3,1),(3,-1),(-3,1),(-3,-1)]:
                    target=(self.parent.boardpos[0]-coord[0],self.parent.boardpos[1]-coord[1])
                    if isinstance(game.board.get(target),b.Tile) and not isinstance(game.board.get(target).piece,b.Piece):
                        temp.append(target)
                return temp
        elif self.level == 7:
            return chain(s.WhiteBishop.moves(self,game),s.WhiteKnight.moves(self,game))
        elif self.level == 8:
            if self.alignment == "k":
                return chain(s.WhiteRook.moves(self,game),s.WhiteKnight.moves(self,game))
            elif self.alignment == "b":
                return s.WhiteQueen.moves(self,game)
        elif self.level == 9:
            return chain(s.WhiteBishop.moves(self,game),b.Movement.l_shape((0,7,0,7),(s.inf,s.inf,s.inf,s.inf),self.parent.boardpos,game,2,1))
        elif self.level == 10:
            return chain(s.WhiteRook.moves(self,game),b.Movement.l_shape((0,7,0,7),(s.inf,s.inf,s.inf,s.inf),self.parent.boardpos,game,2,1))
        else:
            return s.WhiteKing.moves(self,game)
    
    def capture_squares(self, game, hypo = False):
        if game.board.turn != self.colour:
            return []
        if self.level == 1:
            if self.colour == 0:
                return s.WhitePawn.capture_squares(self,game,hypo)
            else:
                return s.BlackPawn.capture_squares(self,game,hypo)
        elif self.level == 2:
            if self.alignment == "k":
                temp=b.Capture.orthogonals((0,7,0,7),(1,1,1,1),self.parent.boardpos,game,self.colour,hypo)
                target=(self.parent.boardpos[0],self.parent.boardpos[1]-2)
                if self.parent.boardpos[1] >= 2 and isinstance(game.board.get(target),b.Tile) and isinstance(game.board.get(target).piece,b.Piece):
                    temp=chain(temp,[target])
                target=(self.parent.boardpos[0],self.parent.boardpos[1]+2)
                if self.parent.boardpos[1] <= 5 and isinstance(game.board.get(target),b.Tile) and isinstance(game.board.get(target).piece,b.Piece):
                    temp=chain(temp,[target])
                return temp
            elif self.alignment == "b":
                return b.Capture.from_list(game, self.parent.boardpos, [(2,0),(-2,0),(0,2),(0,-2),(2,2),(-2,2),(2,-2),(-2,-2)], self.colour,hypo)
        elif self.level == 3:
            if self.alignment == "k":
                return s.WhiteKnight.capture_squares(self, game, hypo)
            elif self.alignment == "b":
                return s.WhiteBishop.capture_squares(self, game, hypo)
        elif self.level == 4:
            if self.alignment == "k":
                return chain(s.WhiteKnight.capture_squares(self,game,hypo),b.Capture.orthogonals((0,7,0,7),(1,1,1,1),self.parent.boardpos,game,self.colour,hypo))
            elif self.alignment == "b":
                temp=[]
                for coord in [(0,2),(0,-2),(2,0),(-2,0)]:
                    target=(self.parent.boardpos[0]-coord[0],self.parent.boardpos[1]-coord[1])
                    if isinstance(game.board.get(target),b.Tile) and isinstance(game.board.get(target).piece,b.Piece):
                        temp.append(target)
                return chain(s.WhiteBishop.capture_squares(self,game,hypo),temp)
        elif self.level == 5:
            return s.WhiteRook.capture_squares(self,game,hypo)
        elif self.level == 6:
            if self.alignment == "k":
                return b.Capture.l_shape((0,7,0,7),(s.inf,s.inf,s.inf,s.inf),self.parent.boardpos,game,2,1,self.colour,hypo)
            elif self.alignment == "b":
                temp=[]
                for coord in [(1,1),(-1,1),(1,-1),(-1,-1),(2,0),(-2,0),(0,2),(0,-2),(1,3),(-1,3),(1,-3),(-1,-3),(3,1),(3,-1),(-3,1),(-3,-1)]:
                    target=(self.parent.boardpos[0]-coord[0],self.parent.boardpos[1]-coord[1])
                    if isinstance(game.board.get(target),b.Tile) and isinstance(game.board.get(target).piece,b.Piece):
                        temp.append(target)
                return temp
        elif self.level == 7:
            return chain(s.WhiteBishop.capture_squares(self,game,hypo),s.WhiteKnight.capture_squares(self,game,hypo))
        elif self.level == 8:
            if self.alignment == "k":
                return chain(s.WhiteRook.capture_squares(self,game,hypo),s.WhiteKnight.capture_squares(self,game,hypo))
            elif self.alignment == "b":
                return s.WhiteQueen.capture_squares(self,game,hypo)
        elif self.level == 9:
            return chain(s.WhiteBishop.capture_squares(self,game,hypo),b.Capture.l_shape((0,7,0,7),(s.inf,s.inf,s.inf,s.inf),self.parent.boardpos,game,2,1,self.colour,hypo))
        elif self.level == 10:
            return chain(s.WhiteRook.capture_squares(self,game,hypo),b.Capture.l_shape((0,7,0,7),(s.inf,s.inf,s.inf,s.inf),self.parent.boardpos,game,2,1,self.colour,hypo))
        else:
            return s.WhiteKing.capture_squares(self,game,hypo)
    
    def move_to(self, final, game = None):
        if (isinstance(final.piece,b.Piece) and final.piece.level >= self.level/2) or (final.boardpos[1] <= self.parent.boardpos[1]-5):
            if self.level in [1,5,7]:
                if self.colour == 0:
                    wotk=b.Tile(None,"empty",Rect(0,0,0,0),self,piece=s.WhiteKnight())
                    wotb=b.Tile(None,"empty",Rect(0,0,0,0),self,piece=s.WhiteBishop())
                else:
                    wotk=b.Tile(None,"empty",Rect(0,0,0,0),self,piece=s.BlackKnight())
                    wotb=b.Tile(None,"empty",Rect(0,0,0,0),self,piece=s.BlackBishop())
                align=b.OptionsBar(self,[wotk,wotb],improve_choice)
                self.parent.propagate_options(align)
            elif self.level in [4,6,8]:
                self.alignment=None
            self.level += 1
            self.change_costume()
        self.has_moved=True
        return b.Piece.move_to(self,final, game)
    
    def change_costume(self):
        try:
            img=sprites[self.level][self.alignment]
            if self.colour == 0:
                img += "_w"
            else:
                img += "_b"
            self.image=transform.scale(image.load(b.join(b.PCS_IMG_DIR,f"{img}.png")),b.STD_TILEDIM).convert_alpha()
        except:
            try:
                self.image=transform.scale(msrt_small.render(sprites[self.level][self.alignment],True,b.WHITE if self.colour == 0 else b.BLACK),b.STD_TILEDIM).convert_alpha()
            except:
                pass
    
class BlackAdventurer(b.Piece):
    def __init__(self):
        super().__init__("Adventurer",1,1,b.join(b.PCS_IMG_DIR,"pawn_b.png"),True)
        self.level:int=1
        self.alignment:b.Literal["k","b",None]=None
        self.moved=False
        self.moves=s.partial(WhiteAdventurer.moves,self)
        self.capture_squares=s.partial(WhiteAdventurer.capture_squares,self)
        self.move_to=s.partial(WhiteAdventurer.move_to,self)
        self.change_costume=s.partial(WhiteAdventurer.change_costume,self)

hidden=False
piecesdict={"a":BlackAdventurer,"A":WhiteAdventurer}
initpos=["aaaaaaaa","aaaaaaaa","8","8","8","8","AAAAAAAA","AAAAAAAA"]
board=b.Board(8,8,["8","8","8","8","8","8","8","8"],piecesdict=piecesdict,initpos=initpos)
local_play=True
online_play=False

adv_info=b.Info("Adventurer","Oh, the places you'll go!","WIP",b.join(b.PCS_IMG_DIR,"pawn_w.png"),b.GREEN_TILE,"piece",None)

lore="WIP"

info=b.Info("Way of the Knight (2-path)","This is to chess what Mamono Sweeper is to Minesweeper.",lore,b.join(b.PCS_IMG_DIR,"knight_w.png"),b.GREEN_TILE,"mode",[adv_info],"wotk")
info.construct()
adv_info.set_links([info])
adv_info.construct()
piece_infos=[adv_info]

win=no_win