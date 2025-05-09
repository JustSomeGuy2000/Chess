import modes.basic as b
import modes.standard as s
from modes.wotk import no_win

def after_capture(game:b.Game, final_tile:b.Tile, captured:b.Piece):
    if isinstance(captured,s.WhitePawn):
        check_pos=(final_tile.boardpos[0],6)
    elif isinstance(captured,s.BlackPawn):
        check_pos=(final_tile.boardpos[0],1)
    elif isinstance(captured,s.WhiteBishop):
        if final_tile.colour == 0:
            check_pos=(5,7)
        else:
            check_pos=(2,7)
    elif isinstance(captured,s.BlackBishop):
        if final_tile.colour == 0:
            check_pos=(2,0)
        else:
            check_pos=(5,0)
    elif isinstance(captured,s.WhiteKnight):
        if final_tile.colour == 0:
            check_pos=(1,7)
        else:
            check_pos=(6,7)
    elif isinstance(captured,s.BlackKnight):
        if final_tile.colour == 0:
            check_pos=(6,0)
        else:
            check_pos=(1,0)
    elif isinstance(captured,s.WhiteRook):
        if final_tile.colour == 0:
            check_pos=(7,7)
        else:
            check_pos=(0,7)
    elif isinstance(captured,s.BlackRook):
        if final_tile.colour == 0:
            check_pos=(0,0)
        else:
            check_pos=(7,0)
    if isinstance(captured,s.WhiteQueen):
        check_pos=(3,7)
    elif isinstance(captured,s.BlackQueen):
        check_pos=(3,0)
    check_square=game.board.get(check_pos)
    if not isinstance(check_square.piece,b.Piece):
        check_square.set_piece(captured)

hidden=False
board=b.Board(8,8,["8","8","8","8","8","8","8","8"],piecesdict=s.STD_PCS_DICT,initpos=s.STD_INIT_POS)
local_play=True
online_play=False

piece_infos=[]
info=b.Info("Circe Chess","The path to the underworld is not a one-way street.","WIP",b.join(b.PCS_IMG_DIR,"bishop_b.png"),b.CREAM_TILE,"mode",[s.pawn_info,s.bishop_info,s.knight_info,s.rook_info,s.queen_info,s.king_info],"circe")
info.construct()

win=no_win