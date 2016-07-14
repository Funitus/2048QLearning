from board import Board
from q_utility import QLearningUtility
from q_learning_agent import Agent
import sys

def train():
    """
    Train learning agent with Q-learning algorithm
    """
    QLearningUtility.init()
    board = Board()
    agent = Agent(board)

    n_trials = 100000
    for trial in xrange(n_trials):
        board.reset()
        agent.reset(trial)
        while True:
            agent.make_an_action()
            # Check if the game is over
            if board.is_game_over():
                if board.get_highest_tile() == 11:
                    count_2048 += 1
                break
    QLearningUtility.save_q_dict('sample_q_network.out')

def test():
    """
    Play the game with the strongest Q-value network and record winning rate
    """
    QLearningUtility.init(trained_q='strongest_q_network.out')
    board = Board()
    agent = Agent(board, test=True)
    n_trials = 5000
    n_win = 0
    for trial in xrange(n_trials):
        board.reset()
        agent.reset(trial)
        while not board.is_game_over():
            recommendation, afterstate, max_val = agent.get_argmax_a(agent.get_legal_actions())
            board.update(recommendation)
        if board.get_highest_tile() == 11:
            n_win += 1

    print("Winning rate is {}".format(float(n_win)/n_trials))

def play():
    """
    Let the user play 2048 with recommendation from the strongest AI agent
    """
    QLearningUtility.init(trained_q='strongest_q_network.out')
    board = Board()
    board.reset()
    agent = Agent(board)
    while not board.is_game_over():
        board.print_board()
        recommendation, afterstate, max_val = agent.get_argmax_a(agent.get_legal_actions())
        print("The agent recommend action: {}".format(recommendation))
        a = None
        while a not in ['w', 'a', 's', 'd']:
            a = raw_input("Pick one of the following actions: w, a, s, d")
        board.update(a)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        play()
    else:
        if sys.argv[1] == 'train':
            train()
        elif sys.argv[1] == 'test':
            test()
        else:
            play()
