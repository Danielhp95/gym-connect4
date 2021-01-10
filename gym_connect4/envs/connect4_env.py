from typing import List
from copy import deepcopy
import numpy as np
import gym
from gym.spaces import Box, Discrete, Tuple
from colorama import Fore


class Connect4Env(gym.Env):
    """
        GameState for the Connect 4 game.
        The board is represented as a 2D array (rows and columns).
        Each entry on the array can be:
            0 = empty    (.)
            1 = player 1 (X)
            2 = player 2 (O)

        Winner can be:
             None = No winner (yet)
            -1 = Draw
             1 = player 1 (X)
             2 = player 2 (O)
    """

    def __init__(self, width=7, height=6, connect=4):
        self.num_players = 2

        self.width = width
        self.height = height
        self.connect = connect

        # 3: Channels. Empty cells, p1 chips, p2 chips
        player_observation_space = Box(low=0, high=1,
                                       shape=(self.num_players + 1,
                                              self.width, self.height),
                                       dtype=np.int32)
        self.observation_space = Tuple([player_observation_space
                                        for _ in range(self.num_players)])
        self.action_space = Tuple([Discrete(self.width) for _ in range(self.num_players)])

        # Naive calculation. There are height * width individual cells
        # and each one can have 3 values. This is also encapsulates
        # invalid cases where a chip rests on top of an empy cell.
        self.state_space_size = (self.height * self.width) ** 3

        self.reset()

    def reset(self) -> List[np.ndarray]:
        """
        Initialises the Connect 4 gameboard.
        """
        self.board = np.full((self.width, self.height), -1)

        self.current_player = 0 # Player 1 (represented by value 0) will move now
        self.winner = None
        return self.get_player_observations()

    def filter_observation_player_perspective(self, player: int) -> List[np.ndarray]:
        opponent = 0 if player == 1 else 1
        # One hot channel encoding of the board
        empty_positions = np.where(self.board == -1, 1, 0)
        player_chips   = np.where(self.board == player, 1, 0)
        opponent_chips = np.where(self.board == opponent, 1, 0)
        return np.array([empty_positions, player_chips, opponent_chips])

    def get_player_observations(self) -> List[np.ndarray]:
        p1_state = self.filter_observation_player_perspective(0)
        p2_state = np.array([np.copy(p1_state[0]),
                             np.copy(p1_state[-1]), np.copy(p1_state[-2])])
        return [p1_state, p2_state]

    def clone(self):
        """
        Creates a deep copy of the game state.
        NOTE: it is _really_ important that a copy is used during simulations
              Because otherwise MCTS would be operating on the real game board.
        :returns: deep copy of this GameState
        """
        st = Connect4Env(width=self.width, height=self.height)
        st.current_player = self.current_player
        st.winner = self.winner
        st.board = np.array([self.board[col][:] for col in range(self.width)])
        return st

    def step(self, movecol):
        """
        Changes this GameState by "dropping" a chip in the column
        specified by param movecol.
        :param movecol: column over which a chip will be dropped
        """
        if not(movecol >= 0 and movecol <= self.width and self.board[movecol][self.height - 1] == -1):
            raise IndexError(f'Invalid move. tried to place a chip on column {movecol} which is already full. Valid moves are: {self.get_moves()}')
        row = self.height - 1
        while row >= 0 and self.board[movecol][row] == -1:
            row -= 1

        row += 1

        self.board[movecol][row] = self.current_player
        self.current_player = 1 - self.current_player

        self.winner, reward_vector = self.check_for_episode_termination(movecol, row)

        info = {'legal_actions': self.get_moves(),
                'current_player': self.current_player}
        return self.get_player_observations(), reward_vector, \
               self.winner is not None, info

    def check_for_episode_termination(self, movecol, row):
        winner, reward_vector = self.winner, [0, 0]
        if self.does_move_win(movecol, row):
            winner = 1 - self.current_player
            if winner == 0: reward_vector = [1, -1]
            elif winner == 1: reward_vector = [-1, 1]
        elif self.get_moves() == []:  # A draw has happened
            winner = -1
            reward_vector = [0, 0]
        return winner, reward_vector

    def get_moves(self):
        """
        :returns: array with all possible moves, index of columns which aren't full
        """
        if self.winner is not None:
            return []
        return [col for col in range(self.width) if self.board[col][self.height - 1] == -1]

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
        if self.winner == -1: return 0  # A draw occurred
        return +1 if player == self.winner else -1

    def render(self, mode='human'):
        if mode != 'human': raise NotImplementedError('Rendering has not been coded yet')
        s = ""
        for x in range(self.height - 1, -1, -1):
            for y in range(self.width):
                s += {-1: Fore.WHITE + '.', 0: Fore.RED + 'X', 1: Fore.YELLOW + 'O'}[self.board[y][x]]
                s += Fore.RESET
            s += "\n"
        print(s)
