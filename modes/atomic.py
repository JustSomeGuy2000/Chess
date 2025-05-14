from modes.basic import *
import modes.standard as s
from pygame import *

hidden=False
board=Board(8,8,["8","8","8","8","8","8","8","8"],piecesdict=s.STD_PCS_DICT,initpos=s.STD_INIT_POS)
lock=Rules.lock
win=Rules.win

piece_infos=[]
lore="Boom boom! [I'll add some proper stuff later]"
info=Info("Atomic Chess","The nuclear age begins.",lore,join(OTR_IMG_DIR,"atomic.png"),GREEN_TILE,"mode",[s.pawn_info,s.bishop_info,s.knight_info,s.rook_info,s.queen_info,s.king_info],internal_name="atomic")
info.construct()

def after_capture(game:Game, final_tile:Tile, *args):
    for coord in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
        temp=game.board.get(final_tile.boardpos[0]-coord[0],final_tile.boardpos[1]-coord[1])
        if temp != False and isinstance(temp.piece,Piece) and not temp.piece.name == "Pawn":
            temp.piece=None
        final_tile.piece=None

after_move=s.after_move
interpret=Rules.interpret
local_play=True
online_play=False
