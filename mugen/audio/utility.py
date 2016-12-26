import sys
import essentia
import essentia.standard

def load_audio(audio_file):
    try:
        loader = essentia.standard.MonoLoader(filename = audio_file)
    except Exception as e:
        print("Error reading audio file '{}'. Cannot continue. Error: {}".format(audio_file, e))
        sys.exit(1)
    else:
    	audio = loader()
    	return audio
