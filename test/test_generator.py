import unittest
import music21

from counterpoint.generator import Generator

class TestGenerator (unittest.TestCase):
    """ Tests for the `Generator` class.
    """

    def test_get_above_note (self):
        expected = music21.note.Note('E-')
        actual = Generator.get_above_note(music21.note.Note('C'), 'm3')
        self.assertEqual(expected, actual)

    def test_get_half_steps (self):
        expected = 4
        actual = Generator.get_half_steps(music21.note.Note('C'), music21.note.Note('E'))
        self.assertEqual(expected, actual)
        
