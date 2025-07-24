# encoding: utf-8
import logging
import pprint
from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg
import scipy.stats as stats
import seaborn as sns
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.multitest import multipletests

_PARTICIPANTS_RATINGS_FILE = 'user_data/participants_ratings.csv'
'''
Participant,Session,MEASURE_NAME1,MEASURE_NAME2,...
p101,SESSION_NAME1,value1,value2,...
'''

_PARTICIPANT_ID_COLUMN = 'Participant'
_SESSION_ID_COLUMN = 'Style'

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_EFF_SIZE = 'np2'  # ‘np2’ (partial eta-squared), ‘n2’ (eta-squared) or ‘ng2’(generalized eta-squared, default)


def setup_logger(log_file_name='log_analysis.log', mode='w'):
    global logger

    # Remove any existing handlers (important for rerunning in a notebook or script)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a file handler that logs to a file
    file_handler = logging.FileHandler(log_file_name, mode=mode)
    file_handler.setLevel(logging.INFO)

    # Create a console handler that logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_statistics(measure, data):
    mean_val = data.mean()
    std_val = data.std()
    min_val = data.min()
    max_val = data.max()
    logger.info(f"  {measure} - Mean: {mean_val:.2f}, SD: {std_val:.2f}, Min: {min_val}, Max: {max_val}")


def calculate_basic_statistics(data, session_names, measures_names):
    # Calculate and log overall and session-specific statistics
    total_participants = data[_PARTICIPANT_ID_COLUMN].nunique()
    logger.info(f"Total number of participants: {total_participants}")

    total_sessions = len(session_names)
    logger.info(f"Total number of sessions: {total_sessions}, calculated: {data[_SESSION_ID_COLUMN].nunique()}")

    logger.info("\nOverall Statistics for All Data:")
    for measure in measures_names:
        overall_data = data[measure].dropna()
        if len(overall_data) > 0:
            log_statistics(measure, overall_data)
        else:
            logger.info(f"  {measure} - No data available")

    logger.info("\nSession Statistics:")
    for session in session_names:
        session_data = data[data[_SESSION_ID_COLUMN] == session]
        session_participants = session_data[_PARTICIPANT_ID_COLUMN].nunique()
        logger.info(f"Session: {session}, N = {session_participants}")
        for measure in measures_names:
            measure_data = session_data[measure].dropna()
            if len(measure_data) > 0:
                log_statistics(measure, measure_data)
            else:
                logger.info(f"  {measure} - No data available")
        logger.info("\n")


def reshape_data_for_analysis(data, measures_names):
    data_long = pd.melt(data, id_vars=[_PARTICIPANT_ID_COLUMN, _SESSION_ID_COLUMN], value_vars=measures_names,
                        var_name='Measure', value_name='Score')
    data_long['Score'] = pd.to_numeric(data_long['Score'], errors='coerce')
    return data_long


def check_for_duplicates(data_long):
    duplicates = data_long[
        data_long.duplicated(subset=[_PARTICIPANT_ID_COLUMN, 'Measure', _SESSION_ID_COLUMN], keep=False)]
    if not duplicates.empty:
        logger.error("Duplicate rows found:")
        logger.warning(duplicates)
        return True
    else:
        logger.info("No duplicates found for participant, measure, and session combinations.")
        return False


def perform_normality_tests(data, session_names, measures_names):
    shapiro_results = {}
    for measure in measures_names:
        shapiro_results[measure] = {}
        for session in session_names:
            session_data = data[data[_SESSION_ID_COLUMN] == session][measure]
            if len(session_data) >= 3:
                if np.ptp(session_data) == 0:
                    shapiro_results[measure][session] = None
                    logger.info(f"Skipped Shapiro-Wilk test for {measure} in {session}: data has range zero.")
                else:
                    stat, p_value = stats.shapiro(session_data)
                    shapiro_results[measure][session] = p_value
            else:
                shapiro_results[measure][session] = None
    logger.info("Shapiro-Wilk Test Results (Normality):")
    logger.info(pprint.pformat(shapiro_results))
    return shapiro_results


def perform_sphericity_tests(data_long, session_names, measures_names):
    sphericity_results = {}
    for measure in measures_names:
        rm_anova_data = data_long[data_long['Measure'] == measure].pivot(index=_PARTICIPANT_ID_COLUMN,
                                                                         columns=_SESSION_ID_COLUMN,
                                                                         values='Score').dropna()
        try:
            sphericity_test = pg.sphericity(rm_anova_data)
            if isinstance(sphericity_test, pd.DataFrame):
                W = sphericity_test['W'].values[0]
                pval = sphericity_test['pval'].values[0]
            else:
                W, pval = None, None
        except Exception as e:
            W, pval = None, None
            logger.error(f"Sphericity test failed for {measure}: {e}")

        sphericity_results[measure] = W, pval
    logger.info("\nMauchly's Test Results (Sphericity):")
    logger.info(pprint.pformat(sphericity_results))
    return sphericity_results


def inspect_anova(anova):
    # Log the full summary to understand its structure
    logger.info("ANOVA Summary:")
    logger.info(anova.summary())

    # Log details about the structure and attributes of the anova object
    logger.info("Attributes of the ANOVA object:")
    for attr in dir(anova):
        logger.info(f"{attr}: {getattr(anova, attr)}")

    # Check if anova has an anova_table or equivalent attribute directly
    if hasattr(anova, 'anova_table'):
        logger.info("ANOVA Table found:")
        logger.info(anova.anova_table)
    else:
        logger.info("No direct ANOVA table found in the object.")


def calculate_cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    s1, s2 = group1.std(ddof=1), group2.std(ddof=1)
    pooled_std = sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
    return (group1.mean() - group2.mean()) / pooled_std


def perform_anova_and_effect_size(data_long, session_names, measures_names, shapiro_results, sphericity_results):
    anova_results = {}
    for measure in measures_names:
        measure_data = data_long[data_long['Measure'] == measure].copy()
        logger.info(f"\nStructure of measure_data for measure: {measure}")
        logger.info(measure_data.head())

        # Check normality and sphericity assumptions
        if all(p is None or p > 0.05 for p in shapiro_results[measure].values()) and (
                sphericity_results[measure][1] is None or sphericity_results[measure][1] > 0.05):

            # Perform Repeated Measures ANOVA using Pingouin
            aov = pg.rm_anova(data=measure_data, dv='Score', within=_SESSION_ID_COLUMN, subject=_PARTICIPANT_ID_COLUMN,
                              detailed=True, effsize=_EFF_SIZE)
            logger.info("Repeated Measures ANOVA Results:")
            logger.info(aov)

            eta_sq = aov[_EFF_SIZE].iloc[0]  # Eta Squared
            logger.info(f"Effect Size ({_EFF_SIZE}) for {measure}: {eta_sq:.3f}")

            anova_results[measure] = ("Repeated Measures ANOVA", aov)

        elif all(p is None or p > 0.05 for p in shapiro_results[measure].values()):
            # If normality is met but sphericity is violated, perform ART-ANOVA
            measure_data['Score'] = measure_data.groupby(_PARTICIPANT_ID_COLUMN)['Score'].rank()
            aov = pg.rm_anova(data=measure_data, dv='Score', within=_SESSION_ID_COLUMN, subject=_PARTICIPANT_ID_COLUMN,
                              detailed=True, effsize=_EFF_SIZE)
            logger.info("ART-ANOVA Results:")
            logger.info(aov)

            eta_sq = aov[_EFF_SIZE].iloc[0]  # Eta Squared
            logger.info(f"Effect Size ({_EFF_SIZE}) for {measure}: {eta_sq:.3f}")

            anova_results[measure] = ("ART-ANOVA", aov)

        else:
            # If normality is violated, perform Friedman Test
            friedman_result = pg.friedman(data=measure_data, dv='Score', within=_SESSION_ID_COLUMN,
                                          subject=_PARTICIPANT_ID_COLUMN)
            stat = friedman_result['Q'].iloc[0]
            p_value = friedman_result['p-unc'].iloc[0]
            kendall_w = friedman_result['W'].iloc[0]  # Kendall's W (effect size)

            anova_results[measure] = ("Friedman Test", stat, p_value, kendall_w)
            logger.info(
                f"Friedman Test Statistic for {measure}: {stat:.3f}, p-value: {p_value:.3f}, Kendall's W: {kendall_w:.3f}")

    return anova_results


def perform_posthoc_tests(data_long, session_names, measures_names, anova_results, display_plot):
    posthoc_results = {}
    for measure in measures_names:
        rm_anova_data = data_long[data_long['Measure'] == measure].pivot(index=_PARTICIPANT_ID_COLUMN,
                                                                         columns=_SESSION_ID_COLUMN,
                                                                         values='Score').dropna()
        pairwise_comparisons = []
        tukey_hsd_results = None
        if anova_results[measure][0] in ["Repeated Measures ANOVA", "ART-ANOVA"]:
            all_scores = rm_anova_data.reset_index().melt(id_vars=[_PARTICIPANT_ID_COLUMN],
                                                          value_name='Score',
                                                          var_name=_SESSION_ID_COLUMN)
            tukey_hsd_results = pairwise_tukeyhsd(endog=all_scores['Score'],
                                                  groups=all_scores[_SESSION_ID_COLUMN],
                                                  alpha=0.05)
            logger.info(f"\n{measure} - Tukey HSD Post-hoc Test:")
            logger.info(tukey_hsd_results.summary())

            if display_plot:
                plot_posthoc_results(tukey_hsd_results, measure)

        elif anova_results[measure][0] == "Friedman Test":
            for i, session1 in enumerate(session_names):
                for session2 in session_names[i + 1:]:
                    scores1 = rm_anova_data[session1]
                    scores2 = rm_anova_data[session2]
                    differences = scores1 - scores2
                    if np.all(differences == 0):
                        p_value = np.nan
                    else:
                        _, p_value = stats.wilcoxon(scores1, scores2)
                    pairwise_comparisons.append(p_value)

                    cohen_d = calculate_cohens_d(scores1, scores2)
                    logger.info(f"Cohen's d for {session1} vs {session2} in {measure}: {cohen_d:.3f}")

            _, corrected_pvalues, _, _ = multipletests(pairwise_comparisons, method='bonferroni')
            posthoc_results[measure] = corrected_pvalues

    logger.info("\nPost-hoc Test Results with Bonferroni Correction:")
    for measure, pvalues in posthoc_results.items():
        logger.info(f"\n{measure}:")
        for comparison, pval in zip(
                [(f'{s1} vs {s2}') for i, s1 in enumerate(session_names) for s2 in session_names[i + 1:]],
                pvalues):
            logger.info(f"{comparison}: p-value = {pval}")


def analyze_data(data: pd.DataFrame, session_names: list[str], measures_names: list[str], display_plot: bool = True):
    calculate_basic_statistics(data, session_names, measures_names)

    data_long = reshape_data_for_analysis(data, measures_names)

    if display_plot:
        plot_distributions(data_long, measures_names, session_names)

    if check_for_duplicates(data_long):
        return

    shapiro_results = perform_normality_tests(data, session_names, measures_names)

    sphericity_results = perform_sphericity_tests(data_long, session_names, measures_names)

    anova_results = perform_anova_and_effect_size(data_long, session_names, measures_names,
                                                  shapiro_results, sphericity_results)

    perform_posthoc_tests(data_long, session_names, measures_names, anova_results, display_plot)


def plot_distributions(data_long, measures_names, session_names):
    for measure in measures_names:
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=_SESSION_ID_COLUMN, y='Score', data=data_long[data_long['Measure'] == measure])
        plt.title(f'Distribution of {measure}')
        plt.xlabel('Session')
        plt.ylabel('Score')
        plt.show()


def plot_posthoc_results(tukey_hsd_results, measure):
    # plt.figure(figsize=(12, 8))
    tukey_hsd_results.plot_simultaneous()
    plt.title(f'Tukey HSD Results for {measure}')
    plt.show()


# Plot grouped boxplots with subplots for each measure set without category distinction
def plot_grouped_boxplots_subplots(all_data, all_measures_group, title, show_p_values=True, number_of_columns=6):
    all_measures, y_lim, y_stick = all_measures_group
    n_cols = number_of_columns  # Number of columns in the subplot grid
    n_rows = (len(all_measures) + n_cols - 1) // n_cols  # Calculate the number of rows needed
    plt.figure(figsize=(5 * n_cols, 5 * n_rows))

    for i, measure in enumerate(all_measures, 1):
        plt.subplot(n_rows, n_cols, i)
        melted_subset = all_data.melt(id_vars=[_SESSION_ID_COLUMN], value_vars=[measure], var_name='Measure',
                                      value_name='Score')

        # Create the boxplot
        ax = sns.boxplot(x=_SESSION_ID_COLUMN, y='Score', data=melted_subset, palette="Set3", width=0.4, legend=False,
                         hue=_SESSION_ID_COLUMN)

        # Add mean value line
        for j, session_i in enumerate(all_data[_SESSION_ID_COLUMN].unique()):
            mean_value = all_data[all_data[_SESSION_ID_COLUMN] == session_i][measure].mean()
            ax.hlines(mean_value, j - 0.2, j + 0.2, colors='black', linestyles='dashed', linewidth=2)
            if i == 1 and j == 0:
                ax.hlines(mean_value, j - 0.2, j + 0.2, colors='black', linestyles='dashed', linewidth=2)

        # Customize the plot
        plt.title(measure, fontsize=14)
        plt.xlabel('')
        plt.ylabel('', fontsize=12)
        plt.xticks(rotation=45, fontsize=12)

        # Set y-axis limit and customize y-axis ticks
        if y_lim:
            ax.set_ylim(y_lim)
        if y_stick is not None:
            ax.set_yticks(y_stick)

        if show_p_values:
            # Perform pairwise comparisons and annotate p-values
            unique_sessions = melted_subset[_SESSION_ID_COLUMN].unique()
            pairs = [(unique_sessions[j], unique_sessions[k]) for j in range(len(unique_sessions)) for k in
                     range(j + 1, len(unique_sessions))]
            line_styles = ['-', '--', ':']
            _index = 0
            for idx, (session1, session2) in enumerate(pairs):
                data1 = melted_subset[melted_subset[_SESSION_ID_COLUMN] == session1]['Score']
                data2 = melted_subset[melted_subset[_SESSION_ID_COLUMN] == session2]['Score']

                # Perform t-test or Wilcoxon test depending on normality assumptions
                if len(data1) >= 3 and len(data2) >= 3:
                    _, p = stats.ttest_ind(data1, data2)
                else:
                    _, p = stats.wilcoxon(data1, data2)


                if p < 0.1:
                    # Annotate the p-value on the plot
                    y, h, col = melted_subset['Score'].max() + (_index + 1) * 0.75, 0.2, 'k'
                    x1, x2 = unique_sessions.tolist().index(session1), unique_sessions.tolist().index(session2)
                    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.5, c=col,
                            linestyle=line_styles[idx % len(line_styles)])
                    ax.text((x1 + x2) * .5, y + h, f"{'**' if p < 0.001 else '*' if p < 0.05 else ''} p = {p:.3f}",
                            ha='center',
                            va='bottom', color=col, fontsize=10)
                    _index += 1

        # Add legend for mean value line (only for the first subplot)
        if i == 1:
            ax.legend(loc='upper right', fontsize=12)

    plt.suptitle(title, fontsize=18)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    _file_name = f'output/{title}.png'
    plt.savefig(_file_name)
    logger.info(f'\nSaved {_file_name}')


if __name__ == '__main__':
    # Load the data from CSV
    _data = pd.read_csv(_PARTICIPANTS_RATINGS_FILE)

    # List of sessions and measures
    _sessions = ['S1', 'S2', 'W1', 'W2']
    _measures = [
        'DifficultToUnderstand',
        'Confusing',
        'EasyToRemember',
        'AbsorbedInLearning',
        'Enjoyable',
        'FreeRecall-Immediate',
        'FreeRecall-Delayed'
    ]

    _measures_0_7 = _measures

    # Combine all measures into a dictionary for easy looping
    _measure_groups = {
        'User Ratings (1-7 Likert)': (_measures_0_7, (0, 11), np.arange(0, 8, 1)),
    }

    setup_logger('log_analysis_ratings.log')

    analyze_data(_data, _sessions, _measures, False)

    # Create and save plots
    for _title, _measure_group in _measure_groups.items():
        plot_grouped_boxplots_subplots(_data, _measure_group, _title, True, 5)
