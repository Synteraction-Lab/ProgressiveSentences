from utilities import file_utility
import os

from google.cloud import texttospeech

_AUDIO_FILE_SUFFIX = ""  # modify according to needs

GOOGLE_CLOUD_CREDENTIAL_FILE = "google_cloud_credentials.json"


def _set_api_key():
    credential_file = file_utility.get_credential_file_path(GOOGLE_CLOUD_CREDENTIAL_FILE)
    # The Google Cloud Library looks for this "GOOGLE_APPLICATION_CREDENTIALS" in
    # the environment variable by default (source: https://cloud.google.com/docs/authentication/application-default-credentials)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_file


_set_api_key()
# Set up the TTS client
_client = texttospeech.TextToSpeechClient()

# Configure the voice for Norwegian (e.g., Norwegian Bokmål)
_VOICE = texttospeech.VoiceSelectionParams(
    language_code="nb-NO",  # Norwegian Bokmål
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
)

# Configure the audio settings
_AUDIO_CONFIG = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=0.9  # Set the speed here (0.9 is 90% of the normal speed)
)


def remove_unsupported_characters(text):
    return text.replace("?", "").replace("!", "").replace(".", "").replace(",", "").replace(":", "").replace(";", "")


def create_ssml_words_with_breaks(text, word_gap_millis):
    words = text.split()
    words = [word.capitalize() for word in words]  # Capitalize each word
    word_gap_tag = f'. '  # f'. <break time="{word_gap_millis}ms"/>'
    text_with_breaks = word_gap_tag.join(words)
    if not text_with_breaks.endswith('.'):
        text_with_breaks += '.'  # Add a period at the end

    return f"""
        <speak>
           {text_with_breaks}
        </speak>
    """


def save_tts_audio(text, file_name=None, word_gap_millis=0, directory=None):
    '''
        text: can be any string or ssml_text
        file_name: file name to save the audio
        word_gap_millis: the gap between individual words in milliseconds (default = 0; i.e., no extra gaps)

        e.g.,;
        ssml_text = """
        <speak>
            This is normal speed.<break time="1s"/>
            <prosody rate="slow">This is spoken slowly.</prosody><break time="500ms"/>
            <prosody rate="80%">This is at 80 percent of normal speed.</prosody>
        </speak>
        """
    '''

    _file_name = file_name
    if _file_name is None or _file_name == "":
        _file_name = text

    if _AUDIO_FILE_SUFFIX is not None and _AUDIO_FILE_SUFFIX != "":
        _file_name = f"{_file_name}-{_AUDIO_FILE_SUFFIX}"

    _file_name = remove_unsupported_characters(_file_name)
    _file_name = f"{_file_name}.mp3"

    speech_file_path = file_utility.get_audio_file_path(directory, _file_name)

    text_to_speech = text
    if word_gap_millis > 0:
        text_to_speech = create_ssml_words_with_breaks(text, word_gap_millis)

    print('text_to_speech: ', text_to_speech)

    synthesis_input = texttospeech.SynthesisInput(text=text_to_speech)

    # Perform the text-to-speech request
    response = _client.synthesize_speech(
        input=synthesis_input,
        voice=_VOICE,
        audio_config=_AUDIO_CONFIG
    )

    file_utility.write_data(speech_file_path, response.audio_content)

    print(f"Audio saved at '{speech_file_path}'")
