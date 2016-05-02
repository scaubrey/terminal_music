__author__ = 'Cam'

import random

import math
import wave
import subprocess
import os
import struct
import pdb


class CluePool(object):
    """
    A class for selecting and distributing clue types.
    """

    def __init__(self):

        self._clue_types = [TrebleClefNoteClue, BassClefNoteClue]

        self._clue_types += [IntervalAudioClue]

    def get_clue(self):

        clue_type = random.choice(self._clue_types)
        clue_type_versions = clue_type().get_version_names()
        return clue_type(random.choice(clue_type_versions))


class BaseClue(object):
    """
    Class for base clue functionality.
    """

    def get_answer(self):
        raise NotImplementedError

    def is_correct_answer(self, answer):
        raise NotImplementedError

    def display(self):
        raise NotImplementedError


class AudioClue(BaseClue):

    def __init__(self):

        self._sample_frequency = 16e3  # samples/sec
        self._a4_tuning = 440.0  # hz
        self._amplitude = 65536 / 4  # 16bit signed

        self._notes = [
            'A4', 'Bb4', 'B4', 'C5', 'Db5', 'D5', 'Eb5', 'E5', 'F5', 'Gb5', 'G5', 'Ab5', 'A5'
        ]

        # Equal temperment tuning
        lower_log = math.log(self._a4_tuning, 2)
        upper_log = math.log(self._a4_tuning * 2, 2)
        self._note_freq_map = dict()
        for i, note in enumerate(self._notes):
            self._note_freq_map[note] = math.pow(2, lower_log + i / 12.0 * (upper_log - lower_log))

    def get_answer(self):

        raise NotImplementedError

    def is_correct_answer(self, answer):

        raise NotImplementedError

    def get_note_audio(self, note_name, length_sec):

        audio_len = int(self._sample_frequency * length_sec)
        audio_data = [0] * audio_len

        for i in range(audio_len):
            float_sample = math.sin(2 * math.pi * self._note_freq_map[note_name] * float(i) / self._sample_frequency)
            int_scaled_sample = int(float_sample * self._amplitude)
            audio_data[i] = int_scaled_sample

        return audio_data


class IntervalAudioClue(AudioClue):

    def __init__(self, interval_name='A4', mode='default'):

        super(IntervalAudioClue, self).__init__()

        self._note_play_len_sec = 1.0
        self._interval_name = interval_name
        self._mode = mode
        self._interval_semitone_map = {
            'min2': 1,
            '2': 2,
            'min3': 3,
            '3': 4,
            '4': 5,
            'dim5': 6,
            '5': 7,
            'aug5': 8,
            '6': 9,
            'min7': 10,
            '7': 11,
            'oct': 12
        }

    def get_version_names(self):
        return self._interval_semitone_map.keys()

    def get_answer(self):
        return self._interval_name

    def is_correct_answer(self, answer):
        return self._interval_name == answer

    def display(self):
        audio_data_lower_note = self.get_note_audio('A4', self._note_play_len_sec)

        upper_note_name = self._notes[self._interval_semitone_map[self._interval_name]]

        audio_data_upper_note = self.get_note_audio(upper_note_name, self._note_play_len_sec)

        if self._mode == 'default':
            audio_data = audio_data_lower_note + audio_data_upper_note
        elif self._mode == 'inverse':
            audio_data = audio_data_upper_note + audio_data_lower_note
        elif self._mode == 'simultaneous':
            audio_data = [sum(i) for i in zip(audio_data_lower_note, audio_data_upper_note)]

        tmp_file_path = './tmp.wav'

        wave_writer = wave.open(tmp_file_path, 'wb')
        wave_writer.setnchannels(2)
        wave_writer.setframerate(self._sample_frequency)
        wave_writer.setnframes(len(audio_data))
        wave_writer.setsampwidth(2)

        for sample in audio_data:
            wave_writer.writeframes(struct.pack('i', sample))

        subprocess.call(['afplay', tmp_file_path])

        os.remove(tmp_file_path)


class NoteBaseClue(BaseClue):
    """
    Class for notes in a clef and associated logic.
    """

    def __init__(self, note_name):

        self._note_name = note_name

        # Vertical length of note stem
        self._stem_len = 3

        # Width of printed note, should be even number
        self._stave_len = 20

        # Override for given clef
        self._note_stave_idx_map = None

    def get_clef_rows(self):
        raise NotImplementedError

    def get_base_stave_rows(self, stave_len=10):
        """
        Get a row representation of a blank stave.
        """
        return [
            '-' * stave_len,
            ' ' * stave_len,
            '-' * stave_len,
            ' ' * stave_len,
            '-' * stave_len,
            ' ' * stave_len,
            '-' * stave_len,
            ' ' * stave_len,
            '-' * stave_len
        ]

    def display(self):
        """
        Create a string drawing of the note with the clef.
        """

        # Get note and clef separately
        note_rows = self.get_note_rows()
        clef_rows = self.get_clef_rows()

        # Make sure they align
        graphic_height_diff = len(note_rows) - len(clef_rows)
        if graphic_height_diff < 0:
            raise Exception('Unexpected size of note {} and clef {}'.format(len(note_rows), len(clef_rows)))

        # Adjust height if different
        for i in range(graphic_height_diff):
            clef_rows.insert(0, ' ' * len(clef_rows[0]))

        # Join everything horizontically and then vertically
        stave = '\n'.join([tc_line + '' + stave_line for tc_line, stave_line in zip(clef_rows, note_rows)])

        print stave

    def is_correct_answer(self, answer):
        """
        Check if the string from user on stdin matches the note name
        """
        return self._note_name == answer

    def get_answer(self):
        """
        Get the answer to the clue
        """
        return self._note_name

    def get_version_names(self):
        """
        Return a list of strings for different instantiations of the note.
        """
        return self._note_stave_idx_map.keys()

    def get_note_rows(self):
        """
        Get the row representation of a note on the base stave.
        """

        # Set some vars used frequently
        base_stave = self.get_base_stave_rows(self._stave_len)
        note_x_pos = self._stave_len / 2
        note_idx = self._note_stave_idx_map[self._note_name]

        # Adjust number of lines to leave room for stems on high notes
        while note_idx - self._stem_len < 0:
            note_idx += 1
            base_stave.insert(0, ' ' * self._stave_len)

        # Select the proper note head if altered
        if '#' in self._note_name:
            note_head = '#0'
        elif 'b' in self._note_name:
            note_head = 'b0'
        else:
            note_head = '0'

        # Add note head to stem str
        base_stave[note_idx] = base_stave[note_idx][: (note_x_pos)] + \
                               note_head + \
                               base_stave[note_idx][: (note_x_pos - len(note_head))]

        # Add stem pieces to stave str
        for i in range(1, self._stem_len + 1):
            base_stave[note_idx - i] = base_stave[note_idx - i][: (note_x_pos + len(note_head))] +\
                                           '|' +\
                                           base_stave[note_idx - i][: (note_x_pos - (len(note_head) + 1))]
        return base_stave


class TrebleClefNoteClue(NoteBaseClue):
    """
    Class for a treble clef clue.
    """

    def __init__(self, note_name='A4'):

        super(TrebleClefNoteClue, self).__init__(note_name)

        self._note_stave_idx_map = {
            'F5': 0,
            'E5': 1,
            'D5': 2,
            'C5': 3,
            'B4': 4,
            'A4': 5,
            'G4': 6,
            'F4': 7,
            'E4': 8,
            'F#5': 0,
            'E#5': 1,
            'D#5': 2,
            'C#5': 3,
            'B#4': 4,
            'A#4': 5,
            'G#4': 6,
            'F#4': 7,
            'E#4': 8,
            'Fb5': 0,
            'Eb5': 1,
            'Db5': 2,
            'Cb5': 3,
            'Bb4': 4,
            'Ab4': 5,
            'Gb4': 6,
            'Fb4': 7,
            'Eb4': 8,
        }

        if note_name not in self._note_stave_idx_map.keys():
            raise ValueError('Invalid note name {}'.format(note_name))

    def get_clef_rows(self):
        """
        Get a the row representation of the treble clef.
        """
        return [
            '----|\--',
            '    |/  ',
            '----|---',
            '   /|   ',
            '--/ |_ -',
            '  | | | ',
            '---\|/--',
            '  o |   ',
            '--\_/---',
        ]


class BassClefNoteClue(NoteBaseClue):
    """
    Class for a bass clef clue.
    """

    def __init__(self, note_name='C3'):

        super(BassClefNoteClue, self).__init__(note_name)

        self._note_stave_idx_map = {
            'A3': 0,
            'G3': 1,
            'F3': 2,
            'E3': 3,
            'D3': 4,
            'C3': 5,
            'B2': 6,
            'A2': 7,
            'G2': 8,
            'A#3': 0,
            'G#3': 1,
            'F#3': 2,
            'E#3': 3,
            'D#3': 4,
            'C#3': 5,
            'B#2': 6,
            'A#2': 7,
            'G#2': 8,
            'Ab3': 0,
            'Gb3': 1,
            'Fb3': 2,
            'Eb3': 3,
            'Db3': 4,
            'Cb3': 5,
            'Bb2': 6,
            'Ab2': 7,
            'Gb2': 8,
        }

        if note_name not in self._note_stave_idx_map.keys():
            raise ValueError('Invalid note name {}'.format(note_name))

    def get_clef_rows(self):
        """
        Get a the row representation of the bass clef.
        """
        return [
            '--------',
            '  --\  o',
            '-/---|--',
            ' \   | o',
            '-----|--',
            '    /   ',
            '---/----',
            '  /     ',
            '--------',
        ]


# TODO: Additional clue types - Chords, Intervals, etc.
