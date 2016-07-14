import random
from q_utility import QLearningUtility

class Agent(object):
    """Reinforcement Learning for 2048 Agent"""

    def __init__(self, board, test=False):
        super(Agent, self).__init__()
        self.board = board

        # The boolean variable indicating whether the agent is training or testing
        self.test = test

        self.exploration_rate = 0.4 if not self.test else 0
        self.learning_rate = 0.01

    def get_legal_actions(self):
        """Return an array containing possible actions"""
        legal_actions = []
        for action in QLearningUtility.LEGAL_ACTIONS:
            if self.board.is_legal_action(action):
                legal_actions.append(action)
        return legal_actions

    def make_an_action(self):
        """
        Select an action, then update Q value network if the agent is training
        """
        # <s,a,r,s'>
        # Step 1: s
        s = self.current_state

        # Step 2: a
        legal_actions = self.get_legal_actions()
        a = random.choice(legal_actions)
        board = self.board.clone_board()
        reward = board.take_action(a)
        board = board.board
        max_q = reward + QLearningUtility.get_q_value_total(a, QLearningUtility.get_tuple_states_from_board(board))
        if random.random() > self.exploration_rate:
            a, board, max_q = self.get_argmax_a(legal_actions)

        # Step 3: r
        r = self.board.update(a)

        if self.test:
            return

        # Step 4: get s'
        s_prime = QLearningUtility.get_tuple_states_from_board(self.board.board)

        # Step 5: update Q function
        q = 0
        if board is None:
            self.current_state = s_prime
            return
        board_tuples = QLearningUtility.get_tuple_states_from_board(board)
        if not self.board.is_game_over():
            legal_actions_prime = self.get_legal_actions()
            a_prime, max_s_prime, max_q_prime = self.get_argmax_a(legal_actions_prime)
            q = max_q_prime - QLearningUtility.get_q_value_total(a_prime, board_tuples)
        q = q * self.learning_rate

        for tuple_id in board_tuples:
            tuple_state_id = QLearningUtility.get_tuple_state_id_by_tuple_state(board_tuples[tuple_id])
            q_old = QLearningUtility.get_q_value(a, tuple_id, tuple_state_id)
            q_old += q
            QLearningUtility.set_q_value(a, tuple_id, tuple_state_id, q_old)

        self.current_state = s_prime

    def reset(self, n_trials):
        self.current_state = QLearningUtility.get_tuple_states_from_board(self.board.board)

    def get_argmax_a(self, legal_actions):
        """Take all legal actions and return the action that results in the best
        position
        """
        a = None
        max_value = float("-inf")
        max_s_prime = None
        for act in legal_actions:
            s_prime = self.board.clone_board()
            reward = s_prime.take_action(act)
            value = reward + QLearningUtility.get_q_value_total(act, QLearningUtility.get_tuple_states_from_board(s_prime.board))
            if value > max_value:
                a = act
                max_s_prime = s_prime.board
                max_value = value
        return a, max_s_prime, max_value
