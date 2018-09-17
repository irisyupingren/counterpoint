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
        return x.isRest == y.isRest and x.nameWithOctave == y.nameWithOctave
        # return not x.isRest and not y.isRest and x.nameWithOctave == y.nameWithOctave

    @staticmethod
    def bigleap(notebefore, note):
        '''
        The function to check whether the input "notebefore" and "note" consist a big 'leap'
        '''
        if notebefore.isRest:
            return False
        interval=music21.interval.notesToChromatic(notebefore, note)
        if interval==music21.interval.ChromaticInterval(6) or interval==music21.interval.ChromaticInterval(9) or interval == music21.interval.ChromaticInterval(10) or interval == music21.interval.ChromaticInterval(11) or interval == music21.interval.ChromaticInterval(-6) or interval == music21.interval.ChromaticInterval(-8) or interval == music21.interval.ChromaticInterval(-9) or interval == music21.interval.ChromaticInterval(-10) or interval == music21.interval.ChromaticInterval(-11):
            decision=True
        elif interval==music21.interval.ChromaticInterval(8):
            decision = 6
        elif interval==music21.interval.ChromaticInterval(12):
            decision = 12
        elif interval==music21.interval.ChromaticInterval(-12):
            decision = -12
        else:
            decision=False
        return decision

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
    def recover(leap, note, noteafter):
        interval=music21.interval.Interval(note, noteafter)
        halfstep=interval.cents/100
        decision=False
        if leap == 6 and halfstep > -6 and halfstep < 0:
            decision = True

        if leap == 12 and halfstep > -12 and halfstep < 0:
            decision = True

        if leap == -12 and halfstep < 12 and halfstep > 0:
            decision = True

        return decision

    @staticmethod
    def parallelfifth(cfnotebefore, notebefore, cfnote, note):
        if notebefore.isRest:
            return False
        intervalbefore=music21.interval.notesToInterval(cfnotebefore,notebefore)
        intervalnow=music21.interval.notesToInterval(cfnote,note)
        if intervalbefore == music21.interval.Interval('P5') and intervalnow == music21.interval.Interval('P5'):
            decision=True
        else:
            decision=False
        return decision

    @staticmethod
    def paralleloctave(cfnotebefore, notebefore, cfnote, note):
        if notebefore.isRest:
            return False
        intervalbefore=music21.interval.notesToInterval(cfnotebefore,notebefore)
        intervalnow=music21.interval.notesToInterval(cfnote,note)
        if intervalbefore == music21.interval.Interval('P8') and intervalnow == music21.interval.Interval('P8'):
            decision=True
        else:
            decision=False
        return decision

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
                if Generator.parallelfifth(cf[i-1], notebefore, cf[i], note):
                    f.write('parallelfifth skipping:'+str(c))
                    f.write(' \n')
                if Generator.paralleloctave(cf[i-1], notebefore, cf[i], note):
                    f.write('paralleloctave skipping:'+str(c))
                    f.write(' \n')
                if Generator.bigleap(notebefore, note)==True:
                    f.write('Leap is too big skipping:'+str(c))
                    f.write(' \n')
                if Generator.bigleap(notebefore, note)==6 or Generator.bigleap(notebefore, note)==12 or Generator.bigleap(notebefore, note)==-12:
                    # print("special leaps detected:"+str(bigleap(notebefore, note)))
                    if Generator.recover(Generator.bigleap(notebefore, note), note, noteafter)== False:
                        f.write('no recovery, break:'+str(c))
                        f.write(' \n')

                if Generator.is_same_note(notebefore, note):
                    flag=True
                    break
                if Generator.parallelfifth(cf[i-1], notebefore, cf[i], note):
                    flag=True
                    break
                if Generator.paralleloctave(cf[i-1], notebefore, cf[i], note):
                    flag=True
                    break
                if Generator.bigleap(notebefore, note)==True:
                    flag=True
                    break
                if Generator.bigleap(notebefore, note)==6 or Generator.bigleap(notebefore, note)==12 or Generator.bigleap(notebefore, note)==-12:
                    if Generator.recover(Generator.bigleap(notebefore, note), note, noteafter)== False:
                        flag=True
                        break

            if flag == False:
                if Generator.is_same_note(plist[-2], plist[-1]):
                    f.write('Repeat note skipping lastnote:'+str(c))
                    f.write(' \n')
                if Generator.parallelfifth(cf[-2], plist[-2], cf[-1], plist[-1]):
                    f.write('parallelfifth skipping lastnote:'+str(c))
                    f.write(' \n')
                if Generator.paralleloctave(cf[-2], plist[-2], cf[-1], plist[-1]):
                    f.write('paralleloctave skipping lastnote:'+str(c))
                    f.write(' \n')
                if Generator.bigleap(plist[-2], plist[-1])==True:
                    f.write('Leap is too big skipping lastnote:'+str(c))
                    f.write(' \n')
                if Generator.bigleap(plist[-2], plist[-1])==6 or Generator.bigleap(plist[-2], plist[-1])==12 or Generator.bigleap(plist[-2], plist[-1])==-12:
                    f.write('no recovery, break lastnote:'+str(c))
                    f.write(' \n')

                if Generator.is_same_note(plist[-2], plist[-1]):
                    flag=True
                if Generator.parallelfifth(cf[-2], plist[-2], cf[-1], plist[-1]):
                    flag=True
                if Generator.paralleloctave(cf[-2], plist[-2], cf[-1], plist[-1]):
                    flag=True
                if Generator.bigleap(plist[-2], plist[-1])==True:
                    flag=True

            if flag==False:
                answer.append(plist)
        f.close()

        f = open('test4first', 'w')
        for an in answer:
            f.write(str(an))
            f.write(' \n')
        f.close()
        return answer

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
    def getabovenotes2(note):
        notelist=[]

        interval = music21.interval.Interval('p1')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('m2')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('M2')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('m3')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('M3')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('p4')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('A4')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('p5')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('m6')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('M6')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('m7')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('M7')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('p8')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)
        return notelist

    @staticmethod
    def getaboveharmonic2(note):
        notelist=[]

        interval = music21.interval.Interval('m3')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('M3')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('p4')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('p5')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('m6')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('M6')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        interval = music21.interval.Interval('p8')
        interval.noteStart = note
        i=interval.noteEnd
        i.quarterLength = 2
        notelist.append(i)

        return notelist

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
                possibilities.append(Generator.getabovenotes2(cf[o]))
                o=o+1
            else:
                possibilities.append(Generator.getaboveharmonic2(cf[o]))

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
                    if Generator.parallelfifth(cf[o-1], notebefore2, cf[o], note):
                        f.write('parallelfifth skipping')
                        f.write(' \n')
                    if Generator.paralleloctave(cf[o-1], notebefore2, cf[o], note):
                        f.write('paralleloctave skipping')
                        f.write(' \n')
                if Generator.ifinharmonic(cf[o],note):
                    if Generator.approleftstep(notebefore, note, noteafter)==False:
                        f.write('not approching by step')
                        f.write(' \n')
                if Generator.bigleap(notebefore, note)==True:
                    f.write('Leap is too big skipping')
                    f.write(' \n')
                if Generator.bigleap(notebefore, note)==6 or Generator.bigleap(notebefore, note)==12 or Generator.bigleap(notebefore, note)==-12:
                    if Generator.recover(Generator.bigleap(notebefore, note), note, noteafter)== False:
                        f.write('no recovery, break')
                        f.write(' \n')

                if Generator.is_same_note(notebefore, note):
                    flag=True
                    break
                if i % 2 ==0:
                    if Generator.parallelfifth(cf[o-1], notebefore2, cf[o], note):
                        flag=True
                        break
                    if Generator.paralleloctave(cf[o-1], notebefore2, cf[o], note):
                        flag=True
                        break
                if Generator.ifinharmonic(cf[o],note):
                    if Generator.approleftstep(notebefore, note, noteafter)==False:
                        flag=True
                        break
                if Generator.bigleap(notebefore, note)==True:
                    flag=True
                    break
                if Generator.bigleap(notebefore, note)==6 or Generator.bigleap(notebefore, note)==12 or Generator.bigleap(notebefore, note)==-12:
                    if Generator.recover(Generator.bigleap(notebefore, note), note, noteafter)== False:
                        flag=True
                        break
            if flag == False:
                if Generator.is_same_note(plist[-2], plist[-1]):
                    f.write('Repeat note skipping')
                    f.write(' \n')
                if Generator.parallelfifth(cf[-2], plist[-3], cf[-1], plist[-1]):
                    f.write('parallelfifth skipping')
                    f.write(' \n')
                if Generator.paralleloctave(cf[-2], plist[-3], cf[-1], plist[-1]):
                    f.write('paralleloctave skipping')
                    f.write(' \n')
                if Generator.ifinharmonic(cf[-2],plist[-2]):
                    if Generator.approleftstep(plist[-3], plist[-2], plist[-1])==False:
                        f.write('not approching by step')
                        f.write(' \n')
                if Generator.bigleap(plist[-2], plist[-1])==True:
                    f.write('Leap is too big skipping')
                    f.write(' \n')
                if Generator.bigleap(plist[-3], plist[-2])==True:
                    f.write('Leap is too big skipping')
                    f.write(' \n')

                if Generator.is_same_note(plist[-2], plist[-1]):
                    flag=True
                if Generator.parallelfifth(cf[-2], plist[-3], cf[-1], plist[-1]):
                    flag=True
                if Generator.paralleloctave(cf[-2], plist[-3], cf[-1], plist[-1]):
                    flag=True
                if Generator.ifinharmonic(cf[-2],plist[-2]):
                    if Generator.approleftstep(plist[-3], plist[-2], plist[-1])==False:
                        flag=True
                if Generator.bigleap(plist[-2], plist[-1])==True:
                    flag=True
                if Generator.bigleap(plist[-3], plist[-2])==True:
                    flag=True

            if flag==False:
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
