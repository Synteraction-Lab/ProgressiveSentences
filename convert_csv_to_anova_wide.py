import sys
import optparse
import os
from utilities import file_utility

_RESULTS_DIR = "output"

_PARTICIPANT_ID_COLUMN = 'Participant'
_SESSION_ID_COLUMN = 'Style'

_PARTICIPANTS_RATINGS_FILE = 'user_data/participants_ratings.csv'
_RATINGS_MEASURES = [
    'DifficultToUnderstand',
    'Confusing',
    'EasyToRemember',
    'AbsorbedInLearning',
    'Enjoyable',
    'FreeRecall-Immediate',
    'FreeRecall-Delayed'
]

_PARTICIPANTS_RESULT_SUMMARY_FILE = 'output/participants_marks_summary.csv'
_RESULT_MEASURES = [
    'Word-Recall',
    'Seen-Sentence-Recall',
    'Unseen-Sentence-Recall',
]

_FILE_MEASURES = {
    _PARTICIPANTS_RATINGS_FILE: _RATINGS_MEASURES,
    _PARTICIPANTS_RESULT_SUMMARY_FILE: _RESULT_MEASURES
}


def csv_to_anova(file_name, index_column, group_by_column, interested_data_column):
    df = file_utility.read_csv(file_name)
    df_wide = df.pivot(index=index_column, columns=group_by_column, values=interested_data_column)

    file_path = os.path.splitext(file_name)
    file_name_wide_format = f'{_RESULTS_DIR}/{interested_data_column}{file_path[1]}'

    df_wide.to_csv(file_name_wide_format)
    print(f'New file: [{file_name_wide_format}]')


if __name__ == "__main__":
    for file, measures in _FILE_MEASURES.items():
        for measure in measures:
            csv_to_anova(file, _PARTICIPANT_ID_COLUMN, _SESSION_ID_COLUMN, measure)
