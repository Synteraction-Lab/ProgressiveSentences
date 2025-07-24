from openai import OpenAI
from utilities import file_utility
import os

_AUDIO_FILE_SUFFIX = ""  # modify according to needs

OPENAI_CREDENTIAL_FILE = "openai_credential.json"

_MODEL = "tts-1"
# _MODEL = "tts-1-hd"
_VOICE = "nova"
_FORMAT = "mp3"
_SPEED = 0.9


def _set_api_key():
    credential = file_utility.read_json_file(
        file_utility.get_credential_file_path(OPENAI_CREDENTIAL_FILE))
    # The OpenAI Library looks for this "OPENAI_API_KEY" in
    # the environment variable by default
    os.environ["OPENAI_API_KEY"] = credential["openai_api_key"]


_set_api_key()
_client = OpenAI()


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

    response = _client.audio.speech.create(
        model=_MODEL,
        voice=_VOICE,
        input=text_to_speech,
        response_format=_FORMAT,
        speed=_SPEED
    )

    response.stream_to_file(speech_file_path)
    print(f"Audio saved at '{speech_file_path}'")
