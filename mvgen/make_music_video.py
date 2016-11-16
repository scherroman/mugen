import essentia
import essentia.standard

loader = essentia.standard.MonoLoader(filename = 'mp3s/First Rave (Communion).mp3')
audio = loader()

print audio

rhythm_loader = essentia.standard.RhythmExtractor2013()
rhythm = rhythm_loader(audio)

print rhythm

# help(rhythm)

print rhythm[1]
print rhythm[5]