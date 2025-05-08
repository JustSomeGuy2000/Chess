import modes.standard as s
import modes.basic as b

initpos=["1nn1knn1","4p3","8","8","8","8","PPPPPPPP","4K3"]

hidden=False
local_play=True
online_play=False

info=b.Info("Peasant's Revolt","Vive la revolution!","After decades of chafing under the black king's tyrannical rule, the pawns have had enough. They crown one of their own the white king and march on the black king and his knights.",b.join(b.PCS_IMG_DIR,"knight_b.png"),b.GREEN_TILE,"mode",[s.king_info,s.knight_info,s.pawn_info],"revolt")
info.construct()

board=b.Board(8,8,["8","8","8","8","8","8","8","8"],piecesdict=s.STD_PCS_DICT,initpos=initpos)