# To-do:
- Colour schemes
- Pins are not per piece, but rather included in Rules.lock()?
- Finish adding animations
- Implement decorator that handles all the move validation, so actual movement functions only have to focus on generation
- Implement draws (5-fold repetition or insufficient material)
- Implement a function to manually set the current player, targetable squares, and target (makes cheese-like functions easier)
- Extra move options (for variants like beirut chess, where there is an option to detonate)
- Manual piece-placing option? (for certain variants)
- Manual army choosing? (for some variants)
- Remove debug stuff (grid, mouse position, tiles showing if they are locked)

# Modes to add:
Fischer random
Conway chess (every move, pieces are generated based on Conway's Game of Life rules according to the average of the pieces that created it, adding for your colour and subtracting gor the other. These pieces are considere virtual and disappear when the virtual pieces are recalculated.)
Chinese chess
Fairy chess
Different board shapes and sizes
Random capture chess
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
Ultima
Nemeroth

# Code structure:
Menus have three levels, in decreasing order of relevance:
- v.menu
- v.submenu
- v.additional

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

"settings"
--"main"

# Attributes of gamemodes
## Mandatory
### hidden:
**bool**
- Whether this file should be displayed in the mode choosing screen

### board:
**Board**
- The board the game should use. Should be already instantiated (I think it'll be fine)

### piece_infos:
**list[Info]**
- A list of Info objects regarding any new pieces.

### info:
**Info**
- An Info object regarding the gamemode

### local_play:
**bool**
- Whether this gamemode can be played locally.

### online_play:
**bool**
- Whether this gamemode can be played online.

## Optional
### win():
**(Game) -> tuple[list[BoardCoord], bool|None, int]**
- Called after every selection to determine locked squares and if anyone won

### interpret(): 
**Callable[[Game,str], None]**
- Called in multiplayer to translate incoming signals into moves

### after_move():
**(Game) -> None**
- Called after every move

### after_capture():
**(Game, Tile) -> None**
- Called after every capture

### capture_filter():
**(Iterator[BoardCoord], Game) -> None**
- Called to modify capture square positions before they are applied

### move_filter():
**(Iterator[BoardCoord], Game) -> None**
- Called to modify move square positions before they are applied

### game_start():
**(Game) -> None**
- Called just after the game starts