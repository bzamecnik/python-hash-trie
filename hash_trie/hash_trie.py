'''
An implementation of a plain and compressed trie on strings.
'''

# Trie structure:
# Nodes in trie are tuples (children, is_terminal).
# Children is a hash map from key to node. is_terminal is a boolean indicating
# that the path from the root to this node represents a word, otherwise it is
# just a prefix of other words.
# For plain tries the keys are just characters, for compressed ones the keys
# are strings.

def make_trie(words):
    'Creates a basic uncompressed trie from a sorted list of words.'
    trie = ({}, False)
    for word in words:
        node, is_terminal = trie
        size = len(word)
        for i, char in enumerate(word):
            is_terminal = i == size - 1
            if char not in node:
                node[char] = ({}, is_terminal)
            node, is_terminal = node[char]
    return trie

# TODO: try to build the compressed trie right from the list of words

def compress_trie(trie):
    '''
    Compresses an existing trie, ie. collapses each sequence of non-terminal
    nodes with one child into a single nodes whose key is concatenation of the
    original keys.
    
    The method is idempotent, ie. calling it repeatedly produces the same
    result.
    
    The implementation is recursive (first a top-down pass, then bottom-up
    backtracking).
    '''
    def compress_subtrie(trie, prefix=''):
        '''
        Compresses a (sub)trie with given key prefix. In the top-down pass
        the original keys in single-child sequences are concatenated and in
        the backtracking the result is returned back.
        '''
        children, is_terminal = trie
        child_count = len(children)
        if child_count == 0:
            # not interesting, the base case
            return trie, prefix
        elif child_count == 1:
            for key, child in children.items():
                # just on iteration to obtain the single key-value pair
                next_prefix = key if is_terminal else prefix + key
                comp_child, comp_key = compress_subtrie(child, next_prefix)
                comp_children = {comp_key: comp_child} \
                    if prefix == '' or is_terminal else comp_child[0]
                return (comp_children, comp_child[1] or is_terminal), prefix \
                    if is_terminal else comp_key
        else: # child_count > 1
            # not interesting, just compress each child
            # TODO: try to merge similar cases for child_count >= 1
            comp_children = {}
            for key, child in children.items():
                comp_child, comp_key = compress_subtrie(child, key)
                comp_children[comp_key] = comp_child
            return (comp_children, is_terminal), prefix
    
    return compress_subtrie(trie)[0]

def in_trie(word, trie):
    'Tests whether a given words is cointained in the trie.'
    children, is_terminal = trie
    if len(word) == 0:
        return is_terminal
    for char in word:
        if char in children:
            child = children[char]
            return in_trie(word[1:], child)
    return False

def in_compressed_trie(word, trie):
    'Tests whether a given words is cointained in the compressed trie.'
    children, is_terminal = trie
    if len(word) == 0:
        return is_terminal
    for i in range(len(word)):
        key = word[:i+1]
        if key in children:
            child = children[key]
            return in_compressed_trie(word[i+1:], child)
    return False

def print_trie(trie):
    def print_subtree(root, level):
        children, _ = root
        for key in sorted(children.keys()):
            child = children[key]
            _, is_terminal = child
            print(level * ('*' if is_terminal else '-'), key)
            print_subtree(child, level + 1)
    print_subtree(trie, 1)

def count_nodes(trie, only_terminal=False):
    children, is_terminal = trie
    if only_terminal:
        count = 1 if is_terminal else 0
    else:
        count = 1
    for key, child in children.items():
        count = count + count_nodes(child, only_terminal)
    return count

def load_words(filename):
    with open(filename, 'r') as file:
        words =[word.strip() for word in file.readlines()]
    return words

#if __name__ == '__main__':

    # 235886 words
    #words = load_words('/usr/share/dict/words')

    # 792777 nodes, 235886 terminal nodes
    #trie = make_trie(words)
    # 318795 nodes, 235886 terminal nodes
    #trie_compressed = compress_trie(trie)

    # 100 loops, best of 3: 4.12 ms per loop
    #%timeit 'Zyzzogeton' in words
    # 100000 loops, best of 3: 5.1 µs per loop
    #%timeit in_trie('Zyzzogeton', trie)
    # 100000 loops, best of 3: 2.22 µs per loop
    #%timeit in_compressed_trie('Zyzzogeton', trie_compressed)
