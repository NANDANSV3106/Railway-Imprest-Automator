"""Convert integers to Indian-English words (LAKH/THOUSAND grouping)."""

_ONES = [
    '', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE',
    'TEN', 'ELEVEN', 'TWELVE', 'THIRTEEN', 'FOURTEEN', 'FIFTEEN', 'SIXTEEN',
    'SEVENTEEN', 'EIGHTEEN', 'NINETEEN',
]
_TENS = ['', '', 'TWENTY', 'THIRTY', 'FORTY', 'FIFTY',
         'SIXTY', 'SEVENTY', 'EIGHTY', 'NINETY']


def _below_hundred(x):
    if x < 20:
        return _ONES[x]
    return _TENS[x // 10] + (' ' + _ONES[x % 10] if x % 10 else '')


def _below_thousand(x):
    if x < 100:
        return _below_hundred(x)
    return _ONES[x // 100] + ' HUNDRED' + (' ' + _below_hundred(x % 100) if x % 100 else '')


def num_to_words(n):
    """Convert integer to Indian English words (UPPERCASE)."""
    if n == 0:
        return "ZERO"
    parts = []
    if n >= 100000:
        parts.append(_below_thousand(n // 100000) + ' LAKH')
        n %= 100000
    if n >= 1000:
        parts.append(_below_thousand(n // 1000) + ' THOUSAND')
        n %= 1000
    if n >= 100:
        parts.append(_ONES[n // 100] + ' HUNDRED')
        n %= 100
    if n:
        parts.append(_below_hundred(n))
    return ' '.join(parts)


def amount_in_words(n):
    return f"({num_to_words(n)} ONLY)"


def amount_in_words_title(n):
    """Title-case version for labour annexure."""
    return f"({num_to_words(n).title()} only)"
