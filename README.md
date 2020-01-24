
<img src="https://raw.githubusercontent.com/Danielhp95/gym-connect4/master/connect4.png" alt="drawing" width="300"/>

# Connect 4

Connect 4 is a **two player**, **zero-sum**, **symetrical** connection game, in
which players take turns dropping one coloured disc from the top into a
seven-column, six-row grid. The pieces fall straight down, occupying the lowest
available space within the column. The objective of the game is to be the first
to form a horizontal, vertical or diagonal line of four of one's own discs.

Fun fact: Connect 4 is a solved game. The first player is guaranteed to win by
playing the right moves.

## Game parameterization

The gym environment takes the following parameters:
+ **Width**: Number of rows on the board. Default: 7
+ **Height**: Height of each board row. Default: 6
+ **Connect**: Number of chips of the same colour that need to be placed in a valid pattern to win the game. Default: 4

Use `gym.make` to pass a specific parameterization. For instance: `gym.make('Connect4-v0', height=6, width=9, connect=2)`
