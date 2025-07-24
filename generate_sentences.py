from utilities import file_utility

_L1_SENTENCE_CSV_FILE = 'text/L1-sentences.csv'
'''
L1-sentences
A bear catches a rabbit
A bird flies in the sky
'''

_L1_L2_MAPPING_CSV_FILE = 'text/L1-L2-mapping.csv'

_L1_WORDS, _L2_WORDS = file_utility.load_first_second_colum_from_csv(_L1_L2_MAPPING_CSV_FILE)
# print(_L2_WORDS, _L1_WORDS)

'''
L1,L2
he,sa
He,Sa
'''

_L1_L2_SENTENCE_CSV_FILE = 'output/L1-L2-sentences.csv'


def get_l1_l2_mapping():
    return {key: value for key, value in zip(_L1_WORDS, _L2_WORDS) if
            key is not None and value is not None}


def get_l2_l1_mapping():
    return {key: value for key, value in zip(_L2_WORDS, _L1_WORDS) if
            key is not None and value is not None}


def get_mapped_sentence(sentence, l1_l2_mapping):
    _texts = sentence.split()
    _mapped_texts = []
    for _text in _texts:
        _mapped_text = l1_l2_mapping.get(_text)
        if _mapped_text is not None:
            _mapped_texts.append(_mapped_text)
        else:
            # print(f"Word '{_text}' not found in the L1-L2 mapping")
            raise Exception(f"Text '{_text}' not found in the Mapping")

    return ' '.join(_mapped_texts)


if __name__ == "__main__":
    # load L1 sentences
    _l1_sentences = file_utility.load_first_column_from_csv(_L1_SENTENCE_CSV_FILE)
    _l1_l2_mapping = get_l1_l2_mapping()
    _l2_sentences = [get_mapped_sentence(sentence, _l1_l2_mapping) for sentence in _l1_sentences]

    # Prepare data for writing to CSV
    data = list(zip(_l1_sentences, _l2_sentences))
    column_names = ['L1-sentence', 'L2-sentence']

    # Write the data to a CSV file
    file_utility.write_rows_to_csv(_L1_L2_SENTENCE_CSV_FILE, data, column_names)

    print(f"L1 and L2 sentences have been written to {_L1_L2_SENTENCE_CSV_FILE}")
