# To-do:
Checkmate checking
Implement a function to manually set the current player, targetable squares, and target (makes cheese-like functions easier)
Extra move options (for variants like beirut chess, where there is an option to detonate)
Custom positions (loaded in from PNG or FEN)
Specifiable win condition
Manual piece-placing option? (for certain variants)
Manual army choosing? (for some variants)
Pocket-like space (for some variants)

# Modes:
Duck chess (the duck)
Fischer random
Atomic chess
Conway chess (every move, pieces are generated based on Conway's Game of Life rules according to the average of the pieces that created it, adding for your colour and subtracting gor the other. These pieces are considere virtual and disappear when the virtual pieces are recalculated.)
Chinese chess
Fairy chess
Different board shapes and sizes
Random capture chess
Occidental standard chess (search it up)
Shogi
Checkers
Fog of war
Undercover queen?
Three-check
King of the Hill
Endgame chess
Los Alamos chess
Pre-chess
Omega chess
Transcendental chess
Dunsany's chess
Peasant's revolt
Really bad chess
Baroque chess
Berolina chess
Chess different armies
2000 AD chess
Kung-fu chess
Pocket mutation chess
Super-X chess
Way of the knight
Etchessera
Cannibal chess
Andernach chess
Circe chess
Benedict chess
Chad
Overpopulation chess
Checkers chess
Prohibition chess
Gravity chess
Einstein chess
Grid chess
Knight relay
Monochromatic chess
Portal chess
Portal-edge chess (only left and right sides)
Racing kings
Beirut chess
Panic chess
Synchronous chess?
Viennese chess
Taikyoku shogi
Grant Acedrex

# Code structure:
Menus have three levels, in decreasing order of relevance:
v.menu
v.submenu
v.additional

Menus:
"main"
--None

"modes"
--"main"
--"players"

"almanac"
--"modes"
    --[dynamic]
--"pieces"
    --[dynamic]

"game"
--None