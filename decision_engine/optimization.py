"""
Optimization module for the freight intelligence system.

Ranks multiple booking options based on their decision scores.
"""


def rank_options(options):
    """
    Rank booking options from best to worst.

    Each option must contain:
        - option_id
        - decision_score

    Parameters
    ----------
    options : list of dict
        List of possible booking options.

    Returns
    -------
    list of dict
        Options sorted from highest to lowest score.
    """

    ranked_options = sorted(
        options,
        key=lambda option: option["decision_score"],
        reverse=True
    )

    # Add ranking position
    for rank, option in enumerate(ranked_options, start=1):
        option["rank"] = rank

    return ranked_options


def get_best_option(options):
    """
    Return the highest-scoring booking option.

    Returns None if no options are available.
    """

    if not options:
        return None

    ranked_options = rank_options(options)

    return ranked_options[0]