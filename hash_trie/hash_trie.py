'''
An implementation of a plain and compressed trie on strings.

from hash_trie import Trie

words = ['foo', 'foobar', 'fuck']

trie = Trie.from_list(words)
compressed_trie = trie.compress(words)

assert ('foo' in trie) == True
assert ('foobar' in compressed_trie) == True
assert ('spam' in compressed_trie) == False
'''

class Trie(object):
    '''
    Trie structure:
    
    Nodes in trie are tuples (children, is_terminal).
    
    Children is a hash map from key to node. is_terminal is a boolean indicating
    that the path from the root to this node represents a word, otherwise it is
    just a prefix of other words.
    
    For plain tries the keys are just characters, for compressed ones the keys
    are strings.
    '''
    
    def __init__(self, words, compressed=False):
        def uncompressed_from_list(words):
            'Creates a basic uncompressed trie from a sorted list of words.'
            root = ({}, False)
            for word in words:
                node, is_terminal = root
                size = len(word)
                for i, char in enumerate(word):
                    is_terminal = i == size - 1
                    if char not in node:
                        node[char] = ({}, is_terminal)
                    node, is_terminal = node[char]
            return root

        # TODO: try to build the compressed trie right from the list of words

        def compress_subtrie(root, prefix=''):
            '''

            Compresses this trie into another object, ie. collapses each sequence
            of non-terminal nodes with one child into a single nodes whose key is
            concatenation of the original keys.

            The method is idempotent, ie. calling it repeatedly produces the same
            result.

            The implementation is recursive (first a top-down pass, then bottom-up
            backtracking).
            
            Compresses a (sub)trie with given key prefix. In the top-down pass
            the original keys in single-child sequences are concatenated and in
            the backtracking the result is returned back.
            '''
            children, is_terminal = root
            child_count = len(children)
            if child_count == 0:
                # not interesting, the base case
                return root, prefix
            elif child_count == 1:
                for key, child in children.items():
                    # just on iteration to obtain the single key-value pair
                    next_prefix = key if is_terminal else prefix + key
                    comp_child, comp_key = compress_subtrie(child, next_prefix)
                    comp_children = {comp_key: comp_child} \
                        if prefix == '' or is_terminal else comp_child[0]
                    return (comp_children, comp_child[1] or is_terminal), \
                        prefix if is_terminal else comp_key
            else: # child_count > 1
                # not interesting, just compress each child
                # TODO: try to merge similar cases for child_count >= 1
                comp_children = {}
                for key, child in children.items():
                    comp_child, comp_key = compress_subtrie(child, key)
                    comp_children[comp_key] = comp_child
                return (comp_children, is_terminal), prefix
        
        root = uncompressed_from_list(words)
        if compressed:
            root = compress_subtrie(root)[0]
        
        self.root = root
        self.is_compressed = compressed

    def __contains__(self, word):
        'Tests whether a given words is contained in the trie.'
        
        def in_trie(word, trie):
            children, is_terminal = trie
            word_length = len(word)
            if word_length == 0:
                return is_terminal
            for i in range(word_length if self.is_compressed else 1):
                key = word[:i+1]
                child = children.get(key)
                if child is not None:
                    return in_trie(word[i+1:], child)
            return False
        
        return in_trie(word, self.root)

    def print_trie(self):
        def print_subtree(root, level):
            children, _ = root
            for key in sorted(children.keys()):
                child = children[key]
                _, is_terminal = child
                print(level * ('*' if is_terminal else '-'), key)
                print_subtree(child, level + 1)
        print_subtree(self.root, 1)

    def count_nodes(self, only_terminal=False):
        def _count_nodes(trie, only_terminal):
            children, is_terminal = trie
            if only_terminal:
                count = 1 if is_terminal else 0
            else:
                count = 1
            for key, child in children.items():
                count = count + _count_nodes(child, only_terminal)
            return count
        return _count_nodes(self.root, only_terminal)

def load_words(filename):
    with open(filename, 'r') as file:
        words = [word.strip() for word in file.readlines()]
    return words

#if __name__ == '__main__':

    # 235886 words
    #words = load_words('/usr/share/dict/words')

    # 2.11 s, 792777 nodes, 235886 terminal nodes
    #trie = make_trie(words)
    # 1.09 s, 318795 nodes, 235886 terminal nodes
    #trie_compressed = compress_trie(trie)

    # 100 loops, best of 3: 4.12 ms per loop
    #%timeit 'Zyzzogeton' in words
    # 100000 loops, best of 3: 5.1 µs per loop
    #%timeit in_trie('Zyzzogeton', trie)
    # 100000 loops, best of 3: 2.22 µs per loop
    #%timeit in_compressed_trie('Zyzzogeton', trie_compressed)
