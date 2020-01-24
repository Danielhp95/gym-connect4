from copy import deepcopy
import gym
from gym.spaces import Box, Discrete
from colorama import Fore

class Connect4Env(gym.Env):
    """
        GameState for the Connect 4 game.
        The board is represented as a 2D array (rows and columns).
        Each entry on the array can be:
            - 0 = empty    (.)
            - 1 = player 1 (X)
            - 2 = player 2 (O)
    """

    def __init__(self, width=7, height=6, connect=4):
        self.playerJustMoved = 2 # Player 1 will move now
        self.winner = 0 # 0 = no winner, 1 = Player 1 wins, 2 = Player 2 wins.

        self.width = width
        self.height = height
        self.connect = connect
        self.InitializeBoard()

        self.observation_space = [Box(low=0, high=2,
                                      shape=(self.width, self.height), dtype=int)
                                  for _ in range(2)] # Two player game
        self.action_space = Discrete(self.width)

        # Naive calculation. There are height * width individual cells
        # and each one can have 3 values. This is also encapsulates
        # invalid cases where a chip rests on top of an empy cell.
        self.state_space_size = (self.height * self.width) ** 3

    def InitializeBoard(self):
        """ 
        Initialises the Connect 4 gameboard.
        """
        self.board = []
        for y in range(self.width):
            self.board.append([0] * self.height)

    def Clone(self):
        """ 
        Creates a deep copy of the game state.
        NOTE: it is _really_ important that a copy is used during simulations
              Because otherwise MCTS would be operating on the real game board.
        :returns: deep copy of this GameState
        """
        st = Connect4State(width=self.width, height=self.height)
        st.playerJustMoved = self.playerJustMoved
        st.winner = self.winner
        st.board = [self.board[col][:] for col in range(self.width)]
        return st

    def step(self, movecol):
        """ 
        Changes this GameState by "dropping" a chip in the column
        specified by param movecol.
        :param movecol: column over which a chip will be dropped
        """
        if not(movecol >= 0 and movecol <= self.width and self.board[movecol][self.height - 1] == 0):
            raise IndexError(f'Invalid move. tried to place a chip on column {movecol} which is already full. Valid moves are: {self.get_moves()}')
        row = self.height - 1
        while row >= 0 and self.board[movecol][row] == 0:
            row -= 1

        row += 1

        self.playerJustMoved = 3 - self.playerJustMoved
        self.board[movecol][row] = self.playerJustMoved
        reward_vector = [0, 0]

        if self.does_move_win(movecol, row):
            self.winner = self.playerJustMoved
            if self.winner == 1: reward_vector = [1, -1]
            else: reward_vector = [-1, 1]
            
        info = {}
        return [deepcopy(self.board), deepcopy(self.board)], reward_vector, \
               self.winner == 0, info
            
    def get_moves(self):
        """
        :returns: array with all possible moves, index of columns which aren't full
        """
        if self.winner != 0:
            return []
        return [col for col in range(self.width) if self.board[col][self.height - 1] == 0]

    def does_move_win(self, x, y):
        """ 
        Checks whether a newly dropped chip at position param x, param y
        wins the game.
        :param x: column index
        :param y: row index
        :returns: (boolean) True if the previous move has won the game
        """
        me = self.board[x][y]
        for (dx, dy) in [(0, +1), (+1, +1), (+1, 0), (+1, -1)]:
            p = 1
            while self.is_on_board(x+p*dx, y+p*dy) and self.board[x+p*dx][y+p*dy] == me:
                p += 1
            n = 1
            while self.is_on_board(x-n*dx, y-n*dy) and self.board[x-n*dx][y-n*dy] == me:
                n += 1

            if p + n >= (self.connect + 1): # want (p-1) + (n-1) + 1 >= 4, or more simply p + n >- 5
                return True

        return False

    def is_on_board(self, x, y):
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def get_result(self, player):
        """ 
        :param player: (int) player which we want to see if he / she is a winner
        :returns: winner from the perspective of the param player
        """
        return player == self.winner

    def render(self, mode='human'):
        if mode != 'human': raise NotImplementedError('Rendering has not been coded yet')
        s = ""
        for x in range(self.height - 1, -1, -1):
            for y in range(self.width):
                s += [Fore.WHITE + '.', Fore.RED + 'X', Fore.YELLOW + 'O'][self.board[y][x]]
                s += Fore.RESET
            s += "\n"
        return s
