"""Greedy and prefix beam decoding."""
from scripts.ctc_core import BLANK, collapse_path, validate


def greedy_path(emissions, alphabet):
    # напишите ваш код здесь
    path = []
    for row in emissions:
        best = alphabet[0]
        for symbol in alphabet[1:]:
            if row[symbol] > row[best]:
                best = symbol
        path.append(best)
    return path


def greedy_decode(emissions, alphabet, blank=BLANK):
    validate(emissions, alphabet, blank)
    path = greedy_path(emissions, alphabet)
    return path, collapse_path(path, blank)


def prefix_transitions(prefix, p_blank, p_nonblank, symbol, probability):
    # напишите ваш код здесь
    extended = prefix + symbol
    if prefix and prefix[-1] == symbol:
        # повтор: без blank остаёмся в том же префиксе, через blank расширяем
        return [
            (prefix, p_nonblank * probability),
            (extended, p_blank * probability),
        ]
    return [(extended, (p_blank + p_nonblank) * probability)]


def prefix_beam_decode(emissions, alphabet, beam_width, blank=BLANK):
    validate(emissions, alphabet, blank)
    if isinstance(beam_width, bool) or not isinstance(beam_width, int) or beam_width <= 0:
        raise ValueError('beam width must be a positive integer')
    beam = {'': (1.0, 0.0)}
    for row in emissions:
        arrivals = {}
        def add(prefix, blank_mass=0.0, nonblank_mass=0.0):
            old_blank, old_nonblank = arrivals.get(prefix, (0.0, 0.0))
            arrivals[prefix] = old_blank + blank_mass, old_nonblank + nonblank_mass
        for prefix, (p_blank, p_nonblank) in beam.items():
            add(prefix, blank_mass=(p_blank + p_nonblank) * row[blank])
            for symbol in alphabet:
                if symbol != blank:
                    for destination, mass in prefix_transitions(prefix, p_blank, p_nonblank, symbol, row[symbol]):
                        add(destination, nonblank_mass=mass)
        ranked = sorted(arrivals.items(), key=lambda item: (-(item[1][0] + item[1][1]), item[0]))
        beam = dict(ranked[:beam_width])
    ledger = [(prefix, pb + pnb) for prefix, (pb, pnb) in sorted(beam.items(), key=lambda item: (-(item[1][0] + item[1][1]), item[0]))]
    return ledger[0][0], ledger
