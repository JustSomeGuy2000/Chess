'''Gamemode: occidental standard chess'''

import itertools
if __name__ == "__main__":
    from basic import *
else:
    from modes.basic import *
from pygame import *
from math import inf
m=Movement
c=Capture
font.init()

class WhitePawn(Piece):
    def __init__(self):
        super().__init__("Pawn",1,0,join(PCS_IMG_DIR,"pawn_w.png"))
        self.en_passantable=False
        self.moved=False

    def moves(self, board:Board) -> list[BoardCoord]:
        '''Every square the piece can move to (excluding captures). Most of the time, a few calls to Movement functions are enough.'''
        if not self.moved:
            move_spaces=2
        else:
            move_spaces=1
        return m.forward(board.height,move_spaces,self.parent.boardpos,board)

    def capture_squares(self, board:Board, hypo:bool=False) -> list[BoardCoord]:
        '''Every square the piece can capture on, factoring in the board. If hypo is True, returns every square the piece can capture on hypothetically.'''
        temp=c.compound(0,board.height-1,1,1,self.parent.boardpos,c.left,c.forward,board)+c.compound(board.width,board.height,1,1,self.parent.boardpos,c.right,c.forward,board)
        if 0 < self.parent.boardpos[0] < 8:
            left=True
            right=True
        elif self.parent.boardpos[0] == 0:
            left=False
            right=True
        else:
            left=True
            right=False
        if left:
            target=board.full_layout[self.parent.boardpos[1]][self.parent.boardpos[0]-1].piece
            if target.name == "Pawn" and target.en_passantable:
                pass
        if right:
            target=board.full_layout[self.parent.boardpos[1]][self.parent.boardpos[0]+1].piece
            if target.name == "Pawn" and target.en_passantable:
                pass
        return temp

    def move_to(self, final:Tile, board:Board|None=None) -> Piece:
        '''Move to a Tile. Set its parent's piece to None and set the final Tile's piece to this.'''
        final.piece=self
        self.moved=True
        if self.en_passantable:
            self.en_passantable=False
        elif final.boardpos[1] == self.parent.boardpos[1]+2:
            self.en_passantable=True
        self.parent.piece=None
    
    def lines_of_sight(self, board:Board) -> list[Generator]:
        '''Returns a list of generators, each representing a line of sight of the piece.'''
        return [c.compound(0,board.height-1,1,1,self.parent.boardpos,c.left,c.forward,board),c.compound(board.width,board.height,1,1,self.parent.boardpos,c.right,c.forward,board)]
    
class BlackPawn(Piece):
    def __init__(self):
        super().__init__("Pawn",1,1,join(PCS_IMG_DIR,"pawn_b.png"))
        self.en_passantable=False
        self.moved=False

    def moves(self, board:Board) -> list[BoardCoord]:
        '''Every square the piece can move to (excluding captures). Most of the time, a few calls to Movement functions are enough.'''
        if not self.moved:
            move_spaces=2
        else:
            move_spaces=1
        return m.backward(1,move_spaces,self.parent.boardpos,board)

    def capture_squares(self, board:Board, hypo:bool=False) -> list[BoardCoord]:
        '''Every square the piece can capture on, factoring in the board. If hypo is True, returns every square the piece can capture on hypothetically.'''
        temp=c.compound(1,1,1,1,self.parent.boardpos,c.left,c.backward,board)+c.compound(board.width,0,1,1,self.parent.boardpos,c.right,c.backward,board)
        if 0 < self.parent.boardpos[0] < 8:
            left=True
            right=True
        elif self.parent.boardpos[0] == 1:
            left=False
            right=True
        else:
            left=True
            right=False
        if left:
            target=board.full_layout[self.parent.boardpos[1]][self.parent.boardpos[0]-1].piece
            if target.name == "Pawn" and target.en_passantable:
                pass
        if right:
            target=board.full_layout[self.parent.boardpos[1]][self.parent.boardpos[0]+1].piece
            if target.name == "Pawn" and target.en_passantable:
                pass
        return temp

    def move_to(self, final:Tile, board:Board|None=None) -> Piece:
        '''Move to a Tile. What really happens is that it removes itself from the previous Tile and returns what should be in the Tile it moves to. Actually setting the Tile's piece to that is handled by the game.'''
        final.piece=self
        self.moved=True
        if self.en_passantable:
            self.en_passantable=False
        elif final.boardpos[1] == self.parent.boardpos[1]-2:
            self.en_passantable=True
        self.parent.piece=None
    
    def lines_of_sight(self, board:Board) -> list[Generator]:
        '''Returns a list of generators, each representing a line of sight of the piece.'''
        return [c.compound(0,board.height-1,1,1,self.parent.boardpos,c.left,c.backward,board),c.compound(board.width,board.height,1,1,self.parent.boardpos,c.right,c.backward,board)]
    
class WhiteBishop(Piece):
    def __init__(self):
        super().__init__("Bishop",3,0,join(PCS_IMG_DIR,"bishop_w.png"))

    def moves(self, board:Board):
        return m.diagonals((board.height,1,1,board.width),(inf,inf,inf,inf),self.parent.boardpos,board)
    
    def capture_squares(self, board:Board, hypo = False):
        return c.diagonals((board.height,1,1,board.width),(inf,inf,inf,inf),self.parent.boardpos,board,hypo)
    
    def lines_of_sight(self, board):
        return [Movement.compound(board.width,board.height,inf,inf,self.parent.boardpos,Movement.right,Movement.forward, board),Movement.compound(1,board.height,inf,inf,self.parent.boardpos,Movement.left,Movement.forward, board),Movement.compound(1,1,inf,inf,self.parent.boardpos,Movement.left,Movement.backward, board),Movement.compound(board.width,1,inf,inf,self.parent.boardpos,Movement.right,Movement.backward, board)]
    
class BlackBishop(Piece):
    def __init__(self):
        super().__init__("Bishop",3,1,join(PCS_IMG_DIR,"bishop_b.png"))
        self.moves=WhiteBishop.moves
        self.capture_squares=WhiteBishop.capture_squares
        self.move_to=WhiteBishop.move_to
        self.lines_of_sight=WhiteBishop.lines_of_sight
    
class WhiteKnight(Piece):
    def __init__(self):
        super().__init__("Knight",3,0,join(PCS_IMG_DIR,"knight_w.png"))

    def moves(self, board:Board):
        return m.l_shape((board.height,1,1,board.width),1,self.parent.boardpos,board,2,1)
    
    def capture_squares(self, board, hypo = False):
        return c.l_shape((board.height,1,1,board.width),1,self.parent.boardpos,board,2,1,hypo)
    
    def lines_of_sight(self, board):
        return c.l_shape((board.height,1,1,board.width),1,self.parent.boardpos,board,2,1,hypo=True)
    
class BlackKnight(Piece):
    def __init__(self):
        super().__init__("Knight",3,1,join(PCS_IMG_DIR,"knight_b.png"))
        self.moves=WhiteKnight.moves
        self.capture_squares=WhiteKnight.capture_squares
        self.move_to=WhiteKnight.move_to
        self.lines_of_sight=WhiteKnight.lines_of_sight

class WhiteRook(Piece):
    def __init__(self):
        super().__init__("Rook",5,0,join(PCS_IMG_DIR,"rook_w.png"))
        self.has_moved=False

    def moves(self, board):
        return m.orthogonals((board.height,1,1,board.width),(inf,inf,inf,inf),self.parent.boardpos,board)
    
    def capture_squares(self, board, hypo = False):
        return c.orthogonals((board.height,1,1,board.width),(inf,inf,inf,inf),self.parent.boardpos,board, hypo)
    
    def move_to(self, final, board = None):
        self.has_moved=True
        return super().move_to(final, board)
    
    def lines_of_sight(self, board):
        return [Movement.forward(board.height,inf,self.parent.boardpos,board), Movement.backward(1,inf,self.parent.boardpos,board), Movement.left(1,inf,self.parent.boardpos,board), Movement.right(board.width,inf,self.parent.boardpos,board)]
    
class BlackRook(Piece):
    def __init__(self):
        super().__init__("Rook",5,1,join(PCS_IMG_DIR,"rook_b.png"))
        self.moves=WhiteRook.moves
        self.capture_squares=WhiteRook.capture_squares
        self.move_to=WhiteRook.move_to
        self.lines_of_sight=WhiteRook.lines_of_sight

class WhiteQueen(Piece):
    def __init__(self):
        super().__init__("Queen",9,0,join(PCS_IMG_DIR,"queen_w.png"))

    def moves(self, board:Board):
        return itertools.chain(m.diagonals((8,1,1,8),(inf,inf,inf,inf),self.parent.boardpos,board),m.orthogonals((8,1,1,8),(inf,inf,inf,inf),self.parent.boardpos,board))
    
    def capture_squares(self, board, hypo = False):
        return itertools.chain(c.diagonals((8,1,1,8),(inf,inf,inf,inf),self.parent.boardpos,board,hypo),c.orthogonals((8,1,1,8),(inf,inf,inf,inf),self.parent.boardpos,board,hypo))
    
    def move_to(self, final, board = None):
        return super().move_to(final, board)
    
    def lines_of_sight(self, board):
        return [Movement.compound(8,8,inf,inf,self.parent.boardpos,Movement.right,Movement.forward, board),Movement.compound(1,8,inf,inf,self.parent.boardpos,Movement.left,Movement.forward, board),Movement.compound(1,1,inf,inf,self.parent.boardpos,Movement.left,Movement.backward, board),Movement.compound(8,1,inf,inf,self.parent.boardpos,Movement.right,Movement.backward, board),Movement.forward(8,inf,self.parent.boardpos,board), Movement.backward(1,inf,self.parent.boardpos,board), Movement.left(1,inf,self.parent.boardpos,board), Movement.right(8,inf,self.parent.boardpos,board)]
    
class BlackQueen(Piece):
    def __init__(self):
        super().__init__("Queen",9,1,join(PCS_IMG_DIR,"queen_b.png"))
        self.moves=WhiteQueen.moves
        self.capture_squares=WhiteQueen.capture_squares
        self.move_to=WhiteQueen.move_to
        self.lines_of_sight=WhiteQueen.lines_of_sight

class WhiteKing(Piece):
    def __init__(self):
        super().__init__("King",inf,0,join(PCS_IMG_DIR,"king_w.png"),True)

    def moves(self, board):
        return itertools.chain(m.diagonals((8,1,1,8),(1,1,1,1),self.parent.boardpos,board),m.orthogonals((8,1,1,8),(1,1,1,1),self.parent.boardpos,board))
    
    def capture_squares(self, board, hypo = False):
        return itertools.chain(c.diagonals((8,1,1,8),(1,1,1,1),self.parent.boardpos,board,hypo),c.orthogonals((8,1,1,8),(1,1,1,1),self.parent.boardpos,board,hypo))
    
    def move_to(self, final, board = None):
        return super().move_to(final, board)
    
    def lines_of_sight(self, board):
        return [Movement.compound(8,8,1,1,self.parent.boardpos,Movement.right,Movement.forward, board),Movement.compound(1,8,1,1,self.parent.boardpos,Movement.left,Movement.forward, board),Movement.compound(1,1,1,1,self.parent.boardpos,Movement.left,Movement.backward, board),Movement.compound(8,1,1,1,self.parent.boardpos,Movement.right,Movement.backward, board),Movement.forward(8,1,self.parent.boardpos,board), Movement.backward(1,1,self.parent.boardpos,board), Movement.left(1,1,self.parent.boardpos,board), Movement.right(8,1,self.parent.boardpos,board)]
    
class BlackKing(Piece):
    def __init__(self):
        super().__init__("King",inf,1,join(PCS_IMG_DIR,"king_b.png"),True)
        self.moves=WhiteKing.moves
        self.capture_squares=WhiteKing.capture_squares
        self.move_to=WhiteKing.move_to
        self.lines_of_sight=WhiteKing.lines_of_sight

STD_PCS_DICT:dict[str,type]={"P":WhitePawn,"p":BlackPawn,"B":WhiteBishop,"b":BlackBishop,"N":WhiteKnight,"n":BlackKnight,"R":WhiteRook,"r":BlackRook,"Q":WhiteQueen,"q":BlackQueen,"K":WhiteKing,"k":BlackKing}
STD_INIT_POS:list[list[str]]=["rnbqkbnr","pppppppp","8","8","8","8","PPPPPPPP","RNBQKBNR"]

board=Board(8,8,["8","8","8","8","8","8","8","8"],piecesdict=STD_PCS_DICT,initpos=STD_INIT_POS)
lock=Rules.lock
win=Rules.win

pawn_info=Info("Pawn","The most numerous piece on the board.","Little guys that usually can only go one step forward, but can take two steps on their first move. They capture differently, doing so one step forward diagonally in either direction. Can promote on the last row of the board. Experienced players can also make use of the abstruse method termed \"en passant\".",join(PCS_IMG_DIR,"pawn_w.png"),GREEN_TILE,"piece")
bishop_info=Info("Bishop","Snipers that really come into play after the early-game.","Moves and captures infinitely diagonally. A useful piece for sniping and plugging gaps, but its sieve-like capture structure and inability to move to more than half the squares on the board mean it is not as useful alone.",join(PCS_IMG_DIR,"bishop_w.png"),GREEN_TILE,"piece")
knight_info=Info("Knight","A piece with a truly odd movement pattern, when you think about it.","Moves in an L-shape of 2 tiles then 1 tile (or vice versa). Has the ability to teleport straight to the end of its movement. Is useful in the early game due to its mobility, but drops off later.",join(PCS_IMG_DIR,"knight_w.png"),GREEN_TILE,"piece")
rook_info=Info("Rook","The shining star of the famed (?) \"twin towers\" strategy.","One of the most powerful pieces on the board due to its ability to entirely block off ranks and files. Moves and captures infinitely in the orthogonal directions.",join(PCS_IMG_DIR,"rook_w.png"),GREEN_TILE,"piece")
queen_info=Info("Queen","In a shocking move for the time, the creators of chess made a woman the most powerful piece.","The most powerful and versatile piece on the board. Has the combined traits of the bishop and the rook. Tends to be blundered.",join(PCS_IMG_DIR,"queen_w.png"),GREEN_TILE,"piece")
king_info=Info("King","Useless aside from decorative value, similar to many actual kings.","The crux of the game. Threats against it need to be immediately answered, and trapping it ends the game whether by stalemate or checkmate. Can only move a single, pitiful, tile in any direction around it.",join(PCS_IMG_DIR,"king_w.png"),GREEN_TILE,"piece")

info=Info("Chess","The most commonly played variant of chess.","The form of chess known by billions worldwide. Its kinda boring, actually. Fun fact: can also be called \"occidental\" chess. Just learnt a new word, didn't ya?",join(PCS_IMG_DIR,"pawn_w.png"),GREEN_TILE,"mode",[pawn_info,bishop_info,knight_info,rook_info,queen_info,king_info])
info.construct()

piece_infos:list[Info]=[pawn_info,bishop_info,knight_info,rook_info,queen_info,king_info]
for piece_info in piece_infos:
    piece_info.set_links([info])
    piece_info.construct()

interpret=Rules.interpret
local_play=True
online_play=False

print('Module "standard" (occidental chess) loaded.')