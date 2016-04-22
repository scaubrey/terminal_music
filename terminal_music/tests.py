__author__ = 'Cam'

import unittest

import clues


class GameTests(unittest.TestCase):

    def test_treble_clef_clue(self):

        # Instantiation
        treble_clef_clue = clues.TrebleClefNoteClue('A4')

        with self.assertRaises(ValueError) as e:
            clues.TrebleClefNoteClue('a4')

        with self.assertRaises(ValueError) as e:
            clues.TrebleClefNoteClue('C2')

        with self.assertRaises(ValueError) as e:
            clues.TrebleClefNoteClue('blahblahblah')

        # Methods
        self.assertEqual(treble_clef_clue.get_answer(), 'A4')
        self.assertTrue(treble_clef_clue.is_correct_answer('A4'))

        # Check heigh adjustment for note stem
        self.assertEqual(len(treble_clef_clue.get_note_rows()), 9)
        self.assertEqual(len(clues.TrebleClefNoteClue('D5').get_note_rows()), 10)
        self.assertEqual(len(clues.TrebleClefNoteClue('E5').get_note_rows()), 11)
        self.assertEqual(len(clues.TrebleClefNoteClue('F5').get_note_rows()), 12)

    def test_bass_clef_clue(self):

        # Instantiation
        bass_clef_clue = clues.BassClefNoteClue('C3')

        with self.assertRaises(ValueError) as e:
            clues.BassClefNoteClue('c3')

        with self.assertRaises(ValueError) as e:
            clues.BassClefNoteClue('A4')

        with self.assertRaises(ValueError) as e:
            clues.BassClefNoteClue('blahblah')

        # Methods
        self.assertEqual(bass_clef_clue.get_answer(), 'C3')
        self.assertTrue(bass_clef_clue.is_correct_answer('C3'))

    def test_clue_pool(self):

        clue_pool = clues.CluePool()
        clue = clue_pool.get_clue()
        self.assertIsInstance(clue, clues.NoteBaseClue)


if __name__ == '__main__':
    unittest.main()
