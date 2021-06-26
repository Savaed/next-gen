from typing import Any

import numpy as np

from nextgen.genetic import models


def random_unique_int(start: int = 0, stop: int = 1, size: int = 1, n: int = 1000) -> np.ndarray:
    """Generate random, unique integers from start (inclusive) to stop (inclusive).

    Args:
        start (int, optional): The start of interval. This is inclusive. Defaults to 0.
        stop (int, optional): The stop of interval. This is inclusive. Defaults to 1.
        size (int, optional): The number of generated integers. Defaults to 1.
        n (int, optional): Max number of generating repeats when not all random values are unique. Defaults to 1000.

    Returns:
        np.ndarray: Random integers.
    """

    rng = np.random.default_rng()
    unique = False
    random = np.empty((size))
    i = 0

    while not unique:
        random = rng.integers(start, stop, size=size, endpoint=True).astype(np.int8)
        i += 1
        unique = len(set(random)) == size or i == n

    return random


def get_evo_options(representation: models.ChromosomeRepresentation) -> dict[str, Any]:
    """Get available evolution algorithm options based on chromosome representation.

    Parameters
    ----------
    representation : models.ChromosomeRepresentation
        The chromosome representation.

    Returns
    -------
    dict[str, Any]
        Dictionary of all available options.

    Raises
    ------
    TypeError
        Parameter 'representation' must be of type ChromosomeRepresentation.
    """

    if not isinstance(representation, models.ChromosomeRepresentation):
        raise TypeError(
            f"Parameter 'representation' must be of type ChromosomeRepresentation but it's {type(representation)}"
        )

    options = {
        "available_functions": [e for e in models.SupportedFunctionName],
        "selection_types": [e for e in models.SelectionType],
        "mutation_types": [e for e in models.BinaryMutationType]
        if representation == models.ChromosomeRepresentation.BINARY
        else [e for e in models.RealMutationType],
        "crossover_types": [e for e in models.BinaryCrossoverType]
        if representation == models.ChromosomeRepresentation.BINARY
        else [e for e in models.RealCrossoverType],
    }
    return options


def get_random_at_interval(min: float, max: float, size: int) -> np.ndarray:
    return np.random.default_rng().random(size=size) * (max - min) + min
