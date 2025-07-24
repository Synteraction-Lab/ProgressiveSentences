from utilities import file_utility, openai_utility, google_cloud_utility
from time import sleep

_ENABLE_GOOGLE_CLOUD_TTS = False

_L2_SENTENCE_CSV_FILE = 'text/L2-sentences.csv'
'''
L2,Word-gap-millis
This is a sample.,0
This is, 200
'''

_AUDIO_DIRECTORY = "output/audio"

if __name__ == "__main__":

    # load L1 sentences and word gaps
    l2_sentences, word_gaps = file_utility.load_first_second_colum_from_csv(_L2_SENTENCE_CSV_FILE)

    for sentence, word_gap in zip(l2_sentences, word_gaps):
        if _ENABLE_GOOGLE_CLOUD_TTS:
            google_cloud_utility.save_tts_audio(text=sentence, word_gap_millis=word_gap, directory=_AUDIO_DIRECTORY)
        else:
            openai_utility.save_tts_audio(text=sentence, word_gap_millis=word_gap, directory=_AUDIO_DIRECTORY)

        sleep(0.2)  # Sleep for 0.2 seconds to avoid rate limiting
