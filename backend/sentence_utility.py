from backend.models import Word, Sentence, Participant
import pandas as pd
import re
from io import StringIO
import logging
from typing import List, Dict, Any
from utilities import file_utility

logger = logging.getLogger()

_SENTENCES_FILE = 'backend/data/Sentence_elements.csv'
csv_text_sentence = """
ID,L1,L2,Image,Part1.L1,Part1.L2,Part1.Image,Part2.L1,Part2.L2,Part2.Image
1,A bear catches a rabbit.,En joam coff en poggel,bear-catches-rabbit,A bear catches,En joam coff,bear-catches,a rabbit,en poggel,rabbit
2,A bird flies in the sky.,En bomp jee ep snu phoe,bird-fly-sky,A bird flies,En bomp jee,bird-flies,in the sky,ep snu phoe,sky
"""

_PARTICIPANTS_FILE = 'backend/data/Participant_style.csv'
csv_text_participants = """
Participant,Style.1,Sentences.1,Style.2,Sentences.2,Style.3,Sentences.3
p201,S1,"1,2",S2,"1,2",S3,"1,2"
p202,S2,"1,2",S3,"1,2",S4,"1,2"
"""

_SESSION_START_AUDIO = "audios/Session starts.mp3"
_SESSION_END_AUDIO = "audios/Session ends.mp3"

_SESSION_AUDIO = "audios/two_beep.mp3"

_BREAK_TIME_TEXT = "Break time! Questionnaire."

# DO NOT modify these constants
_SESSION_END_TEXT = "Session ends"
_SESSION_START_TEXT = "Session starts"

_OPACITY_TAG = "style='opacity:0.5'"

_TRAINING_PARTICIPANT_IDS = ['p0', 'px']


def get_session_instructions(participant):
    return f"[{participant}] Use in full screen"


def get_all_styles():
    return ["S1", "S2", "W1", "W2"]


def clean_audio(audio_text):
    return (audio_text.replace("?", "").replace("!", "").replace(".", "")
            .replace(",", "").replace(":", "").replace(";", ""))


def is_not_empty(value):
    return pd.notna(value) and value != ""


def get_text(value):
    return str(value) if is_not_empty(value) else ""


def get_l1_audio(value):
    return f"audios/l1/{clean_audio(value)}.mp3" if is_not_empty(value) else ""


def get_l2_audio(value):
    return f"audios/l2/{clean_audio(value)}.mp3" if is_not_empty(value) else ""


def get_image(value):
    return f"images/{value}.png" if is_not_empty(value) else ""


def get_start_session_sentence(participant="", duration=4000) -> Sentence:
    return Sentence(
        id=0,
        subWords=[
            Word(
                id=0,
                foreignText=_SESSION_START_TEXT,
                englishTranslation=get_session_instructions(participant),
                foreignPronunciation=_SESSION_START_AUDIO,
                englishPronunciation="",
                displayDuration=duration,
                imageUrl=""
            ),
        ]
    )


def get_end_session_sentence(participant="", duration=15000) -> Sentence:
    return Sentence(
        id=1,
        subWords=[
            Word(
                id=1,
                foreignText=_SESSION_END_TEXT,
                englishTranslation=get_text(participant),
                foreignPronunciation=_SESSION_END_AUDIO,
                englishPronunciation="",
                displayDuration=duration,
                imageUrl=""
            )
        ]
    )


def get_break_time_sentence(style="", session_number=None, duration=5000) -> Sentence:
    return Sentence(
        id=2,
        subWords=[
            Word(
                id=2,
                foreignText=f"<custom-color {_OPACITY_TAG}>{_BREAK_TIME_TEXT}</custom-color>",
                englishTranslation=f"<custom-color {_OPACITY_TAG}>[Finished] style: {style}, session: {session_number}</custom-color>",
                foreignPronunciation="",
                englishPronunciation="",
                displayDuration=duration,
                imageUrl=""
            )
        ]
    )


def get_empty_sentence(duration=1000) -> Sentence:
    return Sentence(
        id=-1,
        subWords=[
            get_empty_word(duration=duration)
        ]
    )


def get_empty_word(duration=3000) -> Word:
    return Word(
        id=-1,
        foreignText="",
        englishTranslation="",
        foreignPronunciation="",
        englishPronunciation="",
        displayDuration=duration,
        imageUrl=""
    )


def extract_number_or_default(string, default=10):
    match = re.search(r'\d+', string)
    return (default + int(match.group())) if match else default


def get_session_sentence(style, session_number, duration=2000) -> Sentence:
    style_number = extract_number_or_default(style)
    return Sentence(
        id=style_number,
        subWords=[
            Word(
                id=style_number,
                foreignText=f"Style: {style}",
                englishTranslation=f"[New] <custom-color {_OPACITY_TAG}>Session: {session_number}</custom-color>",
                foreignPronunciation=_SESSION_AUDIO,
                englishPronunciation="",
                displayDuration=duration,
                imageUrl=""
            )
        ]
    )


def get_sentence(style, sentence_id, sentence_l2, sentence_l1, sentence_image, sentence_parts: dict,
                 repeat=False) -> Sentence:
    '''
    CV: The total display duration and gap space are similar between conditions

    S0 (Full Sentence): Present the full concept -> Repeat it.
    S1 = W1 (IndividualToFullSequential, gap = 0): Present an individual concept -> Sequentially build the full concept with a highlight.
    S2 = W2 (IndividualToFullSequential, gap = 4): Present an individual concept -> Sequentially build the full concept with a highlight.

    '''

    l2_audio_duration = 4000

    if style == "S1" or style == "W1":  # 3 words + 1 sentence
        display_duration = 4000
        empty_duration = 50
        end_duration = 4000 * 4 - empty_duration * 3
    elif style == "S2" or style == "W2":  # 3 words + 1 sentence
        display_duration = 4000
        empty_duration = 4000
        end_duration = empty_duration
    elif style == "S0":  # 1 sentence + 1 repeat
        display_duration = 8000
        empty_duration = 8000
        end_duration = empty_duration
    else:
        raise Exception(f"Unknown style: {style}")

    additional_sentence_duration = 1000 * 3
    additional_word_duration = additional_sentence_duration // 3

    sen_id = int(sentence_id)
    l2_text = get_text(sentence_l2)
    l2_audio = get_l2_audio(l2_text)
    l1_text = get_text(sentence_l1)
    l1_audio = get_l1_audio(l1_text)
    image = get_image(sentence_image)

    base_id = sen_id * 100
    part1_l2_text = get_text(sentence_parts['phase_2'][1]['L2'])
    part1_l2_audio = get_l2_audio(part1_l2_text)
    part1_l1_text = get_text(sentence_parts['phase_2'][1]['L1'])
    part1_l1_audio = get_l1_audio(part1_l1_text)
    part1_image = get_image(sentence_parts['phase_2'][1]['Image'])

    part2_l2_text = get_text(sentence_parts['phase_2'][2]['L2'])
    part2_l2_audio = get_l2_audio(part2_l2_text)
    part2_l1_text = get_text(sentence_parts['phase_2'][2]['L1'])
    part2_l1_audio = get_l1_audio(part2_l1_text)
    part2_image = get_image(sentence_parts['phase_2'][2]['Image'])

    part3_l2_text = get_text(sentence_parts['phase_2'][3]['L2'])
    part3_l2_audio = get_l2_audio(part3_l2_text)
    part3_l1_text = get_text(sentence_parts['phase_2'][3]['L1'])
    part3_l1_audio = get_l1_audio(part3_l1_text)
    part3_image = get_image(sentence_parts['phase_2'][3]['Image'])

    if style == 'S0':
        return Sentence(
            id=sen_id,
            subWords=[
                get_empty_word(duration=additional_word_duration),
                Word(
                    id=base_id + 1,
                    foreignText=l2_text,
                    englishTranslation="",
                    foreignPronunciation=l2_audio,
                    englishPronunciation="",
                    displayDuration=l2_audio_duration,
                    imageUrl=image
                ),
                Word(
                    id=base_id + 2,
                    foreignText=l2_text,
                    englishTranslation=l1_text,
                    foreignPronunciation="",
                    englishPronunciation=l1_audio,
                    displayDuration=display_duration + (display_duration - l2_audio_duration),
                    imageUrl=image
                ),
                get_empty_word(duration=empty_duration),
                Word(
                    id=base_id + 3,
                    foreignText=l2_text,
                    englishTranslation="",
                    foreignPronunciation=l2_audio,
                    englishPronunciation="",
                    displayDuration=l2_audio_duration,
                    imageUrl=image
                ),
                Word(
                    id=base_id + 4,
                    foreignText=l2_text,
                    englishTranslation=l1_text,
                    foreignPronunciation="",
                    englishPronunciation=l1_audio,
                    displayDuration=display_duration + (
                            display_duration - l2_audio_duration) + additional_sentence_duration,
                    imageUrl=image
                ),
                get_empty_word(duration=end_duration),
                get_empty_word(duration=additional_word_duration),
            ]
        )

    if style == 'S1' or style == 'W1' or style == 'S2' or style == 'W2':
        # FIXME: This hack uses to enable coherent images
        part1_image = get_image(sentence_parts['phase_2'][1]['Image'])
        part2_image = get_image(sentence_parts['phase_1'][1]['Image'])
        part3_image = get_image(sentence_parts['phase_1'][2]['Image'])

        return Sentence(
            id=sen_id,
            subWords=[
                get_empty_word(duration=additional_word_duration),
                Word(
                    id=base_id + 1,
                    foreignText=part1_l2_text,
                    englishTranslation="",
                    foreignPronunciation=part1_l2_audio,
                    englishPronunciation="",
                    displayDuration=l2_audio_duration,
                    imageUrl=part1_image
                ),
                Word(
                    id=base_id + 2,
                    foreignText=part1_l2_text,
                    englishTranslation=part1_l1_text,
                    foreignPronunciation="",
                    englishPronunciation=part1_l1_audio,
                    displayDuration=display_duration + (display_duration - l2_audio_duration),
                    imageUrl=part1_image
                ),
                get_empty_word(duration=empty_duration),
                Word(
                    id=base_id + 3,
                    foreignText=f"<custom-color {_OPACITY_TAG}>{part1_l2_text}</custom-color> {part2_l2_text}",
                    englishTranslation="",
                    foreignPronunciation=part2_l2_audio,
                    englishPronunciation="",
                    displayDuration=l2_audio_duration,
                    imageUrl=part2_image
                ),
                Word(
                    id=base_id + 4,
                    foreignText=f"<custom-color {_OPACITY_TAG}>{part1_l2_text}</custom-color> {part2_l2_text}",
                    englishTranslation=f"<custom-color {_OPACITY_TAG}>{part1_l1_text}</custom-color> {part2_l1_text}",
                    foreignPronunciation="",
                    englishPronunciation=part2_l1_audio,
                    displayDuration=display_duration + (display_duration - l2_audio_duration),
                    imageUrl=part2_image
                ),
                get_empty_word(duration=empty_duration),
                Word(
                    id=base_id + 5,
                    foreignText=f"<custom-color {_OPACITY_TAG}>{part1_l2_text} {part2_l2_text}</custom-color> {part3_l2_text}",
                    englishTranslation="",
                    foreignPronunciation=part3_l2_audio,
                    englishPronunciation="",
                    displayDuration=l2_audio_duration,
                    imageUrl=f"{part2_image}|{part3_image}"
                ),
                Word(
                    id=base_id + 6,
                    foreignText=f"<custom-color {_OPACITY_TAG}>{part1_l2_text} {part2_l2_text}</custom-color> {part3_l2_text}",
                    englishTranslation=f"<custom-color {_OPACITY_TAG}>{part1_l1_text} {part2_l1_text}</custom-color> {part3_l1_text}",
                    foreignPronunciation="",
                    englishPronunciation=part3_l1_audio,
                    displayDuration=display_duration + (display_duration - l2_audio_duration),
                    imageUrl=f"{part2_image}|{part3_image}"
                ),
                get_empty_word(duration=empty_duration),
                Word(
                    id=base_id + 7,
                    foreignText=l2_text,
                    englishTranslation="",
                    foreignPronunciation=l2_audio,
                    englishPronunciation="",
                    displayDuration=l2_audio_duration,
                    imageUrl=image
                ),
                Word(
                    id=base_id + 8,
                    foreignText=l2_text,
                    englishTranslation=l1_text,
                    foreignPronunciation="",
                    englishPronunciation="",
                    displayDuration=display_duration + (
                            display_duration - l2_audio_duration) + additional_sentence_duration,
                    imageUrl=image
                ),
                get_empty_word(duration=end_duration),
                get_empty_word(duration=additional_word_duration),
            ]
        )


def get_participant_sentences(participant_id: str, styles_sentences: Dict[str, Any],
                              sentence_content: Dict[int, tuple]) -> Participant:
    sentences: List[Sentence] = []

    # append the start sentence
    sentences.append(get_start_session_sentence(duration=3000, participant=participant_id))

    for i in range(1, len(get_all_styles()) + 1):
        style = styles_sentences[f'Style.{i}']
        sentence_ids = styles_sentences[f'Sentences.{i}'].split(',')

        # append empty sentence before session
        sentences.append(get_empty_sentence(duration=1000))

        # append the session sentence, to stop if needed
        sentences.append(get_session_sentence(style, i, duration=4000))

        for sid in sentence_ids:
            sid = int(sid)
            sen_l2, sen_l1, sen_image, sen_parts = sentence_content[sid][1:]
            sentences.append(get_sentence(style, sid, sen_l2, sen_l1, sen_image, sen_parts))

        # append break time sentence end of session
        if participant_id not in _TRAINING_PARTICIPANT_IDS:
            sentences.append(get_break_time_sentence(style, i, 20000))

    # append the end sentence
    sentences.append(get_end_session_sentence(participant=participant_id, duration=10000))

    return Participant(participantId=participant_id, currentSentenceIndex=-1, sentences=sentences)


def get_all_sentences_content() -> dict[int, tuple[int, str, str, str, dict]]:
    logger.info("Reading sentences from csv file", _SENTENCES_FILE)
    # df_sentences = pd.read_csv(StringIO(csv_text_sentence))
    df_sentences = file_utility.read_csv(_SENTENCES_FILE)

    _sentences = {}
    for _, row in df_sentences.iterrows():
        _sentence_id = int(row['ID'])

        _sentence_l2 = row['L2']
        _sentence_l1 = row['L1']
        _sentence_image = row['Image']

        _sentence_parts = {
            "phase_1": {
                1: {
                    'L2': row['Part11.L2'],
                    'L1': row['Part11.L1'],
                    'Image': row['Part11.Image'],
                },
                2: {
                    'L2': row['Part12.L2'],
                    'L1': row['Part12.L1'],
                    'Image': row['Part12.Image'],
                },
            },
            "phase_2": {
                1: {
                    'L2': row['Part21.L2'],
                    'L1': row['Part21.L1'],
                    'Image': row['Part21.Image'],
                },
                2: {
                    'L2': row['Part22.L2'],
                    'L1': row['Part22.L1'],
                    'Image': row['Part22.Image'],
                },
                3: {
                    'L2': row['Part23.L2'],
                    'L1': row['Part23.L1'],
                    'Image': row['Part23.Image'],
                },
            },
            "words_1": {
                1: {
                    'L2': row['Word11.L2'],
                    'L1': row['Word11.L1'],
                    'Image': row['Word11.Image'],
                },
                2: {
                    'L2': row['Word12.L2'],
                    'L1': row['Word12.L1'],
                    'Image': row['Word12.Image'],
                },
            },
        }

        if is_not_empty(row['Word13.L1']):
            _sentence_parts['words_1'][3] = {
                'L2': row['Word13.L2'],
                'L1': row['Word13.L1'],
                'Image': row['Word13.Image'],
            }

        _sentences[_sentence_id] = (_sentence_id, _sentence_l2, _sentence_l1, _sentence_image, _sentence_parts)

    return _sentences


def get_all_participants_content() -> dict[str, Dict[str, Any]]:
    logger.info("Reading participants from csv file", _PARTICIPANTS_FILE)
    # df_participants = pd.read_csv(StringIO(csv_text_participants))
    df_participants = file_utility.read_csv(_PARTICIPANTS_FILE)

    _participants = {}

    for _, row in df_participants.iterrows():
        _participant_id = get_text(row['Participant'])
        _styles_sentences = row
        _participants[_participant_id] = _styles_sentences

    return _participants


def get_all_participants_sentences():
    sentences_content = get_all_sentences_content()
    participants_content = get_all_participants_content()

    participants_sentences = {}

    for participant_id, styles_sentences in participants_content.items():
        participants_sentences[participant_id] = get_participant_sentences(participant_id,
                                                                           styles_sentences,
                                                                           sentences_content)

    return participants_sentences


if __name__ == "__main__":
    print(get_all_participants_sentences())
