import sys

arg_count = len(sys.argv)
if arg_count != 3:
    raise Exception("Please provide the grammar and sentence files")

grammar_filename = sys.argv[1]
sentence_filename = sys.argv[2]

grammar_lines = open(grammar_filename, "r").read().split('\n')

grammar = {}
terminals = {}

for line in grammar_lines:
    tokens = list(filter(None, line.split(' ')))

    # Non-Terminals
    if len(tokens) > 4:
        # Nested dictionary to lookup valid tags for left and right operands
        if tokens[2] not in grammar:
            grammar[tokens[2]] = {}
        if tokens[3] not in grammar[tokens[2]]:
            grammar[tokens[2]][tokens[3]] = []
        grammar[tokens[2]][tokens[3]].append(tokens[0])

    # Terminals
    elif len(tokens) == 4:
        # Single dictionary to store tags that can apply to single words
        if tokens[2] not in terminals:
            terminals[tokens[2]] = []
        terminals[tokens[2]].append(tokens[0])

sentence_lines = list(filter(None, open(sentence_filename, "r").read().split('\n')))

for sentence in sentence_lines:
    words = list(filter(None, sentence.split(' ')))

    print("PARSING SENTENCE: " + sentence)

    # Nested dictionary to store matrix
    # Each element is a list so I can store back pointers
    table = {}
    n = len(words)

    # Initialize empty table
    for row in range(1, n+1):
        table[row] = {}
        for col in range(row, n+1):
            table[row][col] = []

    # Matrix diagonals
    for i in range(1, n+1):
        table[i][i] = terminals[words[i-1]]

    # Non-trivial cases
    for col in range(1, n+1):
        # For column from bottom to top
        row = col-1
        while row > 0:
            # For every possible partition
            for s in range(row+1, col+1):
                # Existing tags
                lefts = table[row][s-1]
                rights = table[s][col]

                # Compare all combinations of left and right to the grammar
                if len(lefts) > 0 and len(rights) > 0:
                    for left in lefts:
                        for right in rights:
                            if left in grammar:
                                if right in grammar[left]:
                                    for tag in grammar[left][right]:
                                        table[row][col].append(tag)

            row -= 1

    num_parses = 0
    for tag in table[1][n]:
        if tag == "S":
            num_parses += 1

    print("NUMBER OF PARSES FOUND: " + str(num_parses))

    # Print the table
    print("TABLE:")
    for row in range(1, n+1):
        for col in range(row, n+1):
            tags = ""
            if len(table[row][col]) > 0:
                sorted_taglist = sorted(table[row][col])
                for tag_num in range(len(sorted_taglist)):

                    tags += sorted_taglist[tag_num]
                    if tag_num < len(sorted_taglist) - 1:
                        tags += " "
            else:
                tags = "-"

            print("cell[" + str(row) + ", " + str(col) + "]: " + tags)
    print()

