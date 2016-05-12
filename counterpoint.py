from __future__ import division 
 
import music21
import numpy as np
import random
import sys
from random import randint
import itertools
import math

def getinput(path):
    '''
    The function convert musicxml files to numerical values
    '''
    cf = music21.converter.parse(path)
    notelist=[]
    cf.show('text')
    for i in range(1,len(cf[2])):
        measure=cf[2][i]
        for note in measure:
            if (type(note) is music21.note.Note):
                notelist.append(note)
    return notelist

def getupperfirstnote(note):
    '''
    Get all the possibility of the first note when the counterpoint is the upper part and the cantus firmus is the lower part
    '''
    notelist=[]

    notelist.append(note)

    interval = music21.interval.Interval('p5')
    interval.noteStart = note
    notelist.append(interval.noteEnd)

    interval = music21.interval.Interval('p8')
    interval.noteStart = note
    notelist.append(interval.noteEnd)

    notelist.append(note)
    return notelist

def getabovefifth(note):
    '''
    Get the note which is a fifth from the lower part cantus firmus
    '''
    interval = music21.interval.Interval('p5')
    interval.noteStart = note
    i=interval.noteEnd
    i.quarterLength = 2
    return i

def getabovemajorsix(note):
    interval = music21.interval.Interval('M6')
    interval.noteStart = note
    return interval.noteEnd

def getabovesixth(note):
    notelist=[]

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
    return notelist

def getaboveoctave(note):
    interval = music21.interval.Interval('p8')
    interval.noteStart = note
    i=interval.noteEnd
    return i

def getaboveharmonic(note):
    '''
    Get the notes which are harmonic to the given lower part cantus firmus
    '''
    notelist=[]

    interval = music21.interval.Interval('m3')
    interval.noteStart = note
    notelist.append(interval.noteEnd)

    interval = music21.interval.Interval('M3')
    interval.noteStart = note
    notelist.append(interval.noteEnd)

    interval = music21.interval.Interval('p4')
    interval.noteStart = note
    notelist.append(interval.noteEnd)

    interval = music21.interval.Interval('p5')
    interval.noteStart = note
    notelist.append(interval.noteEnd)

    interval = music21.interval.Interval('m6')
    interval.noteStart = note
    notelist.append(interval.noteEnd)

    interval = music21.interval.Interval('M6')
    interval.noteStart = note
    notelist.append(interval.noteEnd)

    interval = music21.interval.Interval('p8')
    interval.noteStart = note
    notelist.append(interval.noteEnd)

    return notelist

def repeatnote(notebefore, note):
    '''
    The function to check whether the input "notebefore" and "note" are the same note
    '''
    if notebefore.isRest:
        return False
    if notebefore.nameWithOctave == note.nameWithOctave:
        decision = True
    else:
        decision = False
    return decision

def bigleap(notebefore, note):
    '''
    The function to check whether the input "notebefore" and "note" consist a big 'leap'
    '''
    if notebefore.isRest:
        return False
    interval=music21.interval.notesToChromatic(notebefore, note)
    if interval==music21.interval.ChromaticInterval(6) or interval==music21.interval.ChromaticInterval(9) or interval == music21.interval.ChromaticInterval(10) or interval == music21.interval.ChromaticInterval(11) or interval == music21.interval.ChromaticInterval(6) or interval == music21.interval.ChromaticInterval(-6) or interval == music21.interval.ChromaticInterval(-8) or interval == music21.interval.ChromaticInterval(-9) or interval == music21.interval.ChromaticInterval(-10) or interval == music21.interval.ChromaticInterval(-11):
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

def getallpath(plist):
    allpath=list(itertools.product(*plist))
    return allpath

def firstspeciesabove(cf):
    answer=[]
    possibilities=[]
    temp=[]
    possibilities.append(getupperfirstnote(cf[0]))
    for n in range(1,len(cf)-2):
        possibilities.append(getaboveharmonic(cf[n]))
    temp.append(getabovemajorsix(cf[-2]))
    possibilities.append(temp)
    possibilities.append(getaboveharmonic(cf[-1]))
    allpossibilities=getallpath(possibilities)

    c=0

    f = open('test4log', 'w')
    for plist in allpossibilities:
        flag=False
        c=c+1
        print("running index:" +str(c))
        print("running answer"+str(plist))

        if exposedtritone(plist):
            f.write('tritone')
            break

        for i in range(1,len(cf)-1):
            note=plist[i]
            notebefore=plist[i-1]
            noteafter=plist[i+1]
            if repeatnote(notebefore, note) == True:
                f.write('Repeat note skipping:'+str(c))
                f.write(' \n')
            if parallelfifth(cf[i-1], notebefore, cf[i], note)==True:
                f.write('parallelfifth skipping:'+str(c))
                f.write(' \n')
            if paralleloctave(cf[i-1], notebefore, cf[i], note)==True:
                f.write('paralleloctave skipping:'+str(c))
                f.write(' \n')
            if bigleap(notebefore, note)==True:
                f.write('Leap is too big skipping:'+str(c))
                f.write(' \n')
            if bigleap(notebefore, note)==6 or bigleap(notebefore, note)==12 or bigleap(notebefore, note)==-12:
                # print("special leaps detected:"+str(bigleap(notebefore, note)))
                if recover(bigleap(notebefore, note), note, noteafter)== False:
                    f.write('no recovery, break:'+str(c))
                    f.write(' \n')

            if repeatnote(notebefore, note) == True:
                flag=True
                break
            if parallelfifth(cf[i-1], notebefore, cf[i], note)==True:
                flag=True
                break
            if paralleloctave(cf[i-1], notebefore, cf[i], note)==True:
                flag=True
                break
            if bigleap(notebefore, note)==True:
                flag=True
                break
            if bigleap(notebefore, note)==6 or bigleap(notebefore, note)==12 or bigleap(notebefore, note)==-12:
                if recover(bigleap(notebefore, note), note, noteafter)== False:
                    flag=True
                    break

        if flag == False:
            if repeatnote(plist[-2], plist[-1]) == True:
                f.write('Repeat note skipping lastnote:'+str(c))
                f.write(' \n')
            if parallelfifth(cf[-2], plist[-2], cf[-1], plist[-1])==True:
                f.write('parallelfifth skipping lastnote:'+str(c))
                f.write(' \n')
            if paralleloctave(cf[-2], plist[-2], cf[-1], plist[-1])==True:
                f.write('paralleloctave skipping lastnote:'+str(c))
                f.write(' \n')
            if bigleap(plist[-2], plist[-1])==True:
                f.write('Leap is too big skipping lastnote:'+str(c))
                f.write(' \n')
            if bigleap(plist[-2], plist[-1])==6 or bigleap(plist[-2], plist[-1])==12 or bigleap(plist[-2], plist[-1])==-12:
                f.write('no recovery, break lastnote:'+str(c))
                f.write(' \n')

            if repeatnote(plist[-2], plist[-1]) == True:
                flag=True
            if parallelfifth(cf[-2], plist[-2], cf[-1], plist[-1])==True:
                flag=True
            if paralleloctave(cf[-2], plist[-2], cf[-1], plist[-1])==True:
                flag=True
            if bigleap(plist[-2], plist[-1])==True:
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

def secondspeciesabove(cf):
    o=0
    answer=[]
    possibilities=[]

    possibilities.append(getupperfirstnote2(cf[0]))
    for n in range(1,2*(len(cf))-4):
        # print("The nth note: "+str(n))
        if n % 2 == 1:
            possibilities.append(getabovenotes2(cf[o]))
            o=o+1
        else:
            possibilities.append(getaboveharmonic2(cf[o]))

    temp=[]
    temp.append(getabovefifth(cf[-2]))
    possibilities.append(temp)

    possibilities.append(getabovesixth(cf[-2]))

    temp=[]
    temp.append(getaboveoctave(cf[-1]))
    possibilities.append(temp)
    allpossibilities=getallpath(possibilities)

    c=0
    f = open('test4secondlog', 'w')

    for plist in allpossibilities:
        flag=False
        c=c+1
        print("running index:" +str(c))
        print("running answer"+str(plist))

        if exposedtritone(plist):
            f.write('tritone')
            break

        for i in range(1,2*len(cf)-2):
            note=plist[i]
            notebefore=plist[i-1]
            notebefore2=plist[i-2]
            noteafter=plist[i+1]
            o=int(math.floor(i/2))

            if repeatnote(notebefore, note) == True:
                f.write('Repeat note skipping')
                f.write(' \n')
            if i % 2 ==0:
                if parallelfifth(cf[o-1], notebefore2, cf[o], note)==True:
                    f.write('parallelfifth skipping')
                    f.write(' \n')
                if paralleloctave(cf[o-1], notebefore2, cf[o], note)==True:
                    f.write('paralleloctave skipping')
                    f.write(' \n')
            if ifinharmonic(cf[o],note)==True:
                if approleftstep(notebefore, note, noteafter)==False:
                    f.write('not approching by step')
                    f.write(' \n')
            if bigleap(notebefore, note)==True:
                f.write('Leap is too big skipping')
                f.write(' \n')
            if bigleap(notebefore, note)==6 or bigleap(notebefore, note)==12 or bigleap(notebefore, note)==-12:
                if recover(bigleap(notebefore, note), note, noteafter)== False:
                    f.write('no recovery, break')
                    f.write(' \n')

            if repeatnote(notebefore, note) == True:
                flag=True
                break
            if i % 2 ==0:
                if parallelfifth(cf[o-1], notebefore2, cf[o], note)==True:
                    flag=True
                    break
                if paralleloctave(cf[o-1], notebefore2, cf[o], note)==True:
                    flag=True
                    break
            if ifinharmonic(cf[o],note)==True:
                if approleftstep(notebefore, note, noteafter)==False:
                    flag=True
                    break
            if bigleap(notebefore, note)==True:
                flag=True
                break
            if bigleap(notebefore, note)==6 or bigleap(notebefore, note)==12 or bigleap(notebefore, note)==-12:
                if recover(bigleap(notebefore, note), note, noteafter)== False:
                    flag=True
                    break
        if flag == False:
            if repeatnote(plist[-2], plist[-1]) == True:
                f.write('Repeat note skipping')
                f.write(' \n')
            if parallelfifth(cf[-2], plist[-3], cf[-1], plist[-1])==True:
                f.write('parallelfifth skipping')
                f.write(' \n')
            if paralleloctave(cf[-2], plist[-3], cf[-1], plist[-1])==True:
                f.write('paralleloctave skipping')
                f.write(' \n')
            if ifinharmonic(cf[-2],plist[-2])==True:
                if approleftstep(plist[-3], plist[-2], plist[-1])==False:
                    f.write('not approching by step')
                    f.write(' \n')
            if bigleap(plist[-2], plist[-1])==True:
                f.write('Leap is too big skipping')
                f.write(' \n')
            if bigleap(plist[-3], plist[-2])==True:
                f.write('Leap is too big skipping')
                f.write(' \n')

            if repeatnote(plist[-2], plist[-1]) == True:
                flag=True
            if parallelfifth(cf[-2], plist[-3], cf[-1], plist[-1])==True:
                flag=True
            if paralleloctave(cf[-2], plist[-3], cf[-1], plist[-1])==True:
                flag=True
            if ifinharmonic(cf[-2],plist[-2])==True:
                if approleftstep(plist[-3], plist[-2], plist[-1])==False:
                    flag=True
            if bigleap(plist[-2], plist[-1])==True:
                flag=True
            if bigleap(plist[-3], plist[-2])==True:
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

def fromlisttostream(answer):
    print('total possible cpt: '+str(len(answer)))
    cp=music21.stream.Stream()
    index=randint(0, len(answer))
    picked=list(answer[index])
    for notes in picked:
        cp.append(notes)
    return cp

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

# The cantus firmus file loading
path='/Users/IrisYupingRen/Dropbox/counterpoint/cf/test4.xml'
inputnotes=getinput(path)
# Get the counterpoints and randomly select one and then make it a stream of music21
cp=fromlisttostream(secondspeciesabove(inputnotes))
# Combine the two voice
score=combinecfcp(inputnotes,cp)
# Display the randomly picked counterpoint
score.show()

# Write the randomly picked answer to a midi file
midifile= music21.midi.translate.streamToMidiFile(score)
midifile.open('/Users/IrisYupingRen/Dropbox/counterpoint/test4secondspecies.mid', 'wb')
midifile.write()
midifile.close()