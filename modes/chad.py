import modes.basic as b
import modes.standard as s
from modes.wotk import no_win
from itertools import chain
from functools import partial

hidden=False
local_play=True
online_play=False

walls=[[(2,6),(3,6),(4,6),(1,7),(1,8),(1,9),(5,7),(5,8),(5,9),(2,10),(3,10),(4,10)],[(7,1),(8,1),(9,1),(6,2),(6,3),(6,4),(10,2),(10,3),(10,4),(7,5),(8,5),(9,5)]]
castle=[[(2,7),(3,7),(4,7),(2,8),(3,8),(4,8),(2,9),(3,9),(4,9)],[(7,2),(8,2),(9,2),(7,3),(8,3),(9,3),(7,4),(8,4),(9,4)]]

'''
A piece may capture another piece only under two scenarios:
1. The piece is on the enemy's wall, and an enemy piece inside the castle is in its line of sight
2. The piece is inside its own castle, and an enemy piece is on its wall
Note: Checking for check ignores capture rules, instead following normal lines of sight.
Note: Kings are not subject to this rule, instead capturing as they move.
'''

class WhiteChadRook(s.Piece):
    def __init__(self):
        b.Piece.__init__(self,"Rook",1,0,b.join(b.PCS_IMG_DIR,"rook_w.png"))

    def moves(self, game):
        return b.Movement.orthogonals((0,11,0,11),(s.inf,s.inf,s.inf,s.inf),self.parent.boardpos,game)
    
    def capture_squares(self, game, hypo = False):
        raw=b.Capture.orthogonals((0,11,0,11),(s.inf,s.inf,s.inf,s.inf),self.parent.boardpos,game,self.colour,hypo)
        if hypo:
            for a in raw:
                yield a
            return
        if self.parent.boardpos in walls[(self.colour+1)%2]: #piece on the enemy wall
            for tile in raw: #enemy piece in castle
                if tile in castle[(self.colour+1)%2]:
                    yield tile
        elif self.parent.boardpos in castle[self.colour]: #piece in own castle
            for tile in raw: #enemy piece on wall
                if tile in walls[self.colour]:
                    yield tile

    def move_to(self, final, game):
        b.Piece.move_to(self, final, game)
        if final.boardpos in castle[(self.colour+1)%2]:
            if self.colour == 0:
                final.set_piece(WhiteChadQueen())
            else:
                final.set_piece(BlackChadQueen())

class BlackChadRook(b.Piece):
    def __init__(self):
        b.Piece.__init__(self,"Rook",1,1,b.join(b.PCS_IMG_DIR,"rook_b.png"))
        self.moves=partial(WhiteChadRook.moves,self)
        self.capture_squares=partial(WhiteChadRook.capture_squares,self)
        self.move_to=partial(WhiteChadRook.move_to,self)

class WhiteChadQueen(s.Piece):
    def __init__(self):
        b.Piece.__init__(self,"Queen",2,0,b.join(b.PCS_IMG_DIR,"chad_w.png"))
        self.image=b.transform.scale(self.image,(66,66))

    def moves(self, game):
        return chain(b.Movement.orthogonals((0,11,0,11),(s.inf,s.inf,s.inf,s.inf),self.parent.boardpos,game),b.Movement.diagonals((0,11,0,11),(s.inf,s.inf,s.inf,s.inf),self.parent.boardpos,game))
    
    def capture_squares(self, game, hypo = False):
        raw=chain(b.Capture.orthogonals((0,11,0,11),(s.inf,s.inf,s.inf,s.inf),self.parent.boardpos,game,self.colour,hypo),b.Capture.diagonals((0,11,0,11),(s.inf,s.inf,s.inf,s.inf),self.parent.boardpos,game,self.colour,hypo))
        if hypo:
            for a in raw:
                yield a
            return
        if self.parent.boardpos in walls[(self.colour+1)%2]: #piece on the enemy wall
            for tile in raw: #enemy piece in castle
                if tile in castle[(self.colour+1)%2]:
                    yield tile
        elif self.parent.boardpos in castle[self.colour]: #piece in own castle
            for tile in raw: #enemy piece on wall
                if tile in walls[self.colour]:
                    yield tile

class BlackChadQueen(b.Piece):
    def __init__(self):
        b.Piece.__init__(self,"Queen",2,1,b.join(b.PCS_IMG_DIR,"chad_b.png"))
        self.image=b.transform.scale(self.image,(66,66))
        self.moves=partial(WhiteChadQueen.moves,self)
        self.capture_squares=partial(WhiteChadQueen.capture_squares,self)

class WhiteChadKing(s.Piece):
    def __init__(self):
        b.Piece.__init__(self,"King",s.inf,0,b.join(s.PCS_IMG_DIR,"king_w.png"),True)

    def moves(self, game):
        raw=chain(b.Movement.orthogonals((0,11,0,11),(1,1,1,1),self.parent.boardpos,game),b.Movement.diagonals((0,11,0,11),(1,1,1,1),self.parent.boardpos,game),b.Movement.l_shape((0,11,0,11),1,self.parent.boardpos,game,2,1))
        enemy_captures=[]
        for tile in game.board.get_matching(lambda t: True if isinstance(t.piece,b.Piece) and not t.piece.belongs_to(self.colour) else False):
            enemy_captures.extend(tile.piece.capture_squares(game,True))
        for tile in raw:
            if tile not in enemy_captures and tile in castle[self.colour]:
                yield tile

    def capture_squares(self, game, hypo=False):
        raw=chain(b.Capture.orthogonals((0,11,0,11),(1,1,1,1),self.parent.boardpos,game,self.colour,hypo),b.Capture.diagonals((0,11,0,11),(1,1,1,1),self.parent.boardpos,game,self.colour,hypo),b.Capture.l_shape((0,11,0,11),1,self.parent.boardpos,game,2,1,self.colour,hypo))
        enemy_captures=[]
        for tile in game.board.get_matching(lambda t: True if isinstance(t.piece,b.Piece) and not t.piece.belongs_to(self.colour) and not t.piece.name == "King" else False):
            enemy_captures.extend(tile.piece.capture_squares(game,True))
        for tile in raw:
            if tile not in enemy_captures and tile in castle[self.colour]:
                yield tile

class BlackChadKing(b.Piece):
    def __init__(self):
        b.Piece.__init__(self,"King",s.inf,1,b.join(b.PCS_IMG_DIR,"king_b.png"),True)
        self.moves=partial(WhiteChadKing.moves,self)
        self.capture_squares=partial(WhiteChadKing.capture_squares,self)

pcsdict={"r":BlackChadRook,"R":WhiteChadRook,"q":BlackChadQueen,"Q":BlackChadQueen,"k":BlackChadKing,"K":WhiteChadKing}
board=b.Board(12,12,["93"]*12,(66,66),["93","93","7rrr2","7rkr2","7rrr2","93","93","2RRR7","2RKR7","2RRR7","93","93"],pcsdict,b.denest(walls,1),True)

piece_infos=[]
info=b.Info("Chad","It is said that only True Chads stand even a chance at winning this game.","WIP",b.join(b.PCS_IMG_DIR,"chad_b.png"),b.CREAM_TILE,"mode",[s.king_info,s.rook_info,s.queen_info],"chad")
info.construct()

#win=no_win