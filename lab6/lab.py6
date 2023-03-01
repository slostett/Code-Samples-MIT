# NO ADDITIONAL IMPORTS!
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self):
        self.value = None
        self.children = {}
        self.type = None

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        if self.type is None:  # check to see if we have yet assigned type
            self.type = type(key)  # if we have not yet assigned type, let it be the type of the key.
        elif type(key) != self.type:  # if we have already defined a type, raise error if key of a new type
            raise TypeError

        if len(key) == 1:  # if len key has reached one, set current value to be value
            if key[0:1] not in self.children:  # if not in children add trie with value of interest
                new_trie = Trie()
                new_trie.value = value
                self.children[key[0:1]] = new_trie  # if already in children simply replace the value
            else:
                self.children[key[0:1]].value = value
        else:  # if len key is not one, create child trie
            if key[0:1] in self.children:  # if key already defined add rather than replace
                self.children[key[0:1]].__setitem__(key[1:], value)
            else:
                self.children[key[0:1]] = Trie()
                self.children[key[0:1]].__setitem__(key[1:], value)

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        if self.type is None:  # check to see if we have yet assigned type
            self.type = type(key)  # if we have not yet assigned type, let it be the type of the key.
        elif type(key) != self.type:  # if we have already defined a type, raise error if key of a new type
            raise TypeError

        if key[0:1] not in self.children:  # membership check
            raise KeyError

        if len(key) == 1:  # if len key has reached one, return current value
            if self.children[key].value is None:
                raise KeyError

            return self.children[key].value

        else:  # if len key is not one, look in child trie
            return self.children[key[0:1]].__getitem__(key[1:])

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        if self[key] is None:
            raise KeyError

        self[key] = None

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.
        """
        try:  # see if we can find a value at the input key
            value = self.__getitem__(key)
        except:  # if we can't return False
            return False

        if value is None:  # if value is none we also want to return False
            return False
        else:
            return True

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """
        for child in self.children:  # iterate through children
            if self.children[child].children == {}:  # if children dict is empty
                yield (child, self.children[child].value)  # yield tuple of (letter, value)
            elif self.children[child].value is not None:  # if has value send it up
                yield (child, self.children[child].value)
            for item in self.children[child]:  # iterate through items yielded on call on sub trie
                if item[1] == None:
                    continue
                yield (child + item[0], item[1])  # yield letter + previous letter combos

    def get_children_of(self, key):
        '''
        :param key: gets children sequences as if we started with key
        :return: trie where head node is end of key
        '''

        if self.type is None:  # check to see if we have yet assigned type
            raise KeyError

        if len(key) == 0:
            return self

        if key[0:1] not in self.children:  # membership check
            raise KeyError

        if len(key) == 1:  # if len key has reached one, return current value
            return self.children[key]
        else:  # if len key is not one, look in child trie
            return self.children[key[0:1]].get_children_of(key[1:])


def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    sentences = [x.split() for x in tokenize_sentences(text)]
    freq_dict = {}
    words = set()

    for sentence in sentences:
        for word in sentence:
            if word in words:
                freq_dict[word] += 1
            else:
                freq_dict[word] = 1
                words.add(word)

    word_freqs = Trie()

    for word in freq_dict:
        word_freqs[word] = freq_dict[word]

    return word_freqs


def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    sentences = [tuple(x.split()) for x in tokenize_sentences(text)]
    freq_dict = {}
    phrases = set()
    for sentence in sentences:
        if sentence in phrases:
            freq_dict[sentence] += 1
        else:
            freq_dict[sentence] = 1
            phrases.add(sentence)

    word_freqs = Trie()

    for word in freq_dict:
        word_freqs[word] = freq_dict[word]

    return word_freqs


def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    """
    if type(prefix) != trie.type:
        raise TypeError

    try:
        start = trie.get_children_of(prefix)
    except:
        return []
    freq_dict = {}  # dict where keys are item locations, values are their frequencies
    seen = set()

    for item in start:
        if item[0] in seen:
            freq_dict[prefix + item[0]] += item[1]
        else:
            freq_dict[prefix + item[0]] = item[1]
            seen.add(item[0])

    if prefix in trie:
        freq_dict[prefix] = trie[prefix]

    if max_count is None or max_count > len(freq_dict):
        max_count = len(freq_dict)

    to_return = []

    for i in range(max_count):
        max_val = max(freq_dict, key=lambda x: freq_dict[x])
        to_return.append(max_val)
        freq_dict[max_val] = -1

    return to_return


def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    suggestions = autocomplete(trie, prefix, max_count)
    possibilities_dict = {}

    if len(suggestions) == max_count:
        return suggestions

    for letter in list('abcdefghijklmnopqrstuvwxyz'):  # insertion/replacement
        for i in range(len(prefix)):

            test_word_insert = prefix[:i] + letter + prefix[i:]  # insertion
            if test_word_insert in trie and test_word_insert not in suggestions:
                possibilities_dict[test_word_insert] = trie[test_word_insert]

            test_word_replace = prefix[:i] + letter + prefix[i + 1:]  # replacement
            if test_word_replace in trie and test_word_replace not in suggestions:
                possibilities_dict[test_word_replace] = trie[test_word_replace]

    for i in range(len(prefix)):  # deletion
        test_word = prefix[:i] + prefix[i + 1:]
        if test_word in trie and test_word not in suggestions:
            possibilities_dict[test_word] = trie[test_word]

    for i in range(len(prefix) - 1):  # transpose
        test_word = prefix[:i] + prefix[i:i+2][::-1] + prefix[i+2:]
        if test_word in trie and test_word not in suggestions:
            possibilities_dict[test_word] = trie[test_word]

    if max_count is None or max_count > len(possibilities_dict) + len(suggestions):
        max_count = len(possibilities_dict) + len(suggestions)

    while len(suggestions) < max_count:
        max_val = max(possibilities_dict, key=lambda x: possibilities_dict[x])
        suggestions.append(max_val)
        possibilities_dict[max_val] = -1

    return suggestions


def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    if len(pattern) == 0:  # base case
        if trie.value is not None:
            return [('', trie.value)]
        else:
            return []
    elif pattern[0] not in ['*', '?']:  # if we have a regular old letter
        if pattern[0] in trie.children:
            to_return = word_filter(trie.children[pattern[0]], pattern[1:])

            for i in range(len(to_return)):
                # print(i, pattern, to_return)
                to_return[i] = (pattern[0] + to_return[i][0], to_return[i][1])
            return to_return
        else:
            return []

    elif pattern[0] == '?':  # if the next character is ?, consider all children
        to_return = []
        for sequence in trie.children:
            to_add = word_filter(trie.children[sequence], pattern[1:])
            for i in range(len(to_add)):
                to_return.append((sequence + to_add[i][0], to_add[i][1]))
        return to_return

    elif pattern[0] == '*':  # if star
        if len(pattern) == 1:  # if we have reached the end, return all following sequences
            if trie.value is not None:
                return [x for x in trie] + [('', trie.value)]  # ensure the head node is included
            return [x for x in trie]
        if pattern[1] == '*':
            return word_filter(trie, '*' + pattern[2:])  # if the next character is a star, its as if there's 1*
        if pattern[1] == '?':
            return word_filter(trie, '?*' + pattern[2:])  # if next character is ?, same as if order were flipped
        to_return = []
        for letter in trie.children:
            if letter == pattern[1]: # if this is the case we can exit the * part of the matching
                to_add = word_filter(trie.children[letter], pattern) + word_filter(trie.children[letter], pattern[2:])
            else:  # if not the case, continue by running on the next trie down this path
                to_add = word_filter(trie.children[letter], pattern)
            for i in range(len(to_add)): # finally send the possibilities up
                to_return.append((letter + to_add[i][0], to_add[i][1]))

        to_return_unique = set()
        for item in to_return:  # ensure only unique items are included
            if item not in to_return_unique:
                to_return_unique.add(item)

        return list(to_return_unique)

# you can include test cases of your own in the block below.
if __name__ == '__main__':
    t = Trie()
    t[(1, 0, 0)] = 'tomato'
    t[(2, 0)] = 'ferret'
    t[(1, 0, 1)] = 'dog'
    t[(2,)] = 'cat'
    t[(2, 0)] = True
    kidz = t.get_children_of(())
    for i in kidz:
        print(i)
