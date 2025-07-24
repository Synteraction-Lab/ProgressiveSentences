from utilities import file_utility
import pprint

_L2_SENTENCE_CSV_FILE = 'text/L2-sentences.csv'
'''
L2,Word-gap-millis
This is a sample.,0
This is, 200
'''

import mark_answers

_PARTICIPANT_L2_TEXT_STYLE_MAPPING = mark_answers._PARTICIPANT_L2_TEXT_STYLE_MAPPING
_ALL_STYLES = mark_answers.get_all_styles()


def count_style_details(participant_id: str, l2_texts: list) -> dict[str: int]:
    print(f"count_style_details for {participant_id}")

    _l2_text_style_map = _PARTICIPANT_L2_TEXT_STYLE_MAPPING[participant_id]
    _all_l2_texts = list(_l2_text_style_map.keys())
    # print(_all_l2_texts)

    _style_marks = {f'{_style}-{category}': 0 for _style in _ALL_STYLES
                    for category in ['Words-Max', 'Sentences-Max', 'Phases-Max']}

    _style_categories = []

    for _l2_text in l2_texts:
        _l2_text = mark_answers.get_clean_text(_l2_text)

        _l2_words = mark_answers.get_supported_words(_l2_text)
        _l2_word_count = len(_l2_words)

        if _l2_word_count == 0:
            raise Exception(f"Unsupported L2 text: {_l2_text}")

        _is_known_text = _l2_text in _all_l2_texts

        if _is_known_text:
            _style = _l2_text_style_map[_l2_text]
            category = 'Words' if _l2_word_count == 1 else 'Sentences'
            _style_marks[f'{_style}-{category}-Max'] += _l2_word_count
        else:
            for _l2_word in _l2_words:
                _style = _l2_text_style_map.get(_l2_word)
                print(_l2_word, _style)
                _style_marks[f'{_style}-Phases-Max'] += 1

    return _style_marks


if __name__ == "__main__":
    _participant_id = 'p901'

    _l2_sentences = file_utility.load_first_column_from_csv(_L2_SENTENCE_CSV_FILE)
    styles_details = count_style_details(_participant_id, _l2_sentences)
    pprint.pprint(styles_details, sort_dicts=False)
