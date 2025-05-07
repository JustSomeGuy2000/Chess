from modes.basic import *
import modes.standard as s
from pygame import *

pcs_dict=copy.copy(s.STD_PCS_DICT)
init_pos=copy.copy(s.STD_INIT_POS)

class Duck(Piece):
    def __init__(self):
        super().__init__("Duck",0,"all",join(PCS_IMG_DIR,"duck.png"))

    def capture_squares(self, game, hypo = False):
        return []
    
    def moves(self, game):
        if game.board.submove == 1:
            return Movement.anywhere(game,self.parent.boardpos)
        else:
            return []
    
    def move_to(self, final, game = None):
        game.board.submove=2
        return super().move_to(final, game)

duck_info=Info("Duck","Just a little yellow guy.","The gimmick of the chess variant 'Duck Chess'. Can go anywhere and is controlled by either player. Cannot capture or be captured.",join(PCS_IMG_DIR,"duck.png"),CREAM_TILE,"piece",None)

pcs_dict["d"]=Duck
init_pos[3]="d7"

hidden=False
board=Board(8,8,["8","8","8","8","8","8","8","8"],piecesdict=pcs_dict,initpos=init_pos)
board.submove=0

def after_move(game:Game):
    '''Things to do after a move.'''
    for row in game.board.full_layout:
        for tile in row:
            if isinstance(tile.piece,(s.WhitePawn,s.BlackPawn)) and tile.piece.colour != game.board.turn:
                tile.piece.en_passantable=False
    if game.board.submove < 2:
        game.board.submove += 1
    else:
        game.board.progress_turn()
        if game.board.turn == 0:
            s.end_of_turn(game)
        game.board.submove=0

def capture_filter(captures, game):
    if game.board.submove == 0:
        return captures
    else:
        return []
    
def move_filter(captures, game):
    if game.board.submove == 0 or (game.board.submove == 1 and isinstance(game.selected.piece,Duck)):
        return captures
    else:
        return []

piece_infos=[duck_info]
lore="In a strange twist of fate, an invincible duck has wandered onto the battlefield?!"
info=Info("Duck Chess","Quack quack.",lore,join(PCS_IMG_DIR,"duck.png"),GREEN_TILE,"mode",[s.pawn_info,s.bishop_info,s.knight_info,s.rook_info,s.queen_info,s.king_info,duck_info],internal_name="duck")
info.construct()
duck_info.set_links([info])
duck_info.construct()

local_play=True
online_play=False