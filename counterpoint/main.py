import music21
import sys
import os

from generator import Generator

# Ensure argument list is correct length.
if len(sys.argv) != 3:
    print("Usage: python counterpoint.py <input_file> <output_file>")
    sys.exit()

# Check input file exists.
path = sys.argv[1]
if not os.path.isfile(path):
    print(f"Error: Input file '{path}' does not exist.")
    sys.exit()

# The cantus firmus file loading
inputnotes = Generator.get_input(path)
# Get the counterpoints and randomly select one and then make it a stream of music21
cp=Generator.fromlisttostream(Generator.secondspeciesabove(inputnotes))
# Combine the two voice
score=Generator.combinecfcp(inputnotes,cp)
# Display the randomly picked counterpoint
score.show()

# Write the randomly picked answer to a midi file
midifile=music21.midi.translate.streamToMidiFile(score)
midifile.open(sys.argv[2], 'wb')
midifile.write()
midifile.close()
