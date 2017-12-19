#!/usr/bin/env python3
# Adapted from https://github.com/deraffe/calendar_facts
import random

rnd = random.SystemRandom()

CALENDAR_FACTS = (
        'Did you know that',
        [
            (
                'the',
                ['fall', 'spring'],
                'equinox'
            ),
            (
                'the',
                ['winter', 'summer'],
                ['solstice', 'olympics'],
            ),
            (
                'the',
                ['earliest', 'latest'],
                ['sunrise', 'sunset']
            ),
            (
                'daylight',
                ['saving', 'savings'],
                'time'
            ),
            (
                'leap',
                ['day', 'year']
            ),
            'easter',
            (
                'the',
                ['harvest', 'super', 'blood'],
                'moon'
            ),
            'Toyota Truck month',
            'shark week'
        ],
        [
            (
                'happens',
                ['earlier', 'later', 'at the wrong time'],
                'every year'
            ),
            (
                'drifts out of sync with the',
                [
                    'sun',
                    'moon',
                    'zodiac',
                    (
                        ['gregorian', 'mayan', 'lunar', 'iPhone'],
                        'calendar'
                    ),
                    'atomic clock in colorado'
                ]
            ),
            (
                'might',
                ['not happen', 'happen twice'],
                'this year'
            )
        ],
        'because of',
        [
            (
                'time zone legislation in',
                ['Indiana?', 'Arizona?', 'Russia?']
            ),
            'a decree by the pope in the 1500s?',
            (
                [
                    'precession',
                    'libration',
                    'nutation',
                    'libation',
                    'eccentricity',
                    'obliquity'
                ],
                'of the',
                [
                    'moon?',
                    'sun?',
                    'earth\'s axis?',
                    'equator?',
                    'prime meridian?',
                    (
                        ['international date', 'mason-dixon'],
                        'line?'
                    )
                ]
            ),
            'magnetic field reversal?',
            (
                'an arbitrary decision by',
                [
                    'Benjamin Franklin?',
                    'Isaac Newton?',
                    'FDR?'
                ]
            )
        ],
        'Apparently',
        [
            'it causes a predictable increase in car accidents.',
            'that\'s why we have leap seconds.',
            'scientists are really worried.',
            (
                'it was even more extreme during the',
                [
                    'bronze age.',
                    'ice age.',
                    'cretaceous.',
                    '1990s.'
                ]
            ),
            (
                'There\'s a proposal to fix it, but it',
                [
                    'will never happen.',
                    'actually makes things worse.',
                    'is stalled in congress.',
                    'might be unconstitutional.'
                ]
            ),
            'it\'s getting worse and no one knows why.'
        ],
        'While it may seem like trivia, it',
        [
            'causes huge headaches for software developers.',
            'is taken advantage of by high-speed traders.',
            'triggered the 2003 Northeast Blackout.',
            'has to be corrected for by GPS satellites.',
            'is now recognized as a major cause of World War I.'
        ]
)


def generate(tree):
    for part in tree:
        if isinstance(part, tuple):
            for resp in generate(part):
                yield resp
        elif isinstance(part, list):
            c = choice(part)
            if isinstance(c, str):
                yield c
            else:
                for resp in generate(c):
                    yield resp
        elif isinstance(part, str):
            yield part


def choice(options):
    return rnd.choice(options)

def fact():
    fact = list(generate(CALENDAR_FACTS))
    fact.append('#XKCD1930')
    return ' '.join(fact)


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    args = parser.parse_args()
    print fact()
    return


if __name__ == '__main__':
    main()
