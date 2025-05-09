import modes.standard as s
import modes.basic as b
import random as r
from functools import partial
from itertools import chain

knights:dict[int,list[int]]={0:[0,1],1:[0,2],2:[0,3],3:[0,4],4:[1,2],5:[1,3],6:[1,4],7:[2,3],8:[2,4],9:[3,4]}

def fischer_pair(pos:int, piece:str, fromlist:list[int], board:b.Board):
    board.get(fromlist[pos],7).set_piece(s.STD_PCS_DICT[piece.upper()]())
    board.get(fromlist[pos],0).set_piece(s.STD_PCS_DICT[piece.lower()]())

def game_start(game:b.Game):
    seed=r.randint(0,959)
    empty=[0,1,2,3,4,5,6,7]
    seed, b1=divmod(seed,4)
    fischer_pair(b1*2+1,"b",empty,game.board)
    seed, b2=divmod(seed,4)
    fischer_pair(b2*2,"b",empty,game.board)
    empty.pop(b1*2+1)
    if b1 < b2:
        empty.pop(b2*2-1)
    else:
        empty.pop(b2*2)
    seed, q=divmod(seed, 6)
    fischer_pair(q,"q",empty,game.board)
    empty.pop(q)
    fischer_pair(knights[seed][0],"n",empty,game.board)
    fischer_pair(knights[seed][1],"n",empty,game.board)
    empty.pop(knights[seed][0])
    empty.pop(knights[seed][1]-1)
    fischer_pair(0,"r",empty,game.board)
    game.board.left_rook=empty[0]
    fischer_pair(1,"k",empty,game.board)
    fischer_pair(2,"r",empty,game.board)
    game.board.right_rook=empty[2]

class WhiteFischerKing(b.Piece):
    def __init__(self):
        b.Piece.__init__(self,"King",s.inf,0,b.join(b.PCS_IMG_DIR,"king_w.png"),True)
        self.has_moved=False
        self.capture_squares=partial(s.WhiteKing.capture_squares,self)

    def moves(self, game):
        temp=b.Movement.to_list(chain(b.Movement.diagonals((0,7,0,7),(1,1,1,1),self.parent.boardpos,game),b.Movement.orthogonals((0,7,0,7),(1,1,1,1),self.parent.boardpos,game))) 
        self.parent.piece=None
        capture_squares=b.Rules.gen_capture_squares(game,pieces)
        for tile in capture_squares:
            if tile in temp:
                temp.remove(tile)
        self.parent.piece=self
        if game.board.turn == self.colour and not self.has_moved:
            pieces:list[b.Piece]=[]
            for row in game.board.full_layout:
                for tile in row:
                    if tile and tile.piece.colour != self.colour:
                        pieces.append(tile.piece)
            right=[self.parent.boardpos,(self.parent.boardpos[0]+1,self.parent.boardpos[1]),(self.parent.boardpos[0]+2,self.parent.boardpos[1]),(self.parent.boardpos[0]+3,self.parent.boardpos[1])]
            left=[self.parent.boardpos,(self.parent.boardpos[0]-1,self.parent.boardpos[1]),(self.parent.boardpos[0]-2,self.parent.boardpos[1]),(self.parent.boardpos[0]-3,self.parent.boardpos[1]),(self.parent.boardpos[0]-4,self.parent.boardpos[1])]
            for direction in [right,left]:
                potential=game.board.get(direction[-1]).piece
                if True not in [bool(game.board.get(tile)) for tile in direction[1:-1]] and True not in [(tile in capture_squares) for tile in direction[:-1]] and isinstance(potential,b.Piece) and potential.name == "Rook" and potential.colour == self.colour and not potential.has_moved:
                    temp=chain(temp,[direction[2]])
        return temp
    
    def move_to(self, final, game):
        return super().move_to(final, game)

class BlackFischerKing():
    def __init__(self):
        b.Piece.__init__(self,"King",s.inf,1,b.join(b.PCS_IMG_DIR,"king_b.png"),True)
        self.has_moved=False
        self.capture_squares=partial(s.WhiteKing.capture_squares,self)
        self.moves=partial(WhiteFischerKing.moves,self)
        self.move_to=partial(WhiteFischerKing.move_to,self)

pcsdict=b.copy.copy(s.STD_PCS_DICT)
pcsdict["k"]=BlackFischerKing
pcsdict["K"]=WhiteFischerKing
initpos=["8","pppppppp","8","8","8","8","PPPPPPPP","8"]
board=b.Board(8,8,["8","8","8","8","8","8","8","8"],piecesdict=pcsdict,initpos=initpos)

hidden=False
local_play=True
online_play=False

info=b.Info("Fischer Random Chess","Who needs memorising openings?","WIP",b.join(b.PCS_IMG_DIR,"amalgam_w.png"),b.CREAM_TILE,"mode",[s.pawn_info,s.bishop_info,s.knight_info,s.rook_info,s.queen_info,s.king_info],"fischer_random")
info.construct()
piece=infos=[]