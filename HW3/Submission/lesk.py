import sys

arg_count = len(sys.argv)
if arg_count != 4:
    raise Exception("Please provide the test, definitions, and stopwords files.")

test_sentences_filename = sys.argv[1]
test_sentences_lines = open(test_sentences_filename, "r").read().split('\n')

definitions_filename = sys.argv[2]
definitions_lines = open(definitions_filename, "r").read().split('\n')

stopwords_filename = sys.argv[3]
stopwords_set = set(open(stopwords_filename, "r").read().split('\n'))


sense_names = []
sense_definitions = []
sense_examples = []

for definition_line in definitions_lines:
    definition_components = definition_line.split('\t')
    sense_names.append(definition_components[0])
    sense_definitions.append(definition_components[1])
    sense_examples.append(definition_components[2])


output_filename = test_sentences_filename + ".lesk"
output_file = open(output_filename, "w")


def find_overlap(words, definition, example, stopwords):

    overlap = 0

    seen_words = set([])

    for word_index in range(len(words)):
        word = words[word_index].lower()
        if word[0:12] != "<occurrence>" and word != word.upper():
            if (word in definition or word in example) and word not in stopwords:
                if word not in seen_words:
                    overlap += 1
                    seen_words.add(word)

    return overlap


for sentence_index in range(len(test_sentences_lines)):
    test_sentence = test_sentences_lines[sentence_index]
    sentence_words = test_sentence.split(' ')

    rankings = []
    for i in range(len(sense_definitions)):
        sense_definition = sense_definitions[i]
        sense_example = sense_examples[i]

        # TODO: Calculate ranking based on overlap
        rankings.append(find_overlap(sentence_words, sense_definition, sense_example, stopwords_set))

    # Sort senses by ranking first, then by name
    temp_sense_names = sense_names.copy()
    temp_rankings = rankings.copy()

    sorted_sense_names = []
    sorted_rankings = []

    while len(temp_rankings) > 0:
        max_ranking_index = 0
        for j in range(1, len(temp_rankings)):
            if temp_rankings[j] > temp_rankings[max_ranking_index]:
                max_ranking_index = j
            elif temp_rankings[j] == temp_rankings[max_ranking_index] and temp_sense_names[j] < temp_sense_names[max_ranking_index]:
                max_ranking_index = j

        sorted_sense_names.append(temp_sense_names.pop(max_ranking_index))
        sorted_rankings.append(temp_rankings.pop(max_ranking_index))

    for i in range(len(sorted_sense_names)):
        sense_name = sorted_sense_names[i]
        output_file.write(sense_name + "(" + str(sorted_rankings[i]) + ") ")

    output_file.write('\n')
