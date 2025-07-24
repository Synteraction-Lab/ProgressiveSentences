_L1_WORD_CSV_FILE = 'text/L1-words.csv'
'''
L1
this
sample
'''

_L1_L2_WORD_CSV_FILE = 'output/L1-L2-words.csv'

from fractions import Fraction
from wuggy import WuggyGenerator
from utilities import file_utility


# Generate the candidates, see https://wuggycode.github.io/wuggy/ for details
def get_candidates(generator, word, candidate_count):
    print(f"Generating L2 words for '{word}'")
    generator.set_reference_sequence(generator.lookup_reference_segments(word))
    # generator.set_attribute_filter('sequence_length')
    # generator.set_attribute_filter('segment_length')
    generator.set_statistic('overlap_ratio')
    generator.set_statistic('plain_length')
    generator.set_statistic('transition_frequencies')
    generator.set_statistic('lexicality')
    generator.set_statistic('ned1')
    generator.set_output_mode('plain')
    j = 0
    generated = []

    for i in range(1, candidate_count + 1, 1):
        generator.set_frequency_filter(2 ** i, 2 ** i)
        for sequence in generator.generate_advanced(clear_cache=False):
            match = False
            if (generator.statistics['overlap_ratio'] < Fraction(2, 3) and
                    generator.statistics['lexicality'] == "N"):
                match = True
            if match:
                generated.append(sequence)
                j = j + 1
                if j > candidate_count:
                    break

    print(f"Word: {word} - Generated: {j} candidates: {generated}")

    return generated[0:candidate_count]


if __name__ == "__main__":

    # Load the words from the csv file
    _l1_words = file_utility.load_first_column_from_csv(_L1_WORD_CSV_FILE)

    L1_LANGUAGE = "orthographic_english"
    CANDIDATE_COUNT = 10

    generator = WuggyGenerator()
    generator.load(L1_LANGUAGE)

    # Generate the L2 words for each L1 word
    _l1_l2_pairs = []
    for word in _l1_words:
        candidates = get_candidates(generator, word, CANDIDATE_COUNT)
        _l1_l2_pairs.append([word] + candidates)

    column_names = ['L1'] + [f'L2-{i}' for i in range(1, CANDIDATE_COUNT + 1)]
    file_utility.write_rows_to_csv(_L1_L2_WORD_CSV_FILE, _l1_l2_pairs, column_names)

    print(f"Generated L2 words saved to {_L1_L2_WORD_CSV_FILE}")
