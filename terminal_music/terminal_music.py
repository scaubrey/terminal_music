__author__ = 'Cam'


import argparse

import game


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Terminal Music Education')

    parser.add_argument('-n',
                        default=10,
                        type=int,
                        help='Number of questions.')

    args = parser.parse_args()

    fc_game = game.FlashcardGame(num_questions=args.n)
    fc_game.play()


