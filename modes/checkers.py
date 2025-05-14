import modes.basic as b
import modes.standard as s
from pygame import *
from itertools import chain

'''red_circle=Surface(b.STD_TILEDIM,SRCALPHA,32)
draw.circle(red_circle,(200,25,25),(b.STD_TILEDIM[0]/2,b.STD_TILEDIM[1]/2),b.STD_TILEDIM[0]/2)
white_circle=Surface(b.STD_TILEDIM,SRCALPHA,32)
draw.circle(white_circle,(255,255,255),(b.STD_TILEDIM[0]/2,b.STD_TILEDIM[1]/2),b.STD_TILEDIM[0]/2)'''

def after_move(game:b.Game):
    '''Things to do after a move.'''
    if game.board.end_turn:
        game.board.progress_turn()
    else:
        game.board.select_again.selected=True
        game.selected=game.board.select_again

def win(game:b.Game):
    if not game.board.end_turn:
        return [], False, -1
    real_turn=game.board.turn
    all_light=game.board.get_matching(lambda t: True if isinstance(t.piece,b.Piece) and t.piece.colour == 0 else False)
    all_dark=game.board.get_matching(lambda t: True if isinstance(t.piece,b.Piece) and t.piece.colour == 1 else False)
    all_light_moves=[]
    all_dark_moves=[]
    game.board.cs_storage=[]
    game.board.turn=0
    for tile in all_light:
        all_light_moves.extend(tile.piece.moves(game))
        all_light_moves.extend(tile.piece.capture_squares(game))
    game.board.turn=1
    for tile in all_dark:
        all_dark_moves.extend(tile.piece.moves(game))
        all_dark_moves.extend(tile.piece.capture_squares(game))
    game.board.turn=real_turn
    for tile in game.board.get_matching(lambda t: True if isinstance(t.piece,b.Piece) and t.piece.belongs_to(game.board.turn) else False):
        game.board.cs_storage.extend(tile.piece.capture_squares(game))
    if all_light == [] or all_light_moves == []:
        return [], True, 0
    elif all_dark == [] or all_dark_moves == []:
        return [], True, 1
    else:
        return [], False, -1

class LightMan(b.Piece):
    def __init__(self):
        super().__init__("Man",1,0,b.join(b.PCS_IMG_DIR,"pawn_w.png"))
        self.y_step=1
        if self.colour == 0:
            self.y_step=-1

    def moves(self, game):
        if not self.belongs_to(game.board.turn) or (isinstance(game.board.select_again, b.Tile) and self != game.board.select_again) or (game.board.cs_storage != [] and self.belongs_to(game.board.turn)):
            return []
        if self.colour == 0:
            return chain(b.Movement.diagonal(-1,self.y_step,0,0,1,self.parent.boardpos,game),b.Movement.diagonal(1,self.y_step,7,0,1,self.parent.boardpos,game))
        else:
            return chain(b.Movement.diagonal(-1,self.y_step,0,7,1,self.parent.boardpos,game),b.Movement.diagonal(1,self.y_step,7,7,1,self.parent.boardpos,game))
    
    def capture_squares(self, game, hypo = False):
        if not self.belongs_to(game.board.turn) or (isinstance(game.board.select_again, b.Tile) and self.parent != game.board.select_again):
            return []
        self.prev_square=self.parent.boardpos
        for x_step in [1,-1]:
            cap_target=game.board.get(self.parent.boardpos[0]+x_step,self.parent.boardpos[1]+self.y_step)
            mov_target=game.board.get(self.parent.boardpos[0]+(2*x_step),self.parent.boardpos[1]+(2*self.y_step))
            if isinstance(cap_target,b.Tile) and isinstance(mov_target,b.Tile) and isinstance(cap_target.piece,b.Piece) and not isinstance(mov_target.piece,b.Piece) and not cap_target.piece.belongs_to(self.colour):
                game.board.teleport.append((cap_target.boardpos,mov_target.boardpos))
                yield cap_target.boardpos
    
    def move_to(self, final, game):
        b.Piece.move_to(self, final, game)
        y_step=-1
        if self.colour == 0:
            y_step=1
        average=divmod((self.parent.boardpos[0]+self.prev_square[0]),2)
        game.board.end_turn=True
        game.board.select_again=None
        if average[1] == 0:
            game.board.get(average[0],self.parent.boardpos[1]+y_step).piece=None
            if [a for a in self.capture_squares(game)] != []:
                game.board.end_turn=False
                game.board.select_again=self.parent
        if (self.colour == 0 and self.parent.boardpos[1] == 0) or (self.colour == 1 and self.parent.boardpos[1] == 7):
            if self.colour == 0:
                temp=LightKing()
            else:
                temp=DarkKing()
            self.parent.piece=temp
            temp.parent=final
            self.parent=None
        self.cs_storage=[]

class DarkMan(b.Piece):
    def __init__(self):
        super().__init__("Man",1,1,b.join(b.PCS_IMG_DIR,"pawn_b.png"))
        self.moves=s.partial(LightMan.moves,self)
        self.capture_squares=s.partial(LightMan.capture_squares,self)
        self.move_to=s.partial(LightMan.move_to,self)
        self.y_step=1
        if self.colour == 0:
            self.y_step=-1

class LightKing(b.Piece):
    def __init__(self):
        super().__init__("King",s.inf,0,b.join(b.PCS_IMG_DIR,"king_w.png"))

    def moves(self, game):
        if not self.belongs_to(game.board.turn) or (isinstance(game.board.select_again, b.Tile) and self != game.board.select_again) or game.board.cs_storage != []:
            return []
        return b.Movement.diagonals((0,7,0,7),(1,1,1,1),self.parent.boardpos,game)
    
    def capture_squares(self, game, hypo = False):
        if not self.belongs_to(game.board.turn) or (isinstance(game.board.select_again, b.Tile) and self != game.board.select_again):
            return []
        self.prev_square=self.parent.boardpos
        for y_step in [1,-1]:
            for x_step in [1,-1]:
                cap_target=game.board.get(self.parent.boardpos[0]+x_step,self.parent.boardpos[1]+y_step)
                mov_target=game.board.get(self.parent.boardpos[0]+(2*x_step),self.parent.boardpos[1]+(2*y_step))
                if isinstance(cap_target,b.Tile) and isinstance(mov_target,b.Tile) and isinstance(cap_target.piece,b.Piece) and not isinstance(mov_target.piece,b.Piece) and not cap_target.piece.belongs_to(self.colour):
                    game.board.teleport.append((cap_target.boardpos,mov_target.boardpos))
                    yield cap_target.boardpos
    
    def move_to(self, final, game):
        b.Piece.move_to(self, final, game)
        y_step=int(b.ma.copysign(1,self.prev_square[1]-self.parent.boardpos[1]))
        if self.colour == 0:
            y_step=1
        average=divmod((self.parent.boardpos[0]+self.prev_square[0]),2)
        game.board.end_turn=True
        game.board.select_again=None
        if average[1] == 0:
            game.board.get(average[0],self.parent.boardpos[1]+y_step).piece=None
            if [a for a in self.capture_squares(game)] != []:
                game.board.end_turn=False
                game.board.select_again=self.parent
    
class DarkKing(b.Piece):
    def __init__(self):
        super().__init__("Man",s.inf,1,b.join(b.PCS_IMG_DIR,"king_b.png"))
        self.moves=s.partial(LightKing.moves,self)
        self.capture_squares=s.partial(LightKing.capture_squares,self)
        self.move_to=s.partial(LightKing.move_to,self)

piecesdict={"m":DarkMan,"M":LightMan,"k":DarkKing,"K":LightKing}
initpos=["1m1m1m1m","m1m1m1m1","1m1m1m1m","8","8","M1M1M1M1","1M1M1M1M","M1M1M1M1"]
board=b.Board(8,8,["8","8","8","8","8","8","8","8"],piecesdict=piecesdict,initpos=initpos)
board.turn=1
board.end_turn=True
board.select_again=None
board.turn_number=1
board.cs_storage=[]

king_info=b.Info("King (Checkers)","Way more useful than a king in chess","WIP",b.join(b.PCS_IMG_DIR,"king_w.png"),b.CREAM_TILE,"piece")
man_info=b.Info("Man","Imagine all your pieces being this weakling.","WIP",b.join(b.PCS_IMG_DIR,"pawn_w.png"),b.CREAM_TILE,"piece")
info=b.Info("Checkers","Surprisingly strategic.","WIP",b.join(b.PCS_IMG_DIR,"king_w.png"),b.CREAM_TILE,"mode",[man_info,king_info],"checkers")
info.construct()
king_info.set_links([info])
man_info.set_links([info])
king_info.construct()
man_info.construct()
piece_infos=[man_info,king_info]

hidden=False
online_play=False
local_play=True