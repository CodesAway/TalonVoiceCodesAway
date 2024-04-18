import re
from io import StringIO


def generate_regex(values: dict, transformations: dict) -> str:
    values_list = []
    for item in values.items():
        values_list.append(item)
        # TODO: support transformations
        print(item)

    values_list.sort(reverse=True, key=lambda e: len(e[1]))
    result = StringIO()
    for name, value in values_list:
        if result.tell() != 0:
            result.write("|")

        result.write(f"(?P<{name}>{re.escape(value)})")

    print(values_list)
    regex = result.getvalue()
    print(regex)

    return regex


def replacement(match: re.Match) -> str:
    group_name = [e[0] for e in match.groupdict().items() if e[1] is not None][0]
    return f"@{group_name}@"


values = {"value1": "ab", "valueA": "a", "value2": "bc"}
# TODO: support transformations
transformations = {}

regex = generate_regex(values, transformations)
text = "a1 bc"
result = re.sub(regex, replacement, text)

print("Result:", result)
