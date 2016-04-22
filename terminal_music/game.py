__author__ = 'Cam'

import time

import clues


class FlashcardGame(object):
    """
    A class to encapsulate game related logic.
    """

    def __init__(self, num_questions=10):

        self._score = 0
        self._num_questions = num_questions
        self._clue_pool = clues.CluePool()

    def play(self):
        """
        Play the game.
        """

        print "\n***Welcome to the Terminal Music Theory Game!***\n"

        for i in range(self._num_questions):

            print '\n\nClue {}'.format(i)
            clue = self._clue_pool.get_clue()
            clue.display()

            # Look and feel
            time.sleep(0.5)

            # Get and score the answer
            user_answer = raw_input('What is the note?\t')

            # Validate
            if clue.is_correct_answer(user_answer):
                self.display_success()
                self._score += 1
            else:
                self.display_failure(clue.get_answer())

        print '\n\nFinal Score: {} out of {}'.format(self._score, self._num_questions)

    def display_success(self):
        """
        Print a message for a correct answer
        """
        print "Great Job!"

    def display_failure(self, answer):
        """
        Print a message for a wrong answer
        """
        print "Wrong, sorry. Answer: {}".format(answer)


