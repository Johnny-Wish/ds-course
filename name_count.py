from collections import Counter
import jieba


class Name:
    compound_surnames = ["诸葛", "司马", "公孙", "上官", "欧阳"]

    def __init__(self, full_name, alias=None):
        self.alias = alias
        self.surname, self.given_name = Name.split_name(full_name)

    @staticmethod
    def split_name(name):
        for compound in Name.compound_surnames:
            if name.find(compound) == 0:
                return compound, name[len(compound):]

        return name[0], name[1:]

    @property
    def fullname(self):
        return self.surname + self.given_name

    def match(self, other):
        return other in [self.fullname, self.given_name, self.alias]

    def __repr__(self):
        return "<{}:, surname={}, given-name={}, alias={}>".format(self.fullname, self.surname, self.given_name,
                                                                   self.alias)

    def __str__(self):
        return self.__repr__().replace("-", " ")

    def total_occurrence(self, counter: dict):
        return counter.get(self.fullname, 0) + counter.get(self.alias, 0) + counter.get(self.given_name, 0)


def parse_name_entry(s: str):
    left_pos = s.find("(")
    right_pos = s.find(")")

    if left_pos >= 0 and right_pos > 0:
        full_name = s[:left_pos]
        alias = s[left_pos + 1:right_pos]
    elif left_pos < 0 and right_pos < 0:
        full_name = s
        alias = None
    else:
        raise ValueError("Mismatched parentheses in {}, left = {}, right = {}".format(str, left_pos, right_pos))

    return Name(full_name, alias)


if __name__ == '__main__':
    with open("corpus.txt") as f:
        corpus = f.read()

    with open("name-list.txt") as f:
        names = [parse_name_entry(line) for line in f.readlines() if line.split()]

    tokens = list(jieba.lcut(corpus))
    token_counter = Counter(tokens)
    name_counter = {name: name.total_occurrence(token_counter) for name in names}

    ordered_name_counter = sorted(name_counter.items(), key=lambda p: p[-1], reverse=True)

    n_entries = 30
    for name, count in ordered_name_counter[:n_entries]:
        print(name, count)
