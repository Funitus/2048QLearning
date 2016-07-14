class QLearningUtility(object):
    """Utility class to interact with QLearningUtility.
    Each QLearningUtility is a collection of 4 cells on the 2048 Board.
    """

    LEGAL_ACTIONS = [
        'w', #up
        'd', #right
        's', #down
        'a'  #left
    ]
    """This program doesn't use this constant, in order to speed up calculation.
    When edit this value, also edit formula for:
    - get_q_value_id
    - get_tuple_state_id_by_tuple_state
    """
    MAX_CELL_VAL = 11

    @staticmethod
    def load_q_dict(file_name):
        f = open(file_name, 'r').readline().split('|')
        QLearningUtility.Q_DICT = {};
        for i in xrange(4):
            action = f[2 * i]
            value = f[2 * i + 1].split(',')
            for j, val in enumerate(value):
                value[j] = float(val)
            QLearningUtility.Q_DICT[action] = value

    @staticmethod
    def save_q_dict(file_name):
        f = open(file_name, 'w')
        out = []
        for action in QLearningUtility.Q_DICT:
            out.append(action)
            out.append(",".join(str(x) for x in QLearningUtility.Q_DICT[action]))
        f.write("|".join(out))
        f.close()

    @staticmethod
    def init(trained_q=None):
        QLearningUtility.TUPLES = QLearningUtility.generate_tuples()
        QLearningUtility.TUPLE_STATES = QLearningUtility.generate_tuple_state_id()
        if trained_q is None:
            QLearningUtility.Q_DICT = QLearningUtility.generate_q_dict(QLearningUtility.TUPLES,
                QLearningUtility.TUPLE_STATES)
        else:
            QLearningUtility.load_q_dict(trained_q)

    @staticmethod
    def generate_q_dict(tuples, tuple_states):
        """The Q Look Up Table (LUT) is a combination of 17 smaller LUT,
        corresponding to each BoardTuple. In another word, each BoardTuple has
        a LUT. Each smaller LUT has possible states of that tuple, and Q value
        corresponding to the state-action pair.
        Q value is initialized to 0
        Structure of Q_DICT:
        {
            'a': Big-LUT-of-action-a
            'w': Big-LUT-of-action-w
            's': Big-LUT-of-action-s
            'd': Big-LUT-of-action-d
        }
        """
        q_dict = {}
        for a in QLearningUtility.LEGAL_ACTIONS:
            q_lut = []
            for tuple_id in tuples:
                for tuple_state_id in tuple_states:
                    q_lut.append(0)
            q_dict[a] = q_lut
        return q_dict

    @staticmethod
    def generate_tuple_state_id():
        """Each tuple state is an array length 4. Each array element can take
        value from 0, 2^1, 2^2, ... 2^11. Each state is mapped to an id for
        easy retrieval
        """
        tuple_state_ids = {}
        state_id = 0
        for first_elmt in xrange(QLearningUtility.MAX_CELL_VAL + 1):
            for second_elmt in xrange(QLearningUtility.MAX_CELL_VAL + 1):
                for third_elmt in xrange(QLearningUtility.MAX_CELL_VAL + 1):
                    for forth_elmt in xrange(QLearningUtility.MAX_CELL_VAL + 1):
                        state = [first_elmt, second_elmt, third_elmt, forth_elmt]
                        for i, element in enumerate(state):
                            state[i] = element
                        tuple_state_ids[state_id] = state
                        state_id += 1
        return tuple_state_ids


    @staticmethod
    def generate_tuples():
        """Each QLearningUtility is an array length 4, representing 4 cells in that
        board tuple. Each array element is a Python tuple with (row, col)
        coordinate of the corresponding QLearningUtility.
        Each QLearningUtility is mapped to an id for easy retrieval
        """
        tuples = []
        # Generate all the vertical tuples
        for r in xrange(4):
            board_tuple = []
            for c in xrange(4):
                board_tuple.append((r, c))
            tuples.append(board_tuple)

        # Generate all the horizontal tuples
        for c in xrange(4):
            board_tuple = []
            for r in xrange(4):
                board_tuple.append((r, c))
            tuples.append(board_tuple)

        # Generate all the square tuples
        for r in xrange(3):
            for c in xrange(3):
                tuples.append([
                    (r,     c),
                    (r,     c + 1),
                    (r + 1, c),
                    (r + 1, c + 1)
                ])

        # Assign each tuple an id; a.k.a a key in in tuples_dict for easy retrieval
        tuples_dict = {}
        for i, board_tuple in enumerate(tuples):
            tuples_dict[i] = board_tuple
        return tuples_dict

    @staticmethod
    def get_q_value(a, tuple_id, tuple_state_id):
        """Get a Q value value from the look up table"""
        if a is None:
            return 0
        return QLearningUtility.Q_DICT[a][QLearningUtility.get_q_value_id(tuple_id, tuple_state_id)]

    @staticmethod
    def get_q_value_id(tuple_id, tuple_state_id):
        """Get Q value ID of a tuple's state in its look up table"""
        return tuple_id * 20736 + tuple_state_id

    @staticmethod
    def get_q_value_total(a, state):
        """Return Q value as a sum of q values of all tuples in a state
        """
        q_value = 0
        for tuple_id in state:
            tuple_state = state[tuple_id]
            tuple_state_id = QLearningUtility.get_tuple_state_id_by_tuple_state(tuple_state)
            q_value += QLearningUtility.get_q_value(a, tuple_id, tuple_state_id)
        return q_value

    @staticmethod
    def get_tuple_states_from_board(board):
        """The state of a tuple is an array length 4. Each array element is the
        value of the tile on the main board corresponding to each tuple location
        """
        tuple_states = {}
        for tuple_id in QLearningUtility.TUPLES:
            state = []
            board_tuple = QLearningUtility.TUPLES[tuple_id]
            for tuple_location in board_tuple:
                r = tuple_location[0]
                c = tuple_location[1]
                state.append(board[r][c])
            tuple_states[tuple_id] = state
        return tuple_states

    @staticmethod
    def get_tuple_state_id_by_tuple_state(tuple_state):
        """Get a tuple state's id in its lookup table"""
        return tuple_state[0] * 1728 + tuple_state[1] * 144 + \
            tuple_state[2] * 12 + tuple_state[3]

    @staticmethod
    def set_q_value(a, tuple_id, tuple_state_id, q):
        QLearningUtility.Q_DICT[a][QLearningUtility.get_q_value_id(tuple_id, tuple_state_id)] = q
