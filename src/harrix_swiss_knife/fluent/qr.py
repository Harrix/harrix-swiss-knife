"""Minimal QR Code encoder (byte mode, versions 1-40, automatic mask).

Follows ISO/IEC 18004 the same way as the reference "QR Code generator"
algorithm by Project Nayuki: build data codewords, add Reed-Solomon error
correction, interleave blocks, place function patterns, and choose the mask
with the lowest penalty.

"""

from __future__ import annotations

from enum import Enum

_MIN_VERSION = 1
_MAX_VERSION = 40
_PENALTY_N1 = 3
_PENALTY_N2 = 3
_PENALTY_N3 = 40
_PENALTY_N4 = 10
_RUN_LIMIT = 5
_VERSION_INFO_MIN = 7
_FINDER_RUN_LENGTH = 7
_GF_POLY = 0x11D
_BCH_FORMAT = 0x537
_BCH_VERSION = 0x1F25
_FORMAT_MASK = 0x5412
_BYTE_MODE = 0x4
_SMALL_VERSION_MAX = 9
_PAD_BYTES = (0xEC, 0x11)


class Ecc(Enum):
    """Error correction level: (format bits, index into the tables)."""

    LOW = (1, 0)
    MEDIUM = (0, 1)
    QUARTILE = (3, 2)
    HIGH = (2, 3)


def encode_qr(text: str, ecc: Ecc = Ecc.MEDIUM) -> list[list[bool]]:
    """Encode `text` (UTF-8 bytes) and return the module matrix (`True` = dark).

    Raises:

    - `ValueError`: When the text does not fit in version 40.

    """
    data = text.encode("utf-8")
    version = _choose_version(len(data), ecc)
    bits: list[int] = []
    _append_bits(bits, _BYTE_MODE, 4)
    _append_bits(bits, len(data), 8 if version <= _SMALL_VERSION_MAX else 16)
    for byte in data:
        _append_bits(bits, byte, 8)
    capacity = _num_data_codewords(version, ecc) * 8
    _append_bits(bits, 0, min(4, capacity - len(bits)))
    _append_bits(bits, 0, (-len(bits)) % 8)
    pad_index = 0
    while len(bits) < capacity:
        _append_bits(bits, _PAD_BYTES[pad_index % 2], 8)
        pad_index += 1
    codewords = [int("".join(map(str, bits[i : i + 8])), 2) for i in range(0, len(bits), 8)]
    final = _add_ecc_and_interleave(codewords, version, ecc)
    return _build_matrix(final, version, ecc)


def _add_ecc_and_interleave(data: list[int], version: int, ecc: Ecc) -> list[int]:
    level = ecc.value[1]
    num_blocks = _NUM_ERROR_CORRECTION_BLOCKS[level][version]
    block_ecc_len = _ECC_CODEWORDS_PER_BLOCK[level][version]
    raw_codewords = _num_raw_data_modules(version) // 8
    num_short_blocks = num_blocks - raw_codewords % num_blocks
    short_block_len = raw_codewords // num_blocks
    divisor = _reed_solomon_divisor(block_ecc_len)
    blocks: list[list[int]] = []
    offset = 0
    for index in range(num_blocks):
        length = short_block_len - block_ecc_len + (0 if index < num_short_blocks else 1)
        chunk = data[offset : offset + length]
        offset += length
        remainder = _reed_solomon_remainder(chunk, divisor)
        if index < num_short_blocks:
            chunk = [*chunk, 0]
        blocks.append(chunk + remainder)
    result: list[int] = []
    for column in range(len(blocks[0])):
        for index, block in enumerate(blocks):
            if column != short_block_len - block_ecc_len or index >= num_short_blocks:
                result.append(block[column])
    return result


def _alignment_positions(version: int) -> list[int]:
    if version == 1:
        return []
    count = version // 7 + 2
    step = (version * 8 + count * 3 + 5) // (count * 4 - 4) * 2
    result = [version * 4 + 10 - index * step for index in range(count - 1)]
    return [6, *reversed(result)]


def _append_bits(bits: list[int], value: int, length: int) -> None:
    bits.extend((value >> shift) & 1 for shift in range(length - 1, -1, -1))


def _apply_mask(modules: list[list[bool]], function: list[list[bool]], mask: int, size: int) -> None:
    for y in range(size):
        for x in range(size):
            if function[y][x]:
                continue
            if mask == 0:
                invert = (x + y) % 2 == 0
            elif mask == 1:
                invert = y % 2 == 0
            elif mask == 2:  # noqa: PLR2004
                invert = x % 3 == 0
            elif mask == 3:  # noqa: PLR2004
                invert = (x + y) % 3 == 0
            elif mask == 4:  # noqa: PLR2004
                invert = (x // 3 + y // 2) % 2 == 0
            elif mask == 5:  # noqa: PLR2004
                invert = x * y % 2 + x * y % 3 == 0
            elif mask == 6:  # noqa: PLR2004
                invert = (x * y % 2 + x * y % 3) % 2 == 0
            else:
                invert = ((x + y) % 2 + x * y % 3) % 2 == 0
            if invert:
                modules[y][x] = not modules[y][x]


def _bit(value: int, index: int) -> bool:
    return (value >> index) & 1 != 0


def _build_matrix(codewords: list[int], version: int, ecc: Ecc) -> list[list[bool]]:
    size = version * 4 + 17
    modules = [[False] * size for _ in range(size)]
    function = [[False] * size for _ in range(size)]

    def set_function(x: int, y: int, *, dark: bool) -> None:
        modules[y][x] = dark
        function[y][x] = True

    for index in range(size):
        set_function(6, index, dark=index % 2 == 0)
        set_function(index, 6, dark=index % 2 == 0)
    for cx, cy in ((3, 3), (size - 4, 3), (3, size - 4)):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                x, y = cx + dx, cy + dy
                if 0 <= x < size and 0 <= y < size:
                    distance = max(abs(dx), abs(dy))
                    set_function(x, y, dark=distance not in {2, 4})
    positions = _alignment_positions(version)
    last = len(positions) - 1
    for i, ax in enumerate(positions):
        for j, ay in enumerate(positions):
            if (i == 0 and j == 0) or (i == 0 and j == last) or (i == last and j == 0):
                continue
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    set_function(ax + dx, ay + dy, dark=max(abs(dx), abs(dy)) != 1)
    _draw_format_bits(set_function, size, ecc, 0)
    _draw_version(set_function, size, version)

    _place_codewords(modules, function, codewords, size)
    best_mask = 0
    best_penalty = -1
    for mask in range(8):
        _apply_mask(modules, function, mask, size)
        _draw_format_bits(set_function, size, ecc, mask)
        penalty = _penalty(modules, size)
        if best_penalty < 0 or penalty < best_penalty:
            best_mask, best_penalty = mask, penalty
        _apply_mask(modules, function, mask, size)
    _apply_mask(modules, function, best_mask, size)
    _draw_format_bits(set_function, size, ecc, best_mask)
    return modules


def _choose_version(data_len: int, ecc: Ecc) -> int:
    for version in range(_MIN_VERSION, _MAX_VERSION + 1):
        header = 4 + (8 if version <= _SMALL_VERSION_MAX else 16)
        if header + data_len * 8 <= _num_data_codewords(version, ecc) * 8:
            return version
    msg = "Text is too long for a QR code"
    raise ValueError(msg)


def _draw_format_bits(set_function, size: int, ecc: Ecc, mask: int) -> None:  # noqa: ANN001
    data = ecc.value[0] << 3 | mask
    remainder = data
    for _ in range(10):
        remainder = (remainder << 1) ^ ((remainder >> 9) * _BCH_FORMAT)
    bits = (data << 10 | remainder) ^ _FORMAT_MASK
    for index in range(6):
        set_function(8, index, dark=_bit(bits, index))
    set_function(8, 7, dark=_bit(bits, 6))
    set_function(8, 8, dark=_bit(bits, 7))
    set_function(7, 8, dark=_bit(bits, 8))
    for index in range(9, 15):
        set_function(14 - index, 8, dark=_bit(bits, index))
    for index in range(8):
        set_function(size - 1 - index, 8, dark=_bit(bits, index))
    for index in range(8, 15):
        set_function(8, size - 15 + index, dark=_bit(bits, index))
    set_function(8, size - 8, dark=True)


def _draw_version(set_function, size: int, version: int) -> None:  # noqa: ANN001
    if version < _VERSION_INFO_MIN:
        return
    remainder = version
    for _ in range(12):
        remainder = (remainder << 1) ^ ((remainder >> 11) * _BCH_VERSION)
    bits = version << 12 | remainder
    for index in range(18):
        dark = _bit(bits, index)
        a = size - 11 + index % 3
        b = index // 3
        set_function(a, b, dark=dark)
        set_function(b, a, dark=dark)


def _finder_like_runs(line: list[bool]) -> int:
    """Count `1:1:3:1:1` patterns with four light modules on either side."""
    padded = [False] * 4 + line + [False] * 4
    pattern_a = [True, False, True, True, True, False, True, False, False, False, False]
    pattern_b = list(reversed(pattern_a))
    count = 0
    for start in range(len(padded) - len(pattern_a) + 1):
        window = padded[start : start + len(pattern_a)]
        if window in (pattern_a, pattern_b):
            count += 1
    return count


def _num_data_codewords(version: int, ecc: Ecc) -> int:
    level = ecc.value[1]
    return (
        _num_raw_data_modules(version) // 8
        - _ECC_CODEWORDS_PER_BLOCK[level][version] * _NUM_ERROR_CORRECTION_BLOCKS[level][version]
    )


def _num_raw_data_modules(version: int) -> int:
    result = (16 * version + 128) * version + 64
    if version >= 2:  # noqa: PLR2004
        count = version // 7 + 2
        result -= (25 * count - 10) * count - 55
        if version >= _VERSION_INFO_MIN:
            result -= 36
    return result


def _penalty(modules: list[list[bool]], size: int) -> int:
    result = 0
    lines = [list(row) for row in modules] + [[modules[y][x] for y in range(size)] for x in range(size)]
    for line in lines:
        run_color = line[0]
        run_length = 1
        for value in line[1:]:
            if value == run_color:
                run_length += 1
                continue
            if run_length >= _RUN_LIMIT:
                result += _PENALTY_N1 + run_length - _RUN_LIMIT
            run_color, run_length = value, 1
        if run_length >= _RUN_LIMIT:
            result += _PENALTY_N1 + run_length - _RUN_LIMIT
        result += _finder_like_runs(line) * _PENALTY_N3
    for y in range(size - 1):
        for x in range(size - 1):
            color = modules[y][x]
            if color == modules[y][x + 1] == modules[y + 1][x] == modules[y + 1][x + 1]:
                result += _PENALTY_N2
    dark = sum(value for row in modules for value in row)
    total = size * size
    steps = (abs(dark * 20 - total * 10) + total - 1) // total - 1
    result += max(0, steps) * _PENALTY_N4
    return result


def _place_codewords(modules: list[list[bool]], function: list[list[bool]], codewords: list[int], size: int) -> None:
    bit_index = 0
    total_bits = len(codewords) * 8
    right = size - 1
    while right >= 1:
        if right == _FINDER_RUN_LENGTH - 1:
            right = _FINDER_RUN_LENGTH - 2
        for vertical in range(size):
            for offset in range(2):
                x = right - offset
                upward = ((right + 1) & 2) == 0
                y = size - 1 - vertical if upward else vertical
                if function[y][x] or bit_index >= total_bits:
                    continue
                modules[y][x] = _bit(codewords[bit_index >> 3], 7 - (bit_index & 7))
                bit_index += 1
        right -= 2


def _reed_solomon_divisor(degree: int) -> list[int]:
    result = [0] * (degree - 1) + [1]
    root = 1
    for _ in range(degree):
        for index in range(len(result)):
            result[index] = _reed_solomon_multiply(result[index], root)
            if index + 1 < len(result):
                result[index] ^= result[index + 1]
        root = _reed_solomon_multiply(root, 0x02)
    return result


def _reed_solomon_multiply(x: int, y: int) -> int:
    result = 0
    for index in range(7, -1, -1):
        result = (result << 1) ^ ((result >> 7) * _GF_POLY)
        result ^= ((y >> index) & 1) * x
    return result


def _reed_solomon_remainder(data: list[int], divisor: list[int]) -> list[int]:
    result = [0] * len(divisor)
    for byte in data:
        factor = byte ^ result.pop(0)
        result.append(0)
        for index, coefficient in enumerate(divisor):
            result[index] ^= _reed_solomon_multiply(coefficient, factor)
    return result


# Tables indexed [ecc index][version]; index 0 is unused padding.
_ECC_CODEWORDS_PER_BLOCK = (
    (
        -1,
        7,
        10,
        15,
        20,
        26,
        18,
        20,
        24,
        30,
        18,
        20,
        24,
        26,
        30,
        22,
        24,
        28,
        30,
        28,
        28,
        28,
        28,
        30,
        30,
        26,
        28,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
    ),
    (
        -1,
        10,
        16,
        26,
        18,
        24,
        16,
        18,
        22,
        22,
        26,
        30,
        22,
        22,
        24,
        24,
        28,
        28,
        26,
        26,
        26,
        26,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
        28,
    ),
    (
        -1,
        13,
        22,
        18,
        26,
        18,
        24,
        18,
        22,
        20,
        24,
        28,
        26,
        24,
        20,
        30,
        24,
        28,
        28,
        26,
        30,
        28,
        30,
        30,
        30,
        30,
        28,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
    ),
    (
        -1,
        17,
        28,
        22,
        16,
        22,
        28,
        26,
        26,
        24,
        28,
        24,
        28,
        22,
        24,
        24,
        30,
        28,
        28,
        26,
        28,
        30,
        24,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
        30,
    ),
)
_NUM_ERROR_CORRECTION_BLOCKS = (
    (
        -1,
        1,
        1,
        1,
        1,
        1,
        2,
        2,
        2,
        2,
        4,
        4,
        4,
        4,
        4,
        6,
        6,
        6,
        6,
        7,
        8,
        8,
        9,
        9,
        10,
        12,
        12,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        19,
        20,
        21,
        22,
        24,
        25,
    ),
    (
        -1,
        1,
        1,
        1,
        2,
        2,
        4,
        4,
        4,
        5,
        5,
        5,
        8,
        9,
        9,
        10,
        10,
        11,
        13,
        14,
        16,
        17,
        17,
        18,
        20,
        21,
        23,
        25,
        26,
        28,
        29,
        31,
        33,
        35,
        37,
        38,
        40,
        43,
        45,
        47,
        49,
    ),
    (
        -1,
        1,
        1,
        2,
        2,
        4,
        4,
        6,
        6,
        8,
        8,
        8,
        10,
        12,
        16,
        12,
        17,
        16,
        18,
        21,
        20,
        23,
        23,
        25,
        27,
        29,
        34,
        34,
        35,
        38,
        40,
        43,
        45,
        48,
        51,
        53,
        56,
        59,
        62,
        65,
        68,
    ),
    (
        -1,
        1,
        1,
        2,
        4,
        4,
        4,
        5,
        6,
        8,
        8,
        11,
        11,
        16,
        16,
        18,
        16,
        19,
        21,
        25,
        25,
        25,
        34,
        30,
        32,
        35,
        37,
        40,
        42,
        45,
        48,
        51,
        54,
        57,
        60,
        63,
        66,
        70,
        74,
        77,
        81,
    ),
)
