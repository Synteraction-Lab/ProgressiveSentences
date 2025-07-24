import pandas as pd
import numpy as np

from analyze_ratings import analyze_data, plot_grouped_boxplots_subplots, setup_logger

_PARTICIPANTS_MARKS_FILE = 'output/participants_marks_summary.csv'
'''
Participant,S1-Words,S1-Seen-Sentences,S1-Unseen-Sentences,...
p101,4,5,3,
'''

# List of sessions and measures
_sessions = ['S1', 'S2', 'W1', 'W2']
_measures_day = [
    'Word-Recall',
    'Seen-Sentence-Recall',
    'Unseen-Sentence-Recall',
]

DAY = 'Day8'

# Combine all measures into a dictionary for easy looping
_measure_groups = {
    f'{DAY} Cued Recall': (_measures_day, (0, 9.5), np.arange(0, 9, 1)),
}

# Load the data from CSV
_data = pd.read_csv(_PARTICIPANTS_MARKS_FILE)

setup_logger(f'log_analysis_marks_{DAY}.log')
analyze_data(_data, _sessions, _measures_day, False)

# Create and save plots
for _title, _measure_group in _measure_groups.items():
    plot_grouped_boxplots_subplots(_data, _measure_group, _title, True, 3)
