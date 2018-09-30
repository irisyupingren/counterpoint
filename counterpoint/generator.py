from __future__ import division

import music21
import numpy as np
import random
import sys
from random import randint
import itertools
import math
import os
from pprint import pprint
from functools import partial
from inspect import getmembers
from enum import Enum, auto, unique

class Generator (object):
    """ Provides counterpoint generation functions.
    """

    @staticmethod
    def get_input (path):
        """ Converts a MusicXML file to a list of notes.

        Args:
            path (str): The path of the file to load.

        Returns:
            list of music21.note.Note: A list of all notes in the file at `path`.

        """
        score = music21.converter.parse(path)
        notes = score.flat.notes # Flatten piece, get notes iterator.
        return list(notes) # Using `list` consumes the whole iterator.

    @staticmethod
    def get_above_note (note, interval):
        """ Computes the end note above a start note from a music21 interval description string (e.g. 'm3').

        Args:
            note (music21.note.Note): The start note.
            interval (str): The music21 interval description string (e.g. 'm3').

        Returns:
            music21.note.Note: The end note at the specified interval above `note`.

        """
        interval = music21.interval.Interval(interval)
        interval.noteStart = note # This assignment modifies `interval.noteEnd`.
        return interval.noteEnd

    @staticmethod
    def get_above_notes (note, intervals):
        """ Gets a list of the notes at the intervals given in `intervals` above `note`.

        Args:
            note (music21.note.Note): The start note.
            intervals (list of str): A list of music21 interval description strings (e.g. 'm3').

        Returns:
            list of music21.note.Note: A list of the notes at the intervals above `note` specified in `intervals`.

        """
        # Partial application of `get_above_note` to `note` to yield a single-param function we can use with `map`.
        func = partial(Generator.get_above_note, note)
        return list(map(func, intervals))

    @staticmethod
    def get_upper_first_note (note):
        """ Gets all possibilities for the first note of the counterpoint given the first note of the cantus firmus.

        Args:
            note (music21.note.Note): The first note of the cantus firmus.

        Returns:
            list of music21.note.Note: A list of possibilities for the first note of the counterpoint.

        """
        return note + Generator.get_above_notes(note, ['p5', 'p8'])

    @staticmethod
    def get_above_fifth (root):
        """ Get the note which is a fifth above the given root note.

        Args:
            note (music21.note.Note): The root note.

        Returns:
            music21.note.Note: The note which is a fifth above `root`.

        """
        return Generator.get_above_note(root, 'p5')

    @staticmethod
    def get_above_major_sixth (root):
        """ Get the note which is a major sixth above the given root note.

        Args:
            note (music21.note.Note): The root note.

        Returns:
            music21.note.Note: The note which is a major sixth above `root`.

        """
        return Generator.get_above_note(root, 'M6')

    @staticmethod
    def get_above_sixth (root):
        """ Get the notes which are a minor and major sixth above the given root note.

        Args:
            note (music21.note.Note): The root note.

        Returns:
            list of music21.note.Note: The notes which are a minor and major sixth above `root`.

        """
        return Generator.get_above_notes(root, ['m6', 'M6'])

    @staticmethod
    def get_above_octave (root):
        """ Get the note which is an octave above the given root note.

        Args:
            note (music21.note.Note): The root note.

        Returns:
            music21.note.Note: The note which is one octave above `root`.

        """
        return Generator.get_above_note(root, 'p8')

    @staticmethod
    def get_above_harmonic (root):
        """ Get the notes which are above and harmonic to the given root note.

        Args:
            note (music21.note.Note): The root note.

        Returns:
            list of music21.note.Note: A list of the notes which are harmonic to `root`.

        """
        return Generator.get_above_notes(root, ['m3', 'M3',' p4', 'p5', 'm6', 'M6', 'p8'])

    @staticmethod
    def is_same_note (x, y):
        """ Returns true if `x` and `y` are the same note, otherwise returns false.

        Args:
            x (music21.note.Note): The first note.
            y (music21.note.Note): The second note.

        Returns:
            bool: True if `x` and `y` are the same note, otherwise false.

        """
        return x.isRest == y.isRest and x.nameWithOctave == y.nameWithOctave # TODO: Examine semantics here carefully.
        # return not x.isRest and not y.isRest and x.nameWithOctave == y.nameWithOctave

    @unique # This annotaion forces all members of the enum to have distinct, unique values.
    class BigLeapType(Enum):
        """ An enumeration of types of big leap.
        """
         # The `auto` function is used here because the numeric values of the enum members don't matter.
        NOT_BIG_LEAP = auto()
        BIG_LEAP = auto()
        FIFTH = auto()
        OCTAVE_UP = auto()
        OCTAVE_DOWN = auto()

    @staticmethod
    def is_chromatic_distance (interval, distance):
        """ Returns true if an interval consists of the specified number of semitones.

        Args:
            interval (music21.interval.ChromaticInterval): The interval to check.
            distance (int): The number of semitones.

        Returns:
            bool: True if `interval` consists of `distance` semitones, otherwise false.

        """
        interval == music21.interval.ChromaticInterval(distance)

    @staticmethod
    def is_chromatic_distance_in (interval, distances):
        """ Returns true if an interval consists of any of the specified numbers of semitones.

        Args:
            interval (music21.interval.ChromaticInterval): The interval to check.
            distances (list of int): The list of numbers of semitones.

        Returns:
            bool: True if `interval` consists of a number of semitones in `distances`, otherwise false.

        """
        # The `any` function is equivalent to folding using `or` with 'false' as the initialiser.
        any(map(partial(Generator.is_chromatic_distance, interval), distances))

    @staticmethod
    def big_leap_type (x, y):
        """ Returns the type of big leap between two notes.

        Args:
            x (music21.note.Note): The first note.
            y (music21.note.Note): The second note.

        Returns:
            BigLeapType: The type of big leap between the two notes (may be NOT_BIG_LEAP).

        """
        if x.isRest or y.isRest: # TODO: Examine semantics here carefully.
            return Generator.BigLeapType.NOT_BIG_LEAP
        interval = music21.interval.notesToChromatic(x, y)
        if Generator.is_chromatic_distance_in(interval, [6, 9, 10, 11, -6, -8, -9, -10, -11]):
            return Generator.BigLeapType.BIG_LEAP
        elif Generator.is_chromatic_distance(interval, 8):
            return Generator.BigLeapType.FIFTH
        elif Generator.is_chromatic_distance(interval, 12):
            return Generator.BigLeapType.OCTAVE_UP
        elif Generator.is_chromatic_distance(interval, -12):
            return Generator.BigLeapType.OCTAVE_DOWN
        return Generator.BigLeapType.NOT_BIG_LEAP

    @staticmethod
    def is_special_leap (x, y):
        """ Returns true if the interval between two notes is considered a special leap.

        Args:
            x (music21.note.Note): The first note.
            y (music21.note.Note): The second note.

        Returns:
            bool: True if the interval between `x` and `y` is an octave above or below, or a fifth above, otherwise false.

        """
        return Generator.big_leap_type(x, y) in [Generator.BigLeapType.FIFTH, Generator.BigLeapType.OCTAVE_UP, Generator.BigLeapType.OCTAVE_DOWN]

    @staticmethod
    def exposedtritone(notes):
        intervalno=0
        trend=[]
        for i in range(0,len(notes)-1):
            if notes[i].isRest:
                trend.append(0)
                continue
            interval=music21.interval.Interval(notes[i], notes[i+1])
            halfstep=interval.cents/100
            intervalno=intervalno+float(abs(halfstep))

            if halfstep>0:
                trend.append(1)
            elif halfstep<0:
                trend.append(-1)
            elif halfstep==0:
                trend.append(0)



            if i>=1 and intervalno == 6 and abs(trend[i-1]-trend[i])>=2:
                decision=True
            else:
                decision=False

        return decision

    @staticmethod
    def get_half_steps (x, y):
        """ Returns the number of half steps in the interval between two notes.

        Args:
            x (music21.note.Note): The first note.
            y (music21.note.Note): The second note.

        Returns:
            int: The number of half steps in the interval between the two notes.

        """
        interval = music21.interval.Interval(x, y)
        return interval.cents / 100

    @staticmethod
    def recover (leap, x, y):
        """ Returns true if it is possible to recover from a given big leap between two notes, otherwise returns false.

        Args:
            x (counterpoint.Generator.BigLeapType): The big leap.
            x (music21.note.Note): The first note.
            y (music21.note.Note): The second note.

        Returns:
            bool: True if it is possible to recover from a given big leap between two notes, otherwise false.

        """
        half_steps = Generator.get_half_steps(x, y)
        return ((leap == Generator.BigLeapType.FIFTH and half_steps > -6 and half_steps < 0)
            or (leap == Generator.BigLeapType.OCTAVE_UP and half_steps > -12 and half_steps < 0)
            or (leap == Generator.BigLeapType.OCTAVE_DOWN and half_steps < 12 and half_steps > 0))

    @staticmethod
    def is_interval (interval, x, y):
        """ Returns true if `x` and `y` are at the interval specified, otherwise returns false.

        Args:
            interval (str): The music21 interval string of the interval to check for.
            x (music21.note.Note): The first note.
            y (music21.note.Note): The second note.

        Returns:
            bool: True if `x` and `y` are at the interval specified, otherwise false.

        """
        return music21.interval.notesToInterval(x, y) == music21.interval.Interval(interval)

    @staticmethod
    def is_parallel_fifth (m, n, x, y):
        """ Returns true if `m` and `n` and `x` and `y`, are each a fifth apart, otherwise returns false.

        Args:
            m (music21.note.Note): The first note of the first pair.
            n (music21.note.Note): The second note of the first pair.
            x (music21.note.Note): The first note of the second pair.
            y (music21.note.Note): The second note of the second pair.

        Returns:
            bool: True if `m` and `n` and `x` and `y`, are each a fifth apart, otherwise false.

        """
        is_fifth = partial(Generator.is_interval, 'P5')
        return (not n.isRest) and is_fifth(m, n) and is_fifth(x, y)

    @staticmethod
    def is_parallel_octave (m, n, x, y):
        """ Returns true if `m` and `n` and `x` and `y`, are each an octave apart, otherwise returns false.

        Args:
            m (music21.note.Note): The first note of the first pair.
            n (music21.note.Note): The second note of the first pair.
            x (music21.note.Note): The first note of the second pair.
            y (music21.note.Note): The second note of the second pair.

        Returns:
            bool: True if `m` and `n` and `x` and `y`, are each an octave apart, otherwise false.

        """
        is_octave = partial(Generator.is_interval, 'P8')
        return (not n.isRest) and is_octave(m, n) and is_octave(x, y)

    @staticmethod
    def getallpath(plist):
        allpath=list(itertools.product(*plist))
        return allpath

    @staticmethod
    def firstspeciesabove(cf):
        answer=[]
        possibilities=[]
        temp=[]
        possibilities.append(Generator.get_upper_first_note(cf[0]))
        for n in range(1,len(cf)-2):
            possibilities.append(Generator.get_above_harmonic(cf[n]))
        temp.append(Generator.get_above_major_sixth(cf[-2]))
        possibilities.append(temp)
        possibilities.append(Generator.get_above_harmonic(cf[-1]))
        allpossibilities=Generator.getallpath(possibilities)

        c=0

        f = open('test4log', 'w')
        for plist in allpossibilities:
            flag=False
            c=c+1
            print("running index:" +str(c))
            print("running answer"+str(plist))

            if Generator.exposedtritone(plist):
                f.write('tritone')
                break

            for i in range(1,len(cf)-1):
                note=plist[i]
                notebefore=plist[i-1]
                noteafter=plist[i+1]
                if Generator.is_same_note(notebefore, note):
                    f.write('Repeat note skipping:'+str(c))
                    f.write(' \n')
                if Generator.is_parallel_fifth(cf[i-1], notebefore, cf[i], note):
                    f.write('parallelfifth skipping:'+str(c))
                    f.write(' \n')
                if Generator.is_parallel_octave(cf[i-1], notebefore, cf[i], note):
                    f.write('paralleloctave skipping:'+str(c))
                    f.write(' \n')
                if Generator.big_leap_type(notebefore, note)==Generator.BigLeapType.BIG_LEAP:
                    f.write('Leap is too big skipping:'+str(c))
                    f.write(' \n')
                if Generator.is_special_leap(notebefore, note):
                    # print("special leaps detected:"+str(Generator.big_leap_type(notebefore, note)))
                    if not Generator.recover(Generator.bigleap(notebefore, note), note, noteafter):
                        f.write('no recovery, break:'+str(c))
                        f.write(' \n')

                if Generator.is_same_note(notebefore, note):
                    flag=True
                    break
                if Generator.is_parallel_fifth(cf[i-1], notebefore, cf[i], note):
                    flag=True
                    break
                if Generator.is_parallel_octave(cf[i-1], notebefore, cf[i], note):
                    flag=True
                    break
                if Generator.big_leap_type(notebefore, note)==Generator.BigLeapType.BIG_LEAP:
                    flag=True
                    break
                if Generator.is_special_leap(notebefore, note):
                    if not Generator.recover(Generator.bigleap(notebefore, note), note, noteafter):
                        flag=True
                        break

            if not flag:
                if Generator.is_same_note(plist[-2], plist[-1]):
                    f.write('Repeat note skipping lastnote:'+str(c))
                    f.write(' \n')
                if Generator.is_parallel_fifth(cf[-2], plist[-2], cf[-1], plist[-1]):
                    f.write('parallelfifth skipping lastnote:'+str(c))
                    f.write(' \n')
                if Generator.is_parallel_octave(cf[-2], plist[-2], cf[-1], plist[-1]):
                    f.write('paralleloctave skipping lastnote:'+str(c))
                    f.write(' \n')
                if Generator.big_leap_type(plist[-2], plist[-1])==Generator.BigLeapType.BIG_LEAP:
                    f.write('Leap is too big skipping lastnote:'+str(c))
                    f.write(' \n')
                if Generator.is_special_leap(plist[-2], plist[-1]):
                    f.write('no recovery, break lastnote:'+str(c))
                    f.write(' \n')

                if Generator.is_same_note(plist[-2], plist[-1]):
                    flag=True
                if Generator.is_parallel_fifth(cf[-2], plist[-2], cf[-1], plist[-1]):
                    flag=True
                if Generator.is_parallel_octave(cf[-2], plist[-2], cf[-1], plist[-1]):
                    flag=True
                if Generator.big_leap_type(plist[-2], plist[-1])==Generator.BigLeapType.BIG_LEAP:
                    flag=True

            if not flag:
                answer.append(plist)
        f.close()

        f = open('test4first', 'w')
        for an in answer:
            f.write(str(an))
            f.write(' \n')
        f.close()
        return answer

    @staticmethod
    def clone_note (note):
        """ Clones a note.

        Args:
            note (music21.note.Note): The note to clone.

        Returns:
            music21.note.Note: The cloned note.

        """
        return music21.note.Note(str(note.nameWithOctave))

    @staticmethod
    def getupperfirstnote2(n):
        notelist=[]

        notelist.append(music21.note.Rest(quarterLength=2.0))

        interval = music21.interval.Interval('p5')
        interval.noteStart = n
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('p8')
        interval.noteStart = n
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        pitch = n.nameWithOctave
        note2 = music21.note.Note(str(pitch))
        note2.quarterLength=2
        notelist.append(note2)
        return notelist

    @staticmethod
    def set_quarter_length (length, note):
        """ Returns a copy of a note with its quarter length set to the length given.

        Args:
            length (int): The length to set.
            note (music21.note.Note): The note to set the length on.

        Returns:
            music21.note.Note: The resultant note.

        """
        clone = Generator.clone_note(note) # Don't mutate original note.
        clone.quarterLength = length
        return clone

    @staticmethod
    def set_quarter_lengths (length, notes):
        """ Returns a copy of a list of notes with their quarter lengths set to the length given.

        Args:
            length (int): The length to set.
            notes (list of music21.note.Note): The notes to set the length on.

        Returns:
            list of music21.note.Note: The resultant notes.

        """
        func = partial(Generator.set_quarter_length, length)
        return map(func, notes)

    @staticmethod
    def get_all_above_notes (note):
        notes = Generator.get_above_notes(note, ['p1', 'm2', 'M2', 'm3', 'M3', 'p4', 'A4', 'p5', 'm6', 'M6', 'm7', 'M7', 'p8'])
        return Generator.set_quarter_lengths(2, notes)

    @staticmethod
    def get_all_above_harmonic (note):
        notes = Generator.get_above_notes(note, ['m3', 'M3', 'p4', 'p5', 'm6', 'M6', 'p8'])
        return Generator.set_quarter_lengths(2, notes)

    @staticmethod
    def ifinharmonic(cf, note):
        interval=music21.interval.notesToChromatic(cf, note)
        if (interval==music21.interval.ChromaticInterval(1) or interval==music21.interval.ChromaticInterval(-1) or
            interval==music21.interval.ChromaticInterval(2) or interval==music21.interval.ChromaticInterval(-2) or
            interval==music21.interval.ChromaticInterval(6) or interval==music21.interval.ChromaticInterval(-6) or
            interval==music21.interval.ChromaticInterval(10) or interval==music21.interval.ChromaticInterval(-10) or
            interval==music21.interval.ChromaticInterval(11) or interval==music21.interval.ChromaticInterval(-11)):
            decision=True
        else:
            decision=False
        return decision

    @staticmethod
    def approleftstep(notebefore, note, noteafter):
        if notebefore.isRest:
            return False

        interval=music21.interval.notesToChromatic(notebefore, note)
        interval2=music21.interval.notesToChromatic(note, noteafter)
        if (interval == music21.interval.ChromaticInterval(1) or interval == music21.interval.ChromaticInterval(-1)) and (interval2 ==music21.interval.ChromaticInterval(1) or interval2 ==music21.interval.ChromaticInterval(-1)):
            decision=True
        elif (interval == music21.interval.ChromaticInterval(1) or interval == music21.interval.ChromaticInterval(-1)) and (interval2 ==music21.interval.ChromaticInterval(2) or interval2 ==music21.interval.ChromaticInterval(-2)):
            decision=True
        elif (interval ==music21.interval.ChromaticInterval(2) or interval ==music21.interval.ChromaticInterval(-2)) and (interval2 == music21.interval.ChromaticInterval(1) or interval2 == music21.interval.ChromaticInterval(-1)):
            decision=True
        elif (interval ==music21.interval.ChromaticInterval(2) or interval ==music21.interval.ChromaticInterval(-2)) and (interval2 ==music21.interval.ChromaticInterval(2) or interval2 ==music21.interval.ChromaticInterval(-2)):
            decision=True
        else:
            decision = False
        return decision

    @staticmethod
    def secondspeciesabove(cf):
        o=0
        answer=[]
        possibilities=[]

        possibilities.append(Generator.getupperfirstnote2(cf[0]))
        for n in range(1,2*(len(cf))-4):
            # print("The nth note: "+str(n))
            if n % 2 == 1:
                possibilities.append(Generator.get_all_above_notes(cf[o]))
                o=o+1
            else:
                possibilities.append(Generator.get_all_above_harmonic(cf[o]))

        temp=[]
        temp.append(Generator.get_above_fifth(cf[-2]))
        possibilities.append(temp)

        possibilities.append(Generator.get_above_sixth(cf[-2]))

        temp=[]
        temp.append(Generator.get_above_octave(cf[-1]))
        possibilities.append(temp)
        allpossibilities=Generator.getallpath(possibilities)

        c=0
        f = open('test4secondlog', 'w')

        for plist in allpossibilities:
            flag=False
            c=c+1
            print("running index:" +str(c))
            print("running answer"+str(plist))

            if Generator.exposedtritone(plist):
                f.write('tritone')
                break

            for i in range(1,2*len(cf)-2):
                note=plist[i]
                notebefore=plist[i-1]
                notebefore2=plist[i-2]
                noteafter=plist[i+1]
                o=int(math.floor(i/2))

                if Generator.is_same_note(notebefore, note):
                    f.write('Repeat note skipping')
                    f.write(' \n')
                if i % 2 ==0:
                    if Generator.is_parallel_fifth(cf[o-1], notebefore2, cf[o], note):
                        f.write('parallelfifth skipping')
                        f.write(' \n')
                    if Generator.is_parallel_octave(cf[o-1], notebefore2, cf[o], note):
                        f.write('paralleloctave skipping')
                        f.write(' \n')
                if Generator.ifinharmonic(cf[o],note):
                    if not Generator.approleftstep(notebefore, note, noteafter):
                        f.write('not approching by step')
                        f.write(' \n')
                if Generator.big_leap_type(notebefore, note)==Generator.BigLeapType.BIG_LEAP:
                    f.write('Leap is too big skipping')
                    f.write(' \n')
                if Generator.is_special_leap(notebefore, note):
                    if not Generator.recover(Generator.bigleap(notebefore, note), note, noteafter):
                        f.write('no recovery, break')
                        f.write(' \n')

                if Generator.is_same_note(notebefore, note):
                    flag=True
                    break
                if i % 2 ==0:
                    if Generator.is_parallel_fifth(cf[o-1], notebefore2, cf[o], note):
                        flag=True
                        break
                    if Generator.is_parallel_octave(cf[o-1], notebefore2, cf[o], note):
                        flag=True
                        break
                if Generator.ifinharmonic(cf[o],note):
                    if not Generator.approleftstep(notebefore, note, noteafter):
                        flag=True
                        break
                if Generator.big_leap_type(notebefore, note)==Generator.BigLeapType.BIG_LEAP:
                    flag=True
                    break
                if Generator.is_special_leap(notebefore, note):
                    if not Generator.recover(Generator.bigleap(notebefore, note), note, noteafter):
                        flag=True
                        break
            if not flag:
                if Generator.is_same_note(plist[-2], plist[-1]):
                    f.write('Repeat note skipping')
                    f.write(' \n')
                if Generator.is_parallel_fifth(cf[-2], plist[-3], cf[-1], plist[-1]):
                    f.write('parallelfifth skipping')
                    f.write(' \n')
                if Generator.is_parallel_octave(cf[-2], plist[-3], cf[-1], plist[-1]):
                    f.write('paralleloctave skipping')
                    f.write(' \n')
                if Generator.ifinharmonic(cf[-2],plist[-2]):
                    if not Generator.approleftstep(plist[-3], plist[-2], plist[-1]):
                        f.write('not approching by step')
                        f.write(' \n')
                if Generator.big_leap_type(plist[-2], plist[-1])==Generator.BigLeapType.BIG_LEAP:
                    f.write('Leap is too big skipping')
                    f.write(' \n')
                if Generator.big_leap_type(plist[-3], plist[-2])==Generator.BigLeapType.BIG_LEAP:
                    f.write('Leap is too big skipping')
                    f.write(' \n')

                if Generator.is_same_note(plist[-2], plist[-1]):
                    flag=True
                if Generator.is_parallel_fifth(cf[-2], plist[-3], cf[-1], plist[-1]):
                    flag=True
                if Generator.is_parallel_octave(cf[-2], plist[-3], cf[-1], plist[-1]):
                    flag=True
                if Generator.ifinharmonic(cf[-2],plist[-2]):
                    if not Generator.approleftstep(plist[-3], plist[-2], plist[-1]):
                        flag=True
                if Generator.big_leap_type(plist[-2], plist[-1])==Generator.BigLeapType.BIG_LEAP:
                    flag=True
                if Generator.big_leap_type(plist[-3], plist[-2])==Generator.BigLeapType.BIG_LEAP:
                    flag=True

            if not flag:
                answer.append(plist)


        f.close()

        f = open('test4second', 'w')
        for an in answer:
            f.write(str(an))
            f.write(' \n')
        f.close()
        return answer

    @staticmethod
    def fromlisttostream(answer):
        print('total possible cpt: '+str(len(answer)))
        cp=music21.stream.Stream()
        index=randint(0, len(answer))
        picked=list(answer[index])
        for notes in picked:
            cp.append(notes)
        return cp

    @staticmethod
    def combinecfcp(cf, cp):
        sc = music21.stream.Score()
        p1 = music21.stream.Part()
        p1.id = 'part1'
        p2 = music21.stream.Part()
        p2.id = 'part2'
        for elements in cf:
            p1.append(elements)
        for elements in cp:
            p2.append(elements)
        sc.insert(0, p1)
        sc.insert(0, p2)
        return sc
