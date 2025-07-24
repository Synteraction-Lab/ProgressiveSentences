# encoding: utf-8
from collections import Counter

import pandas as pd

from backend.sentence_utility import get_all_sentences_content, get_all_participants_content, get_all_styles
from generate_sentences import get_l2_l1_mapping, get_mapped_sentence
from utilities import file_utility

_L2_IGNORE_WORDS = ['sa', 'Sa', 'sas', 'chu', 'Chu', 'chus', 'en', 'En', 'snu', 'Snu', 'er', 'eb',
                    'ep', 'fra', 'ures', 'ig', 'x', 'X', 'xx', 'xxx',
                    ]

_PARTICIPANTS_ANSWERS_FILE = 'user_data/participants_answers.csv'
'''
L2,L1,p101,p102,p103,p104,p105
joam,bear,,bear,bear,,cat
nend,park,green,park,,,park
En wims seps ep snu nend,A dog runs in the park,A dog,run,park,cat eats
'''

_PARTICIPANTS_RESULTS_FILE = 'output/participants_answers_marks.csv'
'''
L2,L1,p101,p101-Marks,p102,p102-Marks,p103,p103-Marks
'''

_PARTICIPANTS_RESULT_SUMMARY_FILE = 'output/participants_marks_summary.csv'
'''
Participant,S1-Words,S2-Words,S3-Words,S1-Sentences,S2-Sentences,S3-Sentences,S1-Unseen,S2-Unseen,S3-Unseen
'''


def get_clean_text(text):
    if pd.isna(text):
        return ""

    _clean_text = text
    _clean_text = _clean_text.strip()
    _clean_text = _clean_text.replace("?", "").replace("!", "").replace(".", "") \
        .replace(",", "").replace(":", "").replace(";", "")
    _clean_text = _clean_text.lower()

    return _clean_text


def get_supported_words(sentence):
    _clean_sentence = sentence
    _words = _clean_sentence.split()
    _filtered_words = [word.strip() for word in _words if word not in _L2_IGNORE_WORDS]
    return _filtered_words


_SENTENCES_FILE = 'backend/data/Sentence_elements.csv'
'''
ID,L2,L1,Image
1,En joam coff en poggel.,A bear catches a rabbit.,image1
2,En wims seps ep snu nend.,A dog runs in the park.,image2
'''

_SENTENCES_FILE_DATA = get_all_sentences_content()  # { SENTENCE_ID: (SENTENCE_ID, L2, L1, Image, ...) )}

_ID_L2_SENTENCE_MAPPING = {key: value[1] for key, value in
                           _SENTENCES_FILE_DATA.items()}  # {SentenceId: L2Sentence, ...}


# print("_L2_ID_SENTENCE_MAPPING", _L2_ID_SENTENCE_MAPPING)


def check_duplicates():
    _all_l2_sentences = list(_ID_L2_SENTENCE_MAPPING.values())
    # print("_all_l2_sentences", _all_l2_sentences)

    _all_l2_sentences_clean = [get_clean_text(sentence) for sentence in _all_l2_sentences]
    # print("_all_l2_sentences_clean", _all_l2_sentences_clean)

    _all_l2_words = [word for sentence in _all_l2_sentences_clean for word in
                     get_supported_words(sentence)]
    # print("_all_l2_words", _all_l2_words)

    # Find and print the duplicates
    word_counts = Counter(_all_l2_words)
    duplicates = {word: count for word, count in word_counts.items() if count > 1}
    if duplicates:
        print("Duplicate words and their counts:")
        for word, count in duplicates.items():
            print(f"{word}: {count}")


# L2 to L1 mapping
_L2_L1_MAPPING = get_l2_l1_mapping()


# print("_L2_L1_MAPPING", _L2_L1_MAPPING)

def get_l1_text(l2_text):
    return get_mapped_sentence(l2_text, _L2_L1_MAPPING)


_L1_IGNORE_WORDS = [get_l1_text(l2) for l2 in _L2_IGNORE_WORDS]

_PARTICIPANTS_FILE = 'backend/data/Participant_style.csv'
'''
Participant,Style.1,Sentences.1,Style.2,Sentences.2,Style.3,Sentences.3,Style.4,Sentences.4,Style.5,Sentences.5
p101,S1,"1,2",S2,"1,2",S3,"1,2",S4,"1,2",S5,"1,2"
p102,S2,"1,2",S3,"1,2",S4,"1,2",S5,"1,2",S1,"1,2"
'''

_PARTICIPANTS_FILE_DATA = get_all_participants_content()  # {ParticipantID: {Participant: x, Style.1: , Sentences.1, ...}}

_PARTICIPANT_SENTENCE_ID_STYLE_MAPPING = {}  # {ParticipantID: {SentenceID: Style, ...}}
for _participant_id, _styles in _PARTICIPANTS_FILE_DATA.items():
    _style_sentence_map = {}

    # Iterate over the columns in pairs (Style.X, Sentences.X)
    for i in range(1, len(get_all_styles()) + 1):
        _style = _styles[f'Style.{i}']
        _sentence_ids = _styles[f'Sentences.{i}']

        # Split the sentence IDs and map each to the corresponding style
        for _sentence_id in _sentence_ids.split(','):
            _sentence_id_int = int(_sentence_id)
            _style_sentence_map[_sentence_id_int] = _style

    # Add the participant's mapping to the dictionary
    _PARTICIPANT_SENTENCE_ID_STYLE_MAPPING[_participant_id] = _style_sentence_map

# print("_PARTICIPANT_SENTENCE_ID_STYLE_MAPPING", _PARTICIPANT_SENTENCE_ID_STYLE_MAPPING)


_PARTICIPANT_L2_TEXT_STYLE_MAPPING = {}  # {ParticipantID: {L2_Sentence: Style, L2_Word: Style ...}}

for _participant_id, _sentence_style_map in _PARTICIPANT_SENTENCE_ID_STYLE_MAPPING.items():
    _l2_word_style_map = {}

    for _sentence_id, _style in _sentence_style_map.items():
        _l2_sentence = _ID_L2_SENTENCE_MAPPING[_sentence_id]
        _l2_sentence = get_clean_text(_l2_sentence)
        # assign sentence to style
        _l2_word_style_map[_l2_sentence] = _style
        # assign word to style
        for _l2_word in get_supported_words(_l2_sentence):
            _l2_word_style_map[_l2_word] = _style

        # print(_sentence_id, _l2_word_style_map)

    _PARTICIPANT_L2_TEXT_STYLE_MAPPING[_participant_id] = _l2_word_style_map

    # print("_PARTICIPANT_L2_TEXT_STYLE_MAPPING", _PARTICIPANT_L2_TEXT_STYLE_MAPPING)


def get_manual_mark(correct_text: str, given_text: str, max_marks: int, is_known_text: bool,
                    expected_correct_words: list[str]):
    _expected_words_string = ",".join(expected_correct_words)
    _details = f"Seen Text: [{_expected_words_string}]" if is_known_text else f"Unseen Text: [{_expected_words_string}]"
    print(f'{_details}; Given: [{given_text}], Correct: [{correct_text}], Max: {max_marks}')

    _corrects = ["0"] * max_marks
    for index, _expected_word in enumerate(expected_correct_words):
        _corrects[index] = "0"
        for _given_word in given_text.split():
            if is_correct_text(_expected_word, _given_word) is True:
                _corrects[index] = "1"
                break
    _expected_marks_string = ",".join(_corrects)

    while True:
        _manual_marks = input(
            f"Input Marks (0-{max_marks}, separated by commas) [Suggested: {_expected_marks_string}]: ")
        try:
            if _manual_marks.strip() == "":
                continue

            if _manual_marks == "y":
                _manual_marks = _expected_marks_string

            _individual_marks = _manual_marks.split(',')

            if len(_individual_marks) != max_marks:
                print(f"Invalid individual inputs")
                continue

            _individual_marks = [int(value) for value in _individual_marks if value.strip()]

            if all(val in [0, 1] for val in _individual_marks) and sum(_individual_marks) <= max_marks:
                return _individual_marks
            else:
                print("Invalid input. Please enter only marks of 0 or 1.")
        except ValueError:
            print("Invalid input. Please enter numeric values only.")


def is_same_word_ignoring_plurality(correct_word, given_word):
    if len(correct_word.split()) != 1:
        raise Exception(f"Unsupported word comparison: {correct_word}, {given_word}")

    if f"{given_word}s" == correct_word or f"{given_word}es" == correct_word or given_word == f"{correct_word}s":
        return True
    elif (correct_word == "a" and given_word == "an") or (correct_word == "an" and given_word == "a"):
        return True
    elif (correct_word == "fly" and given_word == "flies") or (correct_word == "flies" and given_word == "fly"):
        return True
    elif (correct_word == "sky" and given_word == "skies") or (correct_word == "skies" and given_word == "sky"):
        return True
    else:
        return False


def is_correct_text(correct_text, given_text):
    if given_text is None:
        raise Exception(f"Unsupported None comparison: {correct_text}")

    if given_text == "" or given_text == "-" or given_text == "x" or given_text == "xx":
        return False
    elif given_text in _L1_IGNORE_WORDS:
        return False
    elif all(word in _L1_IGNORE_WORDS for word in given_text.split()):
        return False
    elif given_text == correct_text:
        return True
    elif len(correct_text.split()) == 1 and is_same_word_ignoring_plurality(correct_text, given_text):
        return True
    else:
        return None


def get_marks(correct_text: str, given_text: str, max_marks: int, is_known_text: bool,
              expected_correct_words: list[str]):
    correctness = is_correct_text(correct_text, given_text)

    if correctness is True:
        _mark = [1] * max_marks
        print(f"Mark {_mark}:: Given: [{given_text}], Correct: [{correct_text}]")
    elif correctness is False:
        _mark = [0] * max_marks
        print(f"Mark {_mark} :: Given: [{given_text}], Correct: [{correct_text}]")
    else:
        _mark = get_manual_mark(correct_text, given_text, max_marks, is_known_text, expected_correct_words)
        print(f"Mark {_mark} :: Given: [{given_text}], Correct: [{correct_text}]")

    return _mark


def mark_participant(participant_id: str, participant_answers_df: pd.DataFrame) -> tuple[
    list[int], list[str], dict]:
    print(f"\nmark_participant for {participant_id}")

    _l2_text_style_map = _PARTICIPANT_L2_TEXT_STYLE_MAPPING[participant_id]
    _all_l2_texts = list(_l2_text_style_map.keys())
    # print(_all_l2_texts)

    '''
    L2,L1,p101,p102,p103,p104,p105
    joam,bear,,bear,bear,,cat
    nend,park,green,park,,,park
    En wims seps ep snu nend,A dog runs in the park,A dog,run,park,cat eats
    '''
    _l2_texts = participant_answers_df['L2'].tolist()
    # print("_l2_texts", _l2_texts)

    # _l2_answers = participant_answers_df[f'{participant_id}'].tolist() # previous approach

    # Extract columns for the specific participant, and combine answers for the participant (union of results from all columns)
    _participant_columns = [col for col in participant_answers_df.columns if participant_id in col]

    if len(_participant_columns) == 0:
        raise Exception(f"No answers found for participant {participant_id}")

    _l2_answers = []
    for index, row in participant_answers_df.iterrows():
        combined_answer = ''  # Start with an empty string for each row
        for col in _participant_columns:
            if pd.notna(row[col]) and row[col] != '':
                combined_answer += str(row[col])
                # break  # Exit the loop once we find the first non-empty answer

        _l2_answers.append(combined_answer)  # Add the answer to the list

    print(f"L2 text: {len(_l2_texts)}, Answers: {len(_l2_answers)}")
    print("_l2_answers", _l2_answers)

    _style_marks = {f'{_sty}-{category}': 0 for _sty in get_all_styles()
                    for category in ['Words', 'Words-Max', 'Seen-Sentences', 'Seen-Sentences-Max',
                                     'Unseen-Sentences', 'Unseen-Sentences-Max']}

    _l2_marks = []
    _style_categories = []

    for index, (_l2_text, _answer_l1) in enumerate(zip(_l2_texts, _l2_answers)):
        _l2_text = get_clean_text(_l2_text)
        _correct_l1 = get_clean_text(get_l1_text(_l2_text))
        _answer_l1 = get_clean_text(_answer_l1)

        _expected_l2_words = get_supported_words(_l2_text)
        _l2_word_count = len(_expected_l2_words)

        if _l2_word_count == 0:
            raise Exception(f"Unsupported L2 text: {_l2_text}")

        _is_known_text = _l2_text in _all_l2_texts
        _max = _l2_word_count
        # print(index, _l2_text, _l2_word_count, _is_known_text)

        _expected_l1_words = [get_l1_text(_expected_l2_word) for _expected_l2_word in _expected_l2_words]

        _marks = get_marks(_correct_l1, _answer_l1, _max, _is_known_text, _expected_l1_words)
        # print(_marks)
        _l2_marks.append(sum(_marks))
        # print(f'Correct: [{_correct_l1}], Given: [{_answer_l1}], Actual Marks: {_l2_marks[index]}')

        if _is_known_text:
            _style = _l2_text_style_map[_l2_text]
            category = 'Words' if _l2_word_count == 1 else 'Seen-Sentences'
            _style_marks[f'{_style}-{category}'] += sum(_marks)
            _style_marks[f'{_style}-{category}-Max'] += _max

            _style_categories.append(f'{_style}-{category}')
        else:
            _individual_styles = []
            for _word_index, _l2_word in enumerate(_expected_l2_words):
                # print(_word_index, _l2_word)
                _style = _l2_text_style_map.get(_l2_word)
                _style_marks[f'{_style}-Unseen-Sentences'] += _marks[_word_index]
                _style_marks[f'{_style}-Unseen-Sentences-Max'] += 1

                _individual_styles.append(_style)

            _style_categories.append(",".join(_individual_styles))

    return _l2_marks, _style_categories, _style_marks


def write_results(participant_ids: list[str], participant_answers_df: pd.DataFrame):
    individual_results_df = participant_answers_df.copy()
    '''
    L2,L1,p101,p101-Marks,p102,p102-Marks,
    '''

    summary_results = []

    for participant_id in participant_ids:
        # Initialize dictionaries to store style-specific results
        session_results = {f'{style}': {'Participant': participant_id, 'Style': f'{style}'} for style in
                           get_all_styles()}

        _l2_marks, _style_categories, _style_marks = mark_participant(participant_id, individual_results_df)
        # Add the new marks as columns to the DataFrame
        individual_results_df[f'{participant_id}-Marks'] = _l2_marks
        individual_results_df[f'{participant_id}-Styles'] = _style_categories

        # Update the dictionary with style marks using the correct column names
        for key, value in _style_marks.items():
            # e.g., key=S3-Words, value = 0
            _style, _category = key.split('-', 1)
            if _style in session_results:
                # Combine the results from multiple days by accumulating them
                column_name = f'{_category}'
                if column_name in session_results[_style]:
                    session_results[_style][column_name] += value  # Accumulate the value
                else:
                    session_results[_style][column_name] = value
            # print(session_results)

        # Flatten the session_results dictionary into the summary results
        for session_key, session_data in session_results.items():
            summary_results.append(session_data)

    file_utility.write_data_to_csv(_PARTICIPANTS_RESULTS_FILE, individual_results_df)
    print(f"Individual results have been updated and saved to {_PARTICIPANTS_RESULTS_FILE}")

    # Set the 'Participant_ID' as the first column
    summary_results_df = pd.DataFrame(summary_results)
    '''
    Participant,Session (S1-S5), Words,Seen-Sentences, Unseen-Sentences
    '''

    file_utility.write_data_to_csv(_PARTICIPANTS_RESULT_SUMMARY_FILE, summary_results_df)
    print(f"Summary results have been updated and saved to {_PARTICIPANTS_RESULT_SUMMARY_FILE}")


if __name__ == "__main__":
    check_duplicates()

    # _participant_ids = ['px']
    _participant_ids = ['p901', 'p902', 'p903', 'p904', 'p905', 'p906', 'p907', 'p908', 'p909', 'p910', 'p911', 'p912']

    _participant_answers = file_utility.read_csv(_PARTICIPANTS_ANSWERS_FILE)
    write_results(_participant_ids, _participant_answers)
