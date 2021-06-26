from math import ceil, log2

import numpy as np


class BinaryDecoder(object):
    def __init__(self, arg_min: float, arg_max: float, precision: int) -> None:
        self._arg_min = arg_min
        self._arg_max = arg_max
        self._precision = precision
        self._argument_bit_length = self._compute_argument_bit_length()

    @property
    def argument_bit_length(self) -> int:
        return self._argument_bit_length

    def decode_individual(self, individual: np.ndarray, n: int = 2) -> float:
        reshaped_individual = individual.reshape((n, self._argument_bit_length))
        decoded = np.apply_along_axis(self._to_float, 1, reshaped_individual)
        return decoded

    # region Privates

    def _compute_argument_bit_length(self) -> int:
        intervals_number = abs(self._arg_max - self._arg_min) * (10.0 ** self._precision)
        x = log2(intervals_number) + log2(1)
        m = ceil(x)
        return m

    def _to_float(self, binary: np.ndarray) -> float:
        # [1:-1] below removes '[' and ']' bracets from np.array2string() binary representation: "[101010]"
        decimal_from_binary = int(np.array2string(binary, separator="")[1:-1], base=2)
        function_interval = abs(self._arg_max - self._arg_min)
        x = self._arg_min + (decimal_from_binary * function_interval) / (2.0 ** self._argument_bit_length - 1.0)
        return x

    # endregion
