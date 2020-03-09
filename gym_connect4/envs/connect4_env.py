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
            -1 = Draw
             0 = No winner (yet)
             1 = player 1 (X)
             2 = player 2 (O) 
    """

    def __init__(self, width=7, height=6, connect=4):
        self.num_players = 2

        self.width = width
        self.height = height
        self.connect = connect

        # TODO! Update to make this into two channels
        player_observation_space = Box(low=0, high=2,
                                       shape=(self.num_players, 
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
        self.board = np.zeros((self.width, self.height), dtype=np.int64)

        self.player_just_moved = 2 # Player 1 will move now
        self.winner = 0 # -1 = draw, 0 = no winner, 1 = Player 1 wins, 2 = Player 2 wins.
        return self.get_player_observations()

    def filter_observation_player_perspective(self, player: int) -> List[np.ndarray]:
        opponent = 1 if player == 2 else 2
        # One hot channel encoding of the board
        player_chips   = np.where(self.board == player, 1, 0)
        opponent_chips = np.where(self.board == opponent, 1, 0)
        return np.array([player_chips, opponent_chips])

    def get_player_observations(self) -> List[np.ndarray]:
        p1_state = self.filter_observation_player_perspective(1)
        p2_state = np.copy(p1_state)[::-1]
        return [p1_state, p2_state]

    def clone(self):
        """ 
        Creates a deep copy of the game state.
        NOTE: it is _really_ important that a copy is used during simulations
              Because otherwise MCTS would be operating on the real game board.
        :returns: deep copy of this GameState
        """
        st = Connect4Env(width=self.width, height=self.height)
        st.player_just_moved = self.player_just_moved
        st.winner = self.winner
        st.board = np.array([self.board[col][:] for col in range(self.width)])
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

        self.player_just_moved = 3 - self.player_just_moved
        self.board[movecol][row] = self.player_just_moved

        self.winner, reward_vector = self.check_for_episode_termination(movecol, row)
            
        zero_index_player_current_player = (3 - self.player_just_moved) - 1
        info = {'legal_actions': self.get_moves(),
                'current_player': zero_index_player_current_player}
        return self.get_player_observations(), reward_vector, \
               self.winner != 0, info

    def check_for_episode_termination(self, movecol, row):
        winner, reward_vector = self.winner, [0, 0]
        if self.does_move_win(movecol, row):
            winner = self.player_just_moved
            if winner == 1: reward_vector = [1, -1]
            elif winner == 2: reward_vector = [-1, 1]
        elif self.get_moves() == []:  # A draw has happened
            winner = -1
            reward_vector = [0, 0]
        return winner, reward_vector
            
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
        print(s)
