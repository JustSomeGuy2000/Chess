'''Gamemode: occidental standard chess'''
try:
    from basic import *
except:
    from modes.basic import *
from pygame import *
from math import inf
from functools import partial
m=Movement
c=Capture
font.init()

def promote(source:Tile, options:OptionsBar):
    options.parent.parent.piece=source.piece
    source.piece.parent=options.parent.parent

class WhitePawn(Piece):
    def __init__(self):
        super().__init__("Pawn",1,0,join(PCS_IMG_DIR,"pawn_w.png"))
        self.en_passantable=False
        self.moved=False
        self.pointless=True

    def moves(self, game:Game) -> list[BoardCoord]:
        '''Every square the piece can move to (excluding captures). Most of the time, a few calls to Movement functions are enough.'''
        if not self.moved:
            move_spaces=2
        else:
            move_spaces=1
        return m.line(1,-1,0,move_spaces,self.parent.boardpos,game)

    def capture_squares(self, game:Game, hypo:bool=False) -> list[BoardCoord]:
        '''Every square the piece can capture on, factoring in the board. If hypo is True, returns every square the piece can capture on hypothetically.'''
        temp=itertools.chain(c.diagonal(-1,-1,0,0,1,self.parent.boardpos,game,self.colour,hypo),c.diagonal(1,-1,7,0,1,self.parent.boardpos,game,self.colour,hypo))
        if 0 < self.parent.boardpos[0] < 7:
            left=True
            right=True
        elif self.parent.boardpos[0] == 0:
            left=False
            right=True
        else:
            left=True
            right=False
        if left:
            target=game.board.full_layout[self.parent.boardpos[1]][self.parent.boardpos[0]-1].piece
            if isinstance(target,Piece) and target.name == "Pawn" and target.en_passantable:
                temp=itertools.chain(temp,[target.parent.boardpos])
                #game.board.arrows.append(Arrow(game.board.board_to_coord((target.parent.boardpos[0],target.parent.boardpos[1])),game.board.board_to_coord((target.parent.boardpos[0],target.parent.boardpos[1]-1))))
        if right:
            target=game.board.full_layout[self.parent.boardpos[1]][self.parent.boardpos[0]+1].piece
            if isinstance(target,Piece) and target.name == "Pawn" and target.en_passantable:
                temp=itertools.chain(temp,[target.parent.boardpos])
                #game.board.arrows.append(Arrow(game.board.board_to_coord((target.parent.boardpos[0],target.parent.boardpos[1])),game.board.board_to_coord((target.parent.boardpos[0],target.parent.boardpos[1]-1))))
        return temp

    def move_to(self, final:Tile, game:Game):
        '''Move to a Tile. Set its parent's piece to None and set the final Tile's piece to this.'''
        if isinstance(final.piece,BlackPawn) and final.piece.en_passantable and final.boardpos[1] == self.parent.boardpos[1]:
            final.piece=None
            final=game.board.full_layout[final.boardpos[1]-1][final.boardpos[0]]
        final.piece=self
        self.moved=True
        if self.en_passantable:
            self.en_passantable=False
        elif final.boardpos[1] == self.parent.boardpos[1]-2:
            self.en_passantable=True
        self.parent.piece=None
        self.parent=final
        if (self.colour == 0 and self.parent.boardpos[1] == 0) or (self.colour == 1 and self.parent.boardpos[1] == 7):
            self.get_options()

    def get_options(self) -> OptionsBar:
        queen_tile=Tile((0,0),"empty",Rect(0,0,0,0),self,None)
        if self.colour == 0:
            queen_tile.piece=WhiteQueen()
        else:
            queen_tile.piece=BlackQueen()
        rook_tile=Tile((0,0),"empty",Rect(0,0,0,0),self,None)
        if self.colour == 0:
            rook_tile.piece=WhiteRook()
        else:
            rook_tile.piece=BlackRook()
        bishop_tile=Tile((0,0),"empty",Rect(0,0,0,0),self,None)
        if self.colour == 0:
            bishop_tile.piece=WhiteBishop()
        else:
            bishop_tile.piece=BlackBishop()
        knight_tile=Tile((0,0),"empty",Rect(0,0,0,0),self,None)
        if self.colour == 0:
            knight_tile.piece=WhiteKnight()
        else:
            knight_tile.piece=BlackKnight()
        self.parent.propagate_options(OptionsBar(self, [queen_tile,rook_tile,bishop_tile,knight_tile],promote))
    
class BlackPawn(Piece):
    def __init__(self):
        super().__init__("Pawn",1,1,join(PCS_IMG_DIR,"pawn_b.png"))
        self.en_passantable=False
        self.moved=False
        self.get_options=partial(WhitePawn.get_options,self)
        self.pointless=True

    def moves(self, game:Game) -> list[BoardCoord]:
        '''Every square the piece can move to (excluding captures). Most of the time, a few calls to Movement functions are enough.'''
        if not self.moved:
            move_spaces=2
        else:
            move_spaces=1
        return m.line(1,1,0,move_spaces,self.parent.boardpos,game)

    def capture_squares(self, game:Game, hypo:bool=False) -> list[BoardCoord]:
        '''Every square the piece can capture on, factoring in the board. If hypo is True, returns every square the piece can capture on hypothetically.'''
        temp=itertools.chain(c.diagonal(-1,1,0,0,1,self.parent.boardpos,game,self.colour,hypo),c.diagonal(1,1,7,0,1,self.parent.boardpos,game,self.colour,hypo))
        if 0 < self.parent.boardpos[0] < 7:
            left=True
            right=True
        elif self.parent.boardpos[0] == 0:
            left=False
            right=True
        else:
            left=True
            right=False
        if left:
            target=game.board.full_layout[self.parent.boardpos[1]][self.parent.boardpos[0]-1].piece
            if isinstance(target,Piece) and target.name == "Pawn" and target.en_passantable:
                temp=itertools.chain(temp,[target.parent.boardpos])
                #game.board.arrows.append(Arrow(game.board.board_to_coord((target.parent.boardpos[0],target.parent.boardpos[1])),game.board.board_to_coord((target.parent.boardpos[0],target.parent.boardpos[1]+1))))
        if right:
            target=game.board.full_layout[self.parent.boardpos[1]][self.parent.boardpos[0]+1].piece
            if isinstance(target,Piece) and target.name == "Pawn" and target.en_passantable:
                temp=itertools.chain(temp,[target.parent.boardpos])
                #game.board.arrows.append(Arrow(game.board.board_to_coord((target.parent.boardpos[0],target.parent.boardpos[1])),game.board.board_to_coord((target.parent.boardpos[0],target.parent.boardpos[1]+1))))
        return temp

    def move_to(self, final:Tile, game:Game) -> Piece:
        '''Move to a Tile. What really happens is that it removes itself from the previous Tile and returns what should be in the Tile it moves to. Actually setting the Tile's piece to that is handled by the game.'''
        if isinstance(final.piece,WhitePawn) and final.piece.en_passantable and final.boardpos[1] == self.parent.boardpos[1]:
            final.piece=None
            final=game.board.full_layout[final.boardpos[1]+1][final.boardpos[0]]
        final.piece=self
        self.moved=True
        if self.en_passantable:
            self.en_passantable=False
        elif final.boardpos[1] == self.parent.boardpos[1]+2:
            self.en_passantable=True
        self.parent.piece=None
        self.parent=final
    
class WhiteBishop(Piece):
    def __init__(self):
        super().__init__("Bishop",3,0,join(PCS_IMG_DIR,"bishop_w.png"))

    def moves(self, game:Game):
        return m.diagonals((0,game.board.height-1,0,game.board.width-1),(inf,inf,inf,inf),self.parent.boardpos,game)
    
    def capture_squares(self, game:Game, hypo = False):
        return c.diagonals((0,game.board.height-1,0,game.board.width-1),(inf,inf,inf,inf),self.parent.boardpos,game,self.colour,hypo)
    
class BlackBishop(Piece):
    def __init__(self):
        super().__init__("Bishop",3,1,join(PCS_IMG_DIR,"bishop_b.png"))
        self.moves=partial(WhiteBishop.moves,self)
        self.capture_squares=partial(WhiteBishop.capture_squares,self)
        self.move_to=partial(WhiteBishop.move_to,self)
    
class WhiteKnight(Piece):
    def __init__(self):
        super().__init__("Knight",3,0,join(PCS_IMG_DIR,"knight_w.png"))

    def moves(self, game:Game):
        return m.l_shape((0,7,0,7),1,self.parent.boardpos,game,2,1)
    
    def capture_squares(self, game:Game, hypo = False):
        return c.l_shape((0,7,0,7),1,self.parent.boardpos,game,2,1,self.colour,hypo)
    
class BlackKnight(Piece):
    def __init__(self):
        super().__init__("Knight",3,1,join(PCS_IMG_DIR,"knight_b.png"))
        self.moves=partial(WhiteKnight.moves,self)
        self.capture_squares=partial(WhiteKnight.capture_squares,self)
        self.move_to=partial(WhiteKnight.move_to,self)

class WhiteRook(Piece):
    def __init__(self):
        super().__init__("Rook",5,0,join(PCS_IMG_DIR,"rook_w.png"))
        self.has_moved=False

    def moves(self, game:Game):
        return m.orthogonals((0,7,0,7),(inf,inf,inf,inf),self.parent.boardpos,game)
    
    def capture_squares(self, game:Game, hypo = False):
        return c.orthogonals((0,7,0,7),(inf,inf,inf,inf),self.parent.boardpos,game,self.colour, hypo)
    
    def move_to(self, final, game:Game):
        self.has_moved=True
        return Piece.move_to(self,final, game)
    
class BlackRook(Piece):
    def __init__(self):
        super().__init__("Rook",5,1,join(PCS_IMG_DIR,"rook_b.png"))
        self.has_moved=False
        self.moves=partial(WhiteRook.moves,self)
        self.capture_squares=partial(WhiteRook.capture_squares,self)
        self.move_to=partial(WhiteRook.move_to,self)

class WhiteQueen(Piece):
    def __init__(self):
        super().__init__("Queen",9,0,join(PCS_IMG_DIR,"queen_w.png"))

    def moves(self, game:Game):
        return itertools.chain(m.diagonals((0,7,0,7),(inf,inf,inf,inf),self.parent.boardpos,game),m.orthogonals((0,7,0,7),(inf,inf,inf,inf),self.parent.boardpos,game))
    
    def capture_squares(self, game:Game, hypo = False):
        return itertools.chain(c.diagonals((0,7,0,7),(inf,inf,inf,inf),self.parent.boardpos,game,self.colour,hypo),c.orthogonals((0,7,0,7),(inf,inf,inf,inf),self.parent.boardpos,game,self.colour,hypo))
    
    def move_to(self, final, game:Game):
        return Piece.move_to(self, final, game)
    
class BlackQueen(Piece):
    def __init__(self):
        super().__init__("Queen",9,1,join(PCS_IMG_DIR,"queen_b.png"))
        self.moves=partial(WhiteQueen.moves,self)
        self.capture_squares=partial(WhiteQueen.capture_squares,self)
        self.move_to=partial(WhiteQueen.move_to,self)

class WhiteKing(Piece):
    def __init__(self):
        super().__init__("King",inf,0,join(PCS_IMG_DIR,"king_w.png"),True)
        self.has_moved=False

    def moves(self, game:Game):
        temp=Movement.to_list(itertools.chain(m.diagonals((0,7,0,7),(1,1,1,1),self.parent.boardpos,game),m.orthogonals((0,7,0,7),(1,1,1,1),self.parent.boardpos,game))) 
        self.parent.piece=None
        for tile in game.board.get_matching(lambda t: True if t.piece != None and t.piece.colour != self.colour else False):
            for square in tile.piece.capture_squares(game, True):
                if square in temp:
                    temp.remove(square)
        self.parent.piece=self
        if game.board.turn == self.colour and not self.has_moved:
            pieces:list[Piece]=[]
            for row in game.board.full_layout:
                for tile in row:
                    if tile and tile.piece.colour != self.colour:
                        pieces.append(tile.piece)
            capture_squares=Rules.gen_capture_squares(game,pieces)
            right=[self.parent.boardpos,(self.parent.boardpos[0]+1,self.parent.boardpos[1]),(self.parent.boardpos[0]+2,self.parent.boardpos[1]),(self.parent.boardpos[0]+3,self.parent.boardpos[1])]
            left=[self.parent.boardpos,(self.parent.boardpos[0]-1,self.parent.boardpos[1]),(self.parent.boardpos[0]-2,self.parent.boardpos[1]),(self.parent.boardpos[0]-3,self.parent.boardpos[1]),(self.parent.boardpos[0]-4,self.parent.boardpos[1])]
            for direction in [right,left]:
                potential=game.board.get(direction[-1]).piece
                if True not in [bool(game.board.get(tile)) for tile in direction[1:-1]] and True not in [(tile in capture_squares) for tile in direction[:-1]] and isinstance(potential,Piece) and potential.name == "Rook" and potential.colour == self.colour and not potential.has_moved:
                    temp=itertools.chain(temp,[direction[2]])
        return temp
    
    def capture_squares(self, game:Game, hypo = False):
        temp=Movement.to_list(itertools.chain(c.diagonals((0,7,0,7),(1,1,1,1),self.parent.boardpos,game,self.colour,hypo),c.orthogonals((0,7,0,7),(1,1,1,1),self.parent.boardpos,game,self.colour,hypo)))
        restore_pieces={}
        for tile in temp:
            restore_pieces[tile]=game.board.get(tile).piece
            game.board.get(tile).piece=None
            for tile in game.board.get_matching(lambda t: True if t.piece != None and t.piece.colour != self.colour else False):
                if isinstance(tile.piece,(BlackKing, WhiteKing)):
                    for square in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
                        target_coord=(tile.boardpos[0]-square[0],tile.boardpos[1]-square[1])
                        if game.board.get(target_coord) and target_coord in temp:
                            temp.remove(target_coord)
                else:
                    for square in tile.piece.capture_squares(game, True):
                        if square in temp:
                            temp.remove(square)
        for tile in restore_pieces:
            game.board.get(tile).piece=restore_pieces[tile]
        return temp
    
    def move_to(self, final, game:Game):
        self.has_moved=True
        if final.boardpos[0] == self.parent.boardpos[0]+2:
            game.board.get((7,self.parent.boardpos[1])).piece.move_to(game.board.get(5,self.parent.boardpos[1]),game)
        if final.boardpos[0] == self.parent.boardpos[0]-2:
            game.board.get((0,self.parent.boardpos[1])).piece.move_to(game.board.get(3,self.parent.boardpos[1]),game)
        return Piece.move_to(self,final, game)
    
class BlackKing(Piece):
    def __init__(self):
        super().__init__("King",inf,1,join(PCS_IMG_DIR,"king_b.png"),True)
        self.has_moved=False
        self.moves=partial(WhiteKing.moves,self)
        self.capture_squares=partial(WhiteKing.capture_squares,self)
        self.move_to=partial(WhiteKing.move_to,self)

def after_move(game:Game):
    '''Things to do after a move.'''
    for row in game.board.full_layout:
        for tile in row:
            if isinstance(tile.piece,(WhitePawn,BlackPawn)) and tile.piece.colour != game.board.turn:
                tile.piece.en_passantable=False
    game.board.progress_turn()
    if game.board.turn == 0:
        end_of_turn(game)

def end_of_turn(game:Game):
    '''Things to do after all players have made their move.'''
    pass

STD_PCS_DICT:dict[str,type]={"P":WhitePawn,"p":BlackPawn,"B":WhiteBishop,"b":BlackBishop,"N":WhiteKnight,"n":BlackKnight,"R":WhiteRook,"r":BlackRook,"Q":WhiteQueen,"q":BlackQueen,"K":WhiteKing,"k":BlackKing}
STD_INIT_POS:list[str]=["rnbqkbnr","pppppppp","8","8","8","8","PPPPPPPP","RNBQKBNR"]

hidden=False
board=Board(8,8,["8","8","8","8","8","8","8","8"],piecesdict=STD_PCS_DICT,initpos=STD_INIT_POS)

pawn_info=Info("Pawn","The most numerous piece on the board.","Little guys that usually can only go one step forward, but can take two steps on their first move. They capture differently, doing so one step forward diagonally in either direction. Can promote on the last row of the board. Experienced players can also make use of the abstruse method termed \"en passant\".",join(PCS_IMG_DIR,"pawn_w.png"),GREEN_TILE,"piece")
bishop_info=Info("Bishop","Snipers that really come into play after the early-game.","Moves and captures infinitely diagonally. A useful piece for sniping and plugging gaps, but its sieve-like capture structure and inability to move to more than half the squares on the board mean it is not as useful alone.",join(PCS_IMG_DIR,"bishop_w.png"),GREEN_TILE,"piece")
knight_info=Info("Knight","A piece with a truly odd movement pattern, when you think about it.","Moves in an L-shape of 2 tiles then 1 tile (or vice versa). Has the ability to teleport straight to the end of its movement. Is useful in the early game due to its mobility, but drops off later.",join(PCS_IMG_DIR,"knight_w.png"),GREEN_TILE,"piece")
rook_info=Info("Rook","The shining star of the famed \"twin towers\" strategy.","One of the most powerful pieces on the board due to its ability to entirely block off ranks and files. Moves and captures infinitely in the orthogonal directions.",join(PCS_IMG_DIR,"rook_w.png"),GREEN_TILE,"piece")
queen_info=Info("Queen","In a shocking move for the time, the creators of chess made a woman the most powerful piece.","The most powerful and versatile piece on the board. Has the combined traits of the bishop and the rook. Tends to be blundered.",join(PCS_IMG_DIR,"queen_w.png"),GREEN_TILE,"piece")
king_info=Info("King","Useless aside from decorative value, similar to many actual kings.","The crux of the game. Threats against it need to be immediately answered, and trapping it ends the game whether by stalemate or checkmate. Can only move a single, pitiful, tile in any direction around it.",join(PCS_IMG_DIR,"king_w.png"),GREEN_TILE,"piece")

lore='''    The form of chess known by billions and played by millions worldwide. Its ancient significance has been lost to time. In the abscence of the continous vitalisation and esteem it once enjoyed, the once great Seed of ASBG has been reduced to a mere shadow of its former power. Many stars have stopped watching, many nebulae gone blind, but not all of them. Sometimes, those that remain still cast their gaze on our little blue planet to watch the games we humans play without realising their meaning, and cause the strange effects the ancients so often enjoyed to occur once more for just a moment. [RETURN] [RETURN]    Throughout it all, they who have been silently watching continued their vigil. Watching the daily lives, the joys and the sorrows, the triumphs and failures, of the puny creatures called humans. And the humans no longer need them. And they are pleased.'''

info=Info("Chess","The most commonly played variant of chess.",lore,join(PCS_IMG_DIR,"pawn_w.png"),GREEN_TILE,"mode",[pawn_info,bishop_info,knight_info,rook_info,queen_info,king_info],internal_name="standard")
info.construct()

piece_infos:list[Info]=[pawn_info,bishop_info,knight_info,rook_info,queen_info,king_info]
for piece_info in piece_infos:
    piece_info.set_links([info])
    piece_info.construct()

local_play=True
online_play=False

print('Module "standard" (occidental chess) loaded.')