import modes.basic as b
import modes.standard as s
from itertools import chain

class Maharajah(b.Piece):
    def __init__(self):
        b.Piece.__init__(self,"Maharajah",s.inf,0,b.join(b.PCS_IMG_DIR,"amazon_w.png"))

    def capture_squares(self, game:b.Game, hypo:bool=False):
        temp=chain(s.WhiteQueen.capture_squares(self,game),s.WhiteKnight.capture_squares(self,game))
        captures=[]
        enemies:list[b.Tile]=game.board.get_matching(lambda t: True if isinstance(t.piece,b.Piece) and t.piece.colour == 1 and not isinstance(t.piece,s.BlackKing) else False)
        kings=game.board.get_matching(lambda t: True if isinstance(t.piece,b.Piece) and t.piece.colour == 1 and isinstance(t.piece,s.BlackKing) else False)
        for tile in enemies:
            hold=tile.piece
            tile.piece=b.BRICK_WALL
            for tile2 in enemies:
                if tile2 != tile:
                    for coord in tile2.piece.capture_squares(game,True):
                        captures.append(coord)
            tile.piece=hold
        for king in kings:
            for combo in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
                coords=(king.boardpos[0]-combo[0],king.boardpos[1]-combo[1])
                if isinstance(game.board.get(coords),b.Tile):
                    captures.append(coords)
        for coord in temp:
            square=game.board.get(coord)
            if coord not in captures:
                if hypo or isinstance(square.piece,b.Piece):
                    yield coord

    def moves(self, game):
        temp=chain(s.WhiteQueen.moves(self,game),s.WhiteKnight.moves(self,game))
        self.parent.piece=None
        enemies:list[b.Tile]=game.board.get_matching(lambda t: True if isinstance(t.piece,b.Piece) and t.piece.colour == 1 and not isinstance(t.piece,s.BlackKing) else False)
        king=game.board.get_matching(lambda t: True if isinstance(t.piece,b.Piece) and t.piece.colour == 1 and isinstance(t.piece,s.BlackKing) else False)[0]
        captures=[enemy.piece.capture_squares(game,True) for enemy in enemies]
        capture_sqs=[]
        for pattern in captures:
            for tile in pattern:
                capture_sqs.append(tile)
        for combo in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            coords=(king.boardpos[0]-combo[0],king.boardpos[1]-combo[1])
            if isinstance(game.board.get(coords),b.Tile):
                capture_sqs.append(coords)
        self.parent.piece=self
        for coord in temp:
            if coord not in capture_sqs:
                yield coord

pcsdict=b.copy.copy(s.STD_PCS_DICT)
pcsdict["M"]=Maharajah
initpos=["rnbqkbnr","pppppppp","8","8","8","8","8","4M3"]
board=b.Board(8,8,["8","8","8","8","8","8","8","8"],piecesdict=pcsdict,initpos=initpos)

m_info=b.Info("Amazon","Alias: Maharajah","WIP",b.join(b.PCS_IMG_DIR,"amazon_w.png"),b.CREAM_TILE,"piece")
info=b.Info("Maharajah and the Sepoys","The mad king's game.","WIP",b.join(b.PCS_IMG_DIR,"amazon_w.png"),b.CREAM_TILE,"mode",[m_info],"mats")
info.construct()
piece_infos=[m_info]
m_info.set_links([info])
m_info.construct()

hidden=False
local_play=True
online_play=False