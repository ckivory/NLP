import sys
import math

arg_count = len(sys.argv)
if arg_count != 5:
    raise Exception("Please provide the training, testing, and stopwords files, and k.")

try:
    k = int(sys.argv[4])
except Exception:
    raise Exception("k must be an integer")

# Read training file and format
training_filename = sys.argv[1]
training_lines = open(training_filename, "r").read().split('\n')

training_senses = []
training_sentences = []

sense_inventory = set([])

# Create sense inventory
for training_line in training_lines:
    component = training_line.split('\t')
    training_senses.append(component[0].split(':')[1])

    if component[0] not in sense_inventory:
        sense_inventory.add(component[0].split(':')[1])

    training_sentences.append(component[1])

sorted_sense_inventory = sorted(list(sense_inventory))

# Read test and stopword files
testing_filename = sys.argv[2]
test_sentences = open(testing_filename, "r").read().split('\n')

stopwords_filename = sys.argv[3]
stopwords_set = set(open(stopwords_filename, "r").read().split('\n'))

# Each value represents the index that key word will be represented by in the signature vector
vocabulary = {}
word_index = 0

# Dictionary for each word that returns the frequency of the word in the entire document
frequency_dict = {}

# First key is the category, second key is the word, value is the frequency
frequencies_by_category = {}
for gold_sense in sorted_sense_inventory:
    frequencies_by_category[gold_sense] = {}

if k == 0:
    for sentence_index in range(len(training_sentences)):
        training_sentence = training_sentences[sentence_index]
        current_sense = training_senses[sentence_index]
        words = training_sentence.split(' ')

        for i in range(len(words)):
            word = words[i].lower()

            # For all non-stopwords that contain letters and are not the occurrence itself
            if word[0:12] != "<occurrence>" and word != word.upper() and word not in stopwords_set:
                # Total frequency
                if word not in list(frequency_dict.keys()):
                    frequency_dict[word] = 1
                else:
                    frequency_dict[word] += 1

                    # Only add words to vocab if they have a frequency of at least 2
                    if word not in list(vocabulary.keys()):
                        vocabulary[word] = word_index
                        word_index += 1

                # Frequency per category
                if word not in list(frequencies_by_category[current_sense].keys()):
                    frequencies_by_category[current_sense][word] = 1
                else:
                    frequencies_by_category[current_sense][word] += 1

else:
    for sentence_index in range(len(training_sentences)):
        training_sentence = training_sentences[sentence_index]
        current_sense = training_senses[sentence_index]

        words = training_sentence.split(' ')

        # Look for the occurrence in the sentence
        for i in range(len(words)):
            word = words[i].lower()

            # When you find the occurrence
            if word[0:12] == "<occurrence>":
                # From i backwards by k
                j = i - 1
                while j >= i - k and j > -1:
                    candidate = words[j].lower()
                    if candidate != candidate.upper() and candidate not in stopwords_set:
                        # Total frequency
                        if candidate not in list(frequency_dict.keys()):
                            frequency_dict[candidate] = 1
                        else:
                            frequency_dict[candidate] += 1

                            if candidate not in list(vocabulary.keys()):
                                vocabulary[candidate] = word_index
                                word_index += 1

                        if candidate not in list(frequencies_by_category[current_sense].keys()):
                            frequencies_by_category[current_sense][candidate] = 1
                        else:
                            frequencies_by_category[current_sense][candidate] += 1

                    j -= 1

                # From i forwards by k
                j = i + 1
                while j <= i + k and j < len(words):
                    candidate = words[j].lower()
                    if candidate != candidate.upper() and candidate not in stopwords_set:
                        # Total frequency
                        if candidate not in list(frequency_dict.keys()):
                            frequency_dict[candidate] = 1
                        else:
                            frequency_dict[candidate] += 1
                            if candidate not in list(vocabulary.keys()):
                                vocabulary[candidate] = word_index
                                word_index += 1

                        if candidate not in list(frequencies_by_category[current_sense].keys()):
                            frequencies_by_category[current_sense][candidate] = 1
                        else:
                            frequencies_by_category[current_sense][candidate] += 1

                    j += 1


# Create Signature Vectors that map word indices from vocab onto word frequencies
signature_vectors = {}
for current_sense in sorted_sense_inventory:
    signature_vectors[current_sense] = {}
    for word in list(frequencies_by_category[current_sense].keys()):
        # Only add vocab words to signature vectors
        if word in list(vocabulary.keys()):
            # Set current signature vector entry for current word to the frequency of that word in the category
            signature_vectors[current_sense][vocabulary[word]] = frequencies_by_category[current_sense][word]

# Create Context Vectors
context_vectors = []
for sentence in test_sentences:
    context_vectors.append({})

# Initialize Context Vectors
for sentence_index in range(len(test_sentences)):
    test_sentence = test_sentences[sentence_index]
    sentence_words = test_sentence.split(' ')

    if k == 0:
        # For every word in the test sentence
        for i in range(len(sentence_words)):
            word = sentence_words[i].lower()
            # If the word is in the vocabulary
            if word in list(vocabulary.keys()):
                # If the word is not yet in the context vector
                if vocabulary[word] not in list(context_vectors[sentence_index].keys()):
                    context_vectors[sentence_index][vocabulary[word]] = 1
                else:
                    context_vectors[sentence_index][vocabulary[word]] += 1

    else:
        # Check for the occurrence in the whole sentence
        for i in range(len(sentence_words)):
            word = sentence_words[i].lower()
            # When you find the occurrence
            if word[0:12] == "<occurrence>":
                # From i backwards by k
                j = i - 1
                while j >= i - k and j > -1:
                    candidate = sentence_words[j].lower()
                    if candidate in list(vocabulary.keys()):
                        if vocabulary[candidate] not in list(context_vectors[sentence_index].keys()):
                            context_vectors[sentence_index][vocabulary[candidate]] = 1
                        else:
                            context_vectors[sentence_index][vocabulary[candidate]] += 1
                    j -= 1

                # From i forwards by k
                j = i + 1
                while j <= i + k and j < len(sentence_words):
                    candidate = sentence_words[j].lower()
                    if candidate in list(vocabulary.keys()):
                        if vocabulary[candidate] not in list(context_vectors[sentence_index].keys()):
                            context_vectors[sentence_index][vocabulary[candidate]] = 1
                        else:
                            context_vectors[sentence_index][vocabulary[candidate]] += 1
                    j += 1

# Create Output File
output_filename = testing_filename + ".distsim"
output_file = open(output_filename, "w")

output_file.write("Number of Training Sentences = " + str(len(training_sentences)) + "\n")
output_file.write("Number of Test Sentences = " + str(len(test_sentences)) + "\n")
output_file.write("Number of Gold Senses = " + str(len(list(sense_inventory))) + "\n")
output_file.write("Vocabulary Size = " + str(len(list(vocabulary))) + "\n")

# Create sanitized version of frequency_dict indexed by vocab index
master_frequencies = {}
for key in list(frequency_dict.keys()):
    if key in list(vocabulary.keys()) and frequency_dict[key] > 1:
        master_frequencies[vocabulary[key]] = frequency_dict[key]

# Calculate totals to help with probability calculations
'''
totals_per_category = {}
for gold_sense in sorted_sense_inventory:
    totals_per_category[gold_sense] = 0

master_total = 0

for current_sense in sorted_sense_inventory:
    signature_vector = signature_vectors[current_sense]
    for count in list(signature_vector.values()):
        totals_per_category[current_sense] += count

for total in list(totals_per_category.values()):
    master_total += total
'''


# Output cosine probabilities
def dot_product(vector1, vector2):
    dot = 0

    used_index_set = set([])
    for vector_index in list(vector1.keys()):
        used_index_set.add(vector_index)

    for vector_index in list(vector2.keys()):
        used_index_set.add(vector_index)

    for vector_index in used_index_set:
        x_i = 0
        y_i = 0

        if vector_index in list(vector1.keys()):
            x_i = vector1[vector_index]

        if vector_index in list(vector2.keys()):
            y_i = vector2[vector_index]

        dot += x_i * y_i

    return dot


def magnitude(vector):
    square_sum = 0
    for value in list(vector.values()):
        square_sum += value * value

    return math.sqrt(square_sum)


def cosine_sim(vector1, vector2):
    numerator = dot_product(vector1, vector2)
    denominator = magnitude(vector1) * magnitude(vector2)

    return numerator / denominator


# For every sentence (eventually)
for context_index in range(len(context_vectors)):
    context_vector = context_vectors[context_index]
    word_index_list = list(context_vector.keys())

    chances_by_category = {}
    for gold_sense in sorted_sense_inventory:
        chances_by_category[gold_sense] = 0

    for word_index in word_index_list:

        for current_sense in sorted_sense_inventory:

            signature_vector = signature_vectors[current_sense]

            if word_index in list(signature_vector.keys()):
                cosine_prob = cosine_sim(context_vector, signature_vector)
                chances_by_category[current_sense] = cosine_prob

    # Sort by similarity then by name
    temp_chances = list(chances_by_category.values())
    temp_categories = list(chances_by_category.keys())

    sorted_chances = []
    sorted_categories = []

    while len(temp_chances) > 0:
        # Find maximum
        max_chance_index = 0
        for i in range(1, len(temp_chances)):
            if temp_chances[i] > temp_chances[max_chance_index]:
                max_chance_index = i
            elif temp_chances[i] == temp_chances[max_chance_index] and temp_categories[i] < temp_categories[max_chance_index]:
                max_chance_index = i

        sorted_chances.append(temp_chances.pop(max_chance_index))
        sorted_categories.append(temp_categories.pop(max_chance_index))

    for i in range(len(sorted_categories)):
        current_sense = sorted_categories[i]
        category_chance = sorted_chances[i]

        output_file.write(current_sense + "(" + str(round(category_chance, 2)) + ")")
        if i < len(sorted_categories) - 1:
            output_file.write(" ")

    if context_index < len(context_vectors) - 1:
        output_file.write('\n')
