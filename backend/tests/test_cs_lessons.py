"""Computer Science Foundations, units 1 ("How data is stored") and 3 ("Searching").

The same lesson suite as the Python units. Most cases call the learner's functions (ENG-06). The
searches are told apart by behaviour, not construct: a binary search must return the same count of
looks as the lesson's (low + high) // 2 method, which a linear search cannot.
"""
from lesson_suite import Spec, make_tests, LESSONS
from test_unit2_lessons import client  # noqa: F401
from test_unit10_11_lessons import line_of

sim = lambda i: LESSONS[i].task('challenge').similar_example.code  # noqa: E731

B = 'def to_binary(n):\n    if n == 0:\n        return "0"\n    bits = ""\n    while n > 0:\n        bits = str(n % 2) + bits\n        n = n // 2\n    return bits\n\ndef from_binary(bits):\n    value = 0\n    for bit in bits:\n        value = value * 2 + int(bit)\n    return value\n'
BINARY = Spec(start='', reference=B,
    creative=['def to_binary(n):\n    out = []\n    while True:\n        out.insert(0, str(n % 2))\n        n //= 2\n        if n == 0:\n            return "".join(out)\n\ndef from_binary(bits):\n    return sum(int(b) << i for i, b in enumerate(reversed(bits)))'],
    wrong=[
        ('bits put the wrong way round', B.replace('bits = str(n % 2) + bits', 'bits = bits + str(n % 2)'), 'needs_work', 'cs.binary.case.thirteen'),
        ('no answer for 0', B.replace('    if n == 0:\n        return "0"\n', ''), 'needs_work', 'cs.binary.case.zero'),
        ('place values counted from the left', B.replace('    for bit in bits:\n        value = value * 2 + int(bit)\n', '    for i, bit in enumerate(bits):\n        value = value + int(bit) * 2 ** i\n'), 'needs_work', 'cs.binary.case.read'),
        ('contrived: never more than 7 bits', B.replace('    return bits\n\ndef from', '    return bits[-7:]\n\ndef from'), 'needs_work', 'cs.binary.case.big'),
        ('a leading 0 read as zero', B.replace('    value = 0\n', '    if bits[0] == "0":\n        return 0\n    value = 0\n'), 'needs_work', 'cs.binary.case.leading'),
        ('a number added to text', B.replace('bits = str(n % 2) + bits', 'bits = n % 2 + bits'), 'execution_error', ('error', 'TypeError', 6)),
        ('a misspelt name', B.replace('value = value * 2 + int(bit)', 'value = value * 2 + int(bits[9])'), 'execution_error', ('error', 'IndexError', 13)),
        ('a misspelt parameter', 'def to_binary(n):\n    return str(m)\n', 'execution_error', ('error', 'NameError', 2)),
        ('a module the browser does not have', 'import pygame\n' + B, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'to_base3': 'to_binary', 'k': 'n', 'digits': 'bits'},
    claims=[('predict: 10010', 'print(int("10010", 2))', [], '18'), ('guided: eight lamps', 'print(int("11111111", 2), bin(255))', [], '255 0b11111111'), ('similar example', sim('cs.binary'), [], '101')])

H = 'DIGITS = "0123456789abcdef"\n\ndef hex_to_rgb(colour):\n    text = colour.lstrip("#").lower()\n    parts = []\n    for i in range(0, 6, 2):\n        parts.append(DIGITS.index(text[i]) * 16 + DIGITS.index(text[i + 1]))\n    return parts\n\ndef rgb_to_hex(red, green, blue):\n    out = "#"\n    for value in (red, green, blue):\n        out = out + DIGITS[value // 16] + DIGITS[value % 16]\n    return out\n'
HEX = Spec(start='', reference=H,
    creative=['def hex_to_rgb(colour):\n    n = int(colour.strip("#"), 16)\n    return [(n >> 16) & 255, (n >> 8) & 255, n & 255]\n\ndef rgb_to_hex(red, green, blue):\n    return "#" + "".join(format(v, "02x") for v in (red, green, blue))'],
    wrong=[
        ('adds the two digits', H.replace('DIGITS.index(text[i]) * 16 + DIGITS.index(text[i + 1])', 'DIGITS.index(text[i]) + DIGITS.index(text[i + 1])'), 'needs_work', 'cs.hexadecimal.case.orange'),
        ('one digit for a small amount', H.replace('out = out + DIGITS[value // 16] + DIGITS[value % 16]', 'out = out + format(value, "x")'), 'needs_work', 'cs.hexadecimal.case.small'),
        ('capitals read as missing digits', H.replace('colour.lstrip("#").lower()', 'colour.lstrip("#")').replace('DIGITS.index', 'DIGITS.find'), 'needs_work', 'cs.hexadecimal.case.capitals'),
        ('contrived: amounts capped at 254', H.replace('    for value in (red, green, blue):\n', '    for value in (min(red, 254), min(green, 254), min(blue, 254)):\n'), 'needs_work', 'cs.hexadecimal.case.white'),
        ('contrived: black read as nothing', H.replace('    parts = []\n', '    if text == "000000":\n        return []\n    parts = []\n'), 'needs_work', 'cs.hexadecimal.case.black'),
        ('the # left in', H.replace('colour.lstrip("#").lower()', 'colour.lower()'), 'execution_error', ('error', 'ValueError', 7)),
        ('a number added to text', H.replace('out = out + DIGITS[value // 16] + DIGITS[value % 16]', 'out = out + value'), 'execution_error', ('error', 'TypeError', line_of(H, 'out = out + DIGITS'))),
        ('a misspelt name', H.replace('    return parts\n', '    return part\n'), 'execution_error', ('error', 'NameError', 8)),
        ('a module the browser does not have', 'import pygame\n' + H, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'split_byte': 'hex_to_rgb', 'n': 'value'},
    claims=[('predict: #00ff00', 'print(int("00", 16), int("ff", 16), int("00", 16))', [], '0 255 0'), ('discover: ff is 255', 'print(15 * 16 + 15, int("ff", 16))', [], '255 255'), ('similar example', sim('cs.hexadecimal'), [], '(12, 8)\n200')])

T = 'def shift(message, steps):\n    out = ""\n    for ch in message:\n        if "a" <= ch <= "z":\n            out = out + chr((ord(ch) - ord("a") + steps) % 26 + ord("a"))\n        else:\n            out = out + ch\n    return out\n\ndef byte_count(text):\n    return len(text.encode("utf-8"))\n'
TEXT = Spec(start='', reference=T,
    creative=['ABC = "abcdefghijklmnopqrstuvwxyz"\n\ndef shift(message, steps):\n    return "".join(ABC[(ABC.index(c) + steps) % 26] if c in ABC else c for c in message)\n\ndef byte_count(text):\n    return len(bytes(text, "utf-8"))'],
    wrong=[
        ('no wrap round', T.replace('chr((ord(ch) - ord("a") + steps) % 26 + ord("a"))', 'chr(ord(ch) + steps)'), 'needs_work', 'cs.text-encoding.case.wrap'),
        ('steps always forward', T.replace('+ steps) % 26', '+ abs(steps)) % 26'), 'needs_work', 'cs.text-encoding.case.back'),
        ('counts characters, not bytes', T.replace('len(text.encode("utf-8"))', 'len(text)'), 'needs_work', 'cs.text-encoding.case.bytes'),
        ('contrived: big shifts ignored', T.replace('    out = ""\n', '    if steps > 26:\n        steps = 0\n    out = ""\n'), 'needs_work', 'cs.text-encoding.case.big-steps'),
        ('capitals shifted as if small', T.replace('if "a" <= ch <= "z":', 'if ch.isalpha():'), 'needs_work', 'cs.text-encoding.case.marks'),
        ('a code added to text', T.replace('            out = out + ch\n', '            out = out + ord(ch)\n'), 'execution_error', ('error', 'TypeError', 7)),
        ('a misspelt name', T.replace('    return out\n', '    return outt\n'), 'execution_error', ('error', 'NameError', 8)),
        ('a module the browser does not have', 'import pygame\n' + T, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'next_digit': 'shift', 'd': 'ch'},
    claims=[('predict: y plus 2', 'print(chr(ord("y") + 2))', [], '{'), ('guided: emoji bytes', 'print(len("🙂".encode("utf-8")))', [], '4'), ('similar example', sim('cs.text-encoding'), [], '4 0')])

F = 'def to_cents(price):\n    whole, _, part = price.partition(".")\n    part = (part + "00")[:2]\n    return int(whole) * 100 + int(part)\n\ndef add_prices(prices):\n    total = 0\n    for price in prices:\n        total = total + to_cents(price)\n    return f"{total // 100}.{total % 100:02d}"\n'
FLOAT = Spec(start='', reference=F,
    creative=['def to_cents(price):\n    if "." in price:\n        a, b = price.split(".")\n    else:\n        a, b = price, ""\n    return int(a) * 100 + int(b.ljust(2, "0")[:2])\n\ndef add_prices(prices):\n    cents = sum(to_cents(p) for p in prices)\n    return str(cents // 100) + "." + str(cents % 100).zfill(2)'],
    wrong=[
        ('uses float()', 'def to_cents(price):\n    return int(float(price) * 100)\n\ndef add_prices(prices):\n    total = 0\n    for price in prices:\n        total = total + to_cents(price)\n    return f"{total // 100}.{total % 100:02d}"\n', 'needs_work', 'cs.float-limits.case.cents'),
        ('cents padded on the left', F.replace('part = (part + "00")[:2]', 'part = part.zfill(2)'), 'needs_work', 'cs.float-limits.case.half'),
        ('the total added as floats', F.replace('    total = 0\n    for price in prices:\n        total = total + to_cents(price)\n    return f"{total // 100}.{total % 100:02d}"\n', '    total = 0\n    for price in prices:\n        total = total + float(price)\n    return str(total)\n'), 'needs_work', 'cs.float-limits.case.total'),
        ('contrived: no point means cents', F.replace('    whole, _, part = price.partition(".")\n', '    if "." not in price:\n        return int(price)\n    whole, _, part = price.partition(".")\n'), 'needs_work', 'cs.float-limits.case.whole'),
        ('contrived: adds only the first three', F.replace('    for price in prices:\n', '    for price in prices[:3]:\n'), 'needs_work', 'cs.float-limits.case.many'),
        ('splits at a point that may not be there', 'def to_cents(price):\n    whole, part = price.split(".")\n    return int(whole) * 100 + int((part + "00")[:2])\n\ndef add_prices(prices):\n    total = 0\n    for price in prices:\n        total = total + to_cents(price)\n    return f"{total // 100}.{total % 100:02d}"\n', 'execution_error', ('error', 'ValueError', 2)),
        ('dollars joined as a number', F.replace('    return f"{total // 100}.{total % 100:02d}"\n', '    return total // 100 + "." + str(total % 100)\n'), 'execution_error', ('error', 'TypeError', 10)),
        ('a misspelt name', F.replace('    return int(whole) * 100 + int(part)\n', '    return int(hole) * 100 + int(part)\n'), 'execution_error', ('error', 'NameError', 4)),
        ('a module the browser does not have', 'import pygame\n' + F, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'to_seconds': 'to_cents', 'time': 'price', 'minutes': 'whole', 'seconds': 'part'},
    claims=[('discover: 0.1 + 0.2', 'print(0.1 + 0.2)', [], '0.30000000000000004'), ('predict: 0.5 is exact', 'print((0.5).as_integer_ratio(), (0.1).as_integer_ratio()[1] > 2 ** 50)', [], '(1, 2) True'),
            ('guided: ten dimes', 'total = 0\nfor n in range(10):\n    total = total + 0.1\nprint(total)', [], '0.9999999999999999'), ('similar example', sim('cs.float-limits'), [], '187\n07')])

L = 'def find(items, target):\n    steps = 0\n    for i in range(len(items)):\n        steps = steps + 1\n        if items[i] == target:\n            return [i, steps]\n    return [-1, steps]\n'
LINEAR = Spec(start='', reference=L,
    creative=['def find(items, target):\n    if target in items:\n        i = items.index(target)\n        return [i, i + 1]\n    return [-1, len(items)]'],
    wrong=[
        ('the look counted after the match', L.replace('        steps = steps + 1\n        if items[i] == target:\n            return [i, steps]\n', '        if items[i] == target:\n            return [i, steps]\n        steps = steps + 1\n'), 'needs_work', 'cs.linear-search.case.middle'),
        ('no looks counted when missing', L.replace('    return [-1, steps]', '    return [-1, 0]'), 'needs_work', 'cs.linear-search.case.missing'),
        ('contrived: a first match takes no looks', L.replace('    steps = 0\n', '    steps = 0\n    if items and items[0] == target:\n        return [0, 0]\n'), 'needs_work', 'cs.linear-search.case.first'),
        ('contrived: a repeated target gives the later one', L.replace('    steps = 0\n', '    steps = 0\n    if items.count(target) > 1:\n        return [len(items) - 1 - items[::-1].index(target), len(items)]\n'), 'needs_work', 'cs.linear-search.case.repeats'),
        ('contrived: an empty shelf is found at 0', L.replace('    steps = 0\n', '    steps = 0\n    if not items:\n        return [0, 0]\n'), 'needs_work', 'cs.linear-search.case.empty'),
        ('one position too many', L.replace('range(len(items))', 'range(len(items) + 1)'), 'execution_error', ('error', 'IndexError', 5)),
        ('a misspelt name', L.replace('if items[i] == target', 'if item[i] == target'), 'execution_error', ('error', 'NameError', 5)),
        ('a module the browser does not have', 'import pygame\n' + L, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'first_even': 'find', 'numbers': 'items', 'looks': 'steps'},
    claims=[('predict: a missing item needs every look', L + '\nprint(find(list(range(1000)), -5))', [], '[-1, 1000]'), ('similar example', sim('cs.linear-search'), [], '[8, 3]')])

S = 'def binary_find(items, target):\n    low = 0\n    high = len(items) - 1\n    steps = 0\n    while low <= high:\n        middle = (low + high) // 2\n        steps = steps + 1\n        if items[middle] == target:\n            return [middle, steps]\n        if items[middle] < target:\n            low = middle + 1\n        else:\n            high = middle - 1\n    return [-1, steps]\n'
BSEARCH = Spec(start='', reference=S, creative=[],
    wrong=[
        ('a linear search instead', 'def binary_find(items, target):\n    for i in range(len(items)):\n        if items[i] == target:\n            return [i, i + 1]\n    return [-1, len(items)]\n', 'needs_work', 'cs.binary-search.case.found'),
        ('the loop stops one look early', S.replace('while low <= high:', 'while low < high:'), 'needs_work', 'cs.binary-search.case.missing'),
        ('low starts at 1', S.replace('    low = 0\n', '    low = 1\n'), 'needs_work', 'cs.binary-search.case.first'),
        ('contrived: gives up after four looks', S.replace('while low <= high:', 'while low <= high and steps < 4:'), 'needs_work', 'cs.binary-search.case.long'),
        ('contrived: a list of one is searched as empty', S.replace('    low = 0\n', '    if len(items) == 1:\n        return [-1, 0]\n    low = 0\n'), 'needs_work', 'cs.binary-search.case.single'),
        ('a misspelt name', S.replace('middle = (low + high) // 2', 'middle = (low + hihg) // 2'), 'execution_error', ('error', 'NameError', 6)),
        ('a module the browser does not have', 'import pygame\n' + S, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'secret': 'target', 'lo': 'low', 'hi': 'high', 'mid': 'middle', 'guesses': 'steps'},
    claims=[('predict: about ten looks for 1,000', S + '\nprint(max(binary_find(list(range(1000)), t)[1] for t in range(1000)))', [], '10'),
            ('discover: looks at the middle of seven', 'print((0 + 6) // 2)', [], '3'), ('similar example', sim('cs.binary-search'), [], '73 6')])
BSEARCH.creative = [BSEARCH.reference.replace('steps = steps + 1', 'steps += 1')]

C = 'def linear_worst(n):\n    return n\n\ndef binary_worst(n):\n    steps = 0\n    while n > 0:\n        n = n // 2\n        steps = steps + 1\n    return steps\n\ndef compare(sizes):\n    table = []\n    for s in sizes:\n        table.append([s, linear_worst(s), binary_worst(s)])\n    return table\n'
COUNT = Spec(start='', reference=C, creative=[],
    wrong=[
        ('one halving too few', C.replace('while n > 0:', 'while n > 1:'), 'needs_work', 'cs.counting-steps.case.eight'),
        ('an empty list needs a look', C.replace('    return steps\n', '    return max(1, steps)\n'), 'needs_work', 'cs.counting-steps.case.zero'),
        ('the size put last', C.replace('table.append([s, linear_worst(s), binary_worst(s)])', 'table.append([linear_worst(s), binary_worst(s), s])'), 'needs_work', 'cs.counting-steps.case.table'),
        ('contrived: never more than 10', C.replace('    return steps\n', '    return min(steps, 10)\n'), 'needs_work', 'cs.counting-steps.case.big'),
        ('contrived: odd sizes rounded up', C.replace('    for s in sizes:\n', '    for s in sizes:\n        if s % 2 and s > 1:\n            s = s + 1\n'), 'needs_work', 'cs.counting-steps.case.odd'),
        ('append() given two values', C.replace('table.append([s, linear_worst(s), binary_worst(s)])', 'table.append(s, linear_worst(s))'), 'execution_error', ('error', 'TypeError', 14)),
        ('a misspelt function name', C.replace('binary_worst(s)])', 'binary_wrost(s)])'), 'execution_error', ('error', 'NameError', 14)),
        ('a module the browser does not have', 'import pygame\n' + C, 'unsupported', ('unsupported', 'ModuleNotFoundError', 1)),
    ],
    renamed={'value': 'n', 'doublings': 'steps', 'limit': 'n'},
    claims=[('predict: doubling adds one look', C + '\nprint(binary_worst(2000) - binary_worst(1000))', [], '1'), ('similar example', sim('cs.counting-steps'), [], '10')])
COUNT.creative = [C.replace('steps = steps + 1', 'steps += 1')]

globals().update({f'{k}_u01': v for k, v in make_tests('cs.u01', {'cs.binary': BINARY, 'cs.hexadecimal': HEX, 'cs.text-encoding': TEXT, 'cs.float-limits': FLOAT},
                                                         ['Lamplighter', 'Flag painter', 'Cipher clerk', 'Honest ledger']).items()})
globals().update({f'{k}_u03': v for k, v in make_tests('cs.u03', {'cs.linear-search': LINEAR, 'cs.binary-search': BSEARCH, 'cs.counting-steps': COUNT},
                                                         ['Archivist', 'Halver', 'Step counter']).items()})
