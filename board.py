import random
from math import pow
from q_utility import QLearningUtility

class Board(object):
    """
    The 4x4 game Board along with other utility functions
    Tile is store as log2 of actual tile value, except for empty tile
    0 => 0
    2 => 1
    4 => 2
    ...
    1024 => 10
    2048 => 11
    """

    def __init__(self):
        # Initialize self.board as a 2-dim array size 4x4 to store tiles
        self.reset()

    def clone_board(self):
        """Utility function to duplicate current board and return a board Object"""
        clone = Board()
        for r, row in enumerate(self.board):
            for c, cell in enumerate(row):
                clone.board[r][c] = cell
        return clone

    def has_empty_tile(self):
        """Check if there is any empty tile on the board"""
        for row in self.board:
            for cell in row:
                if cell == 0:
                    return True
        return False

    def is_game_over(self):
        """The game is over under one of the 2 conditions:
        1. There is no legal action
        2. A 2048 tile has spawned
        """
        for row in self.board:
            for cell in row:
                if cell == 11:
                    return True
        for a in QLearningUtility.LEGAL_ACTIONS:
            if self.is_legal_action(a):
                return False
        return True

    def is_legal_action(self, action):
        """Check if the action can move any tile"""
        rotate_to_left = 0
        if action == 'w':
            rotate_to_left = 1
        elif action == 'd':
            rotate_to_left = 2
        elif action == 's':
            rotate_to_left = 3
        self.rotate_board(rotate_to_left)
        legal = self.is_left_legal_action()
        self.rotate_board(4 - rotate_to_left)
        return legal

    def is_left_legal_action(self):
        """This is an utility function.
        It checks if moving left is a legal action.
        """
        for r, row in enumerate(self.board):
            # This variable track the end of row. After this variable is set,
            # if there is any tile after it, then the action left can move
            # that tile and hence legal
            row_should_have_ended = False
            # This variable track the value of the previous tile. If this value
            # match the value of current tile, then they can merge and hence the
            # action is legal
            previous_cel_value = -1
            for c, val in enumerate(row):
                # Check if the cells can be merged
                if val == previous_cel_value and not val == 0:
                    return True
                else:
                    previous_cel_value = val

                # Check if the cells can be moved
                if val == 0:
                    row_should_have_ended = True
                else:
                    if row_should_have_ended:
                        return True
        return False

    def get_highest_tile(self):
        """Get the log value of highest tile on the board"""
        max_val = 0
        for row in self.board:
            for val in row:
                max_val = max(max_val, val)
        return max_val

    def get_new_tile(self):
        """Generate a new tile and randomly placing it on the board. There is
        90% chance of getting tile 2 and 10% chance of getting tile 4
        """
        # Check if a new tile can be spawned
        if not self.has_empty_tile():
            return

        # 90% chance of spawning a 2^1, 10% chance of spawning a 2^2
        new_seed = 1 if random.random() < 0.9 else 2
        while True:
            r = random.randint(0,3)
            c = random.randint(0,3)
            if self.board[r][c] == 0:
                self.board[r][c] = new_seed
                return

    def get_total_score(self):
        """Get the sum of all tiles on the board"""
        score = 0
        for row in self.board:
            for val in row:
                score += pow(2, val) if not val == 0 else 0
        return score

    def print_board(self):
        """Print board in a reading-friendly manner"""
        max_val = 0
        for r in self.board:
            max_val = max(max_val, max(r))
        max_len = len(str(pow(2, max_val)))
        for r in self.board:
            line = "| "
            for c in r:
                c = pow(2, c) if not c == 0 else 0
                val_len = len(str(c))
                c = " " if c == 0 else str(c)
                line += " " * (max_len - val_len) + str(c) + " | "
            print line

    def reset(self):
        """Start a new game: clear the board and randomly generate 2 new tiles"""
        self.board = [[0 for r in xrange(4)]  for c in xrange(4)]
        self.get_new_tile()
        self.get_new_tile()

    def rotate_board(self, steps):
        """Rotation is done clockwise"""
        for s in xrange(steps):
            for i in xrange(2):
                for j in xrange(i, 3 - i):
    				tmp = self.board[i][j]
    				self.board[i][j] = self.board[j][4 - i - 1]
    				self.board[j][4 - i - 1] = self.board[4 - i - 1][4 - j - 1]
    				self.board[4 - i - 1][4 - j - 1] = self.board[4 - j - 1][i]
    				self.board[4 - j - 1][i] = tmp

    def take_action(self, action):
        """Update board after the action is taken, returning reward but
        don't generate new tile just yet
        """
        # Rotate to board to so that the action becomes left
        rotate_to_left = 0
        if action == 'w':
            rotate_to_left = 1
        if action == 'd':
            rotate_to_left = 2
        if action == 's':
            rotate_to_left = 3
        self.rotate_board(rotate_to_left)

        if not self.is_left_legal_action():
            self.rotate_board(4 - rotate_to_left)
            return 0

        # reward is the sum of all newly merged tiles
        reward = 0

        # Push everything to the left
        for r, row in enumerate(self.board):
            crashed_tile = -1
            for c, val in enumerate(row):
                newC = c - 1
                while newC >= 0 and newC > crashed_tile:
                    if self.board[r][newC] == 0:
                        self.board[r][newC] = val
                        self.board[r][newC+1] = 0
                    elif self.board[r][newC] == val:
                        self.board[r][newC] += 1
                        reward += self.board[r][newC]
                        self.board[r][newC+1] = 0
                        crashed_tile = newC
                    else:
                        break
                    newC -= 1


        # Rotate the board back
        self.rotate_board(4 - rotate_to_left)

        return reward

    def update(self, action):
        """Perform action and get reward"""
        reward = self.take_action(action)
        self.get_new_tile()
        return reward
