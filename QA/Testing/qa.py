import nltk
import sys
import math


'''   Begin partner code imports   '''

import re
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet


'''   End partner code imports   '''


# TODO: Create an array of all stories, nested array for all questions, and then produce all answers in a for loop

if len(sys.argv) != 2:
    raise Exception("Please provide the input file")

input_filename = sys.argv[1]
input_file = open(input_filename)

input_lines = open(input_filename, "r").read().split('\n')
input_directory = input_lines[0]

# Test data
all_stories = []
all_questions_lists = []

for input_index in range(1, len(input_lines)):
    storyID = input_lines[input_index]
    story_filename = storyID + ".story"
    questions_filename = storyID + ".questions"
    answers_filename = storyID + ".answers"

    split_story = story_filename.split('.')
    split_questions = questions_filename.split('.')
    split_answers = answers_filename.split('.')

    try:
        story_file = open(story_filename, "r")
    except Exception:
        raise Exception("Story file " + story_filename + " not found.")

    try:
        questions_file = open(questions_filename, "r")
    except Exception:
        raise Exception("Questions file " + questions_filename + " not found.")

    try:
        answers_file = open(answers_filename, "r")
    except Exception:
        raise Exception("Answers file " + answers_filename + " not found.")

    # Get rid of blank lines
    questions_lines_raw = questions_file.readlines()
    questions_lines = []
    for line in questions_lines_raw:
        if len(line) == 0 or line == "\n":
            pass
        else:
            questions_lines.append(line)

    # Split into sentences
    story_lines_raw = story_file.readlines()
    story_lines = []
    built_line = ""
    for line in story_lines_raw:
        if len(line) == 0 or line == "\n":
            story_lines.append(built_line)
            built_line = ""
        else:
            for char in line:
                if char != '\n':
                    built_line += char
                else:
                    built_line += " "   # Might need to do something different to handle the last case

    if len(built_line) > 0:
        story_lines.append(built_line)
        built_line = ""

    # Split questions into IDs, Texts, and Difficulties
    QIDs = []
    QTexts = []
    QDiffs = []
    for line in questions_lines:
        tag = line.split(':')[0]
        if tag == "QuestionID":
            QIDs.append(line[12:].strip('\n'))
        elif tag == "Question":
            QTexts.append(line[10:])
        elif tag == "Difficulty":
            QDiffs.append(line[12:])

    # Split story into headline, date, ID, and text
    headline = story_lines[0][10:]
    date = story_lines[1][6:]
    storyID = story_lines[2][9:]

    story_text_lines = []
    # Make sure I'm not including tag lines in the story text
    for line_index in range(len(story_lines)):
        line = story_lines[line_index]
        if line[:9] == "HEADLINE:" or line[:5] == "DATE:" or line[:8] == "STORYID:" or line[:5] == "TEXT:":
            pass
        else:
            story_text_lines.append(story_lines[line_index])

    all_stories.append(story_text_lines)
    all_questions_lists.append((QIDs, QTexts, QDiffs))


'''   Begin partner code initialization   '''


lemmatizer = nltk.WordNetLemmatizer()
grammar = r"""
    NBAR:
        {<DT>?<CD>?<NN.*|JJ>*<NN.*>}  


    NP:
        {<NBAR>}
        {<NBAR><IN><NBAR>} 

"""
cp = nltk.RegexpParser(grammar)


'''   End partner code initialization   '''


'''   Begin partner helper functions   '''


# functions to find the NP in sentence
def leaves(tree):
    for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
        yield subtree.leaves()


def get_word_postag(word):
    if pos_tag([word])[0][1].startswith('J'):
        return wordnet.ADJ
    if pos_tag([word])[0][1].startswith('V'):
        return wordnet.VERB
    if pos_tag([word])[0][1].startswith('N'):
        return wordnet.NOUN
    else:
        return wordnet.NOUN


def normalise(word):
    postag = get_word_postag(word)
    word = lemmatizer.lemmatize(word, postag)
    return word


def get_terms(tree):
    # How could I modify this function to also return the token index or char index of the leaf?
    for leaf in leaves(tree):
        terms = [normalise(w) for w, t in leaf]
        yield terms


'''   End partner helper functions   '''


# Can I use this to make it construct and return a list instead?
def get_terms_array(tree):
    terms_array = []

    # So tree is actually what is printing just by iterating
    for term in get_terms(tree):
        terms_array.append(term)

    return terms_array


def word_frequency(sentence_list):
    frequency_data = {}

    for sentence in sentence_list:
        if len(sentence) < 1:
            pass
        else:
            for word in sentence:
                if word in list(frequency_data.keys()):
                    frequency_data[word] += 1
                else:
                    frequency_data[word] = 1

    return frequency_data


def magnitude(vector):
    mag = 0
    for entry in list(vector.keys()):
        mag += pow(vector[entry], 2)

    return math.sqrt(mag)


def create_vector_from_sentence(vocab, input_sentence):
    # Create question context vector
    sentence_vector = {}
    for sentence_word in input_sentence:
        if sentence_word in list(vocab.keys()):
            if vocab[sentence_word] in list(sentence_vector.keys()):
                sentence_vector[vocab[sentence_word]] += 1
            else:
                sentence_vector[vocab[sentence_word]] = 1
    return sentence_vector.copy()


# Where question is the sentence from the questions, and story is a list of sentences from the story text
def create_context_window(vocab, story, starting_sentence_index, sentence_context_size):

    context_vector = {}

    sentence_index = starting_sentence_index - sentence_context_size
    sentence_index = max(sentence_index, 0)

    # From bottom of context window to top
    while sentence_index <= starting_sentence_index + sentence_context_size and sentence_index < len(story):
        candidate = story[sentence_index]
        for word in candidate:
            if word in list(vocab.keys()):
                if vocab[word] in list(context_vector.keys()):
                    context_vector[vocab[word]] += 1
                else:
                    context_vector[vocab[word]] = 1

        sentence_index += 1

    return context_vector.copy()


def vector_similarity(vector1, vector2):
    used_indeces = set([])
    for index in list(vector1.keys()):
        used_indeces.add(index)
    for index in list(vector2.keys()):
        used_indeces.add(index)

    sim = 0
    for index in list(used_indeces):
        a = 0
        b = 0
        if index in list(vector1.keys()):
            a = vector1[index]
        if index in list(vector2.keys()):
            b = vector2[index]
        sim += (a * b)

    magA = magnitude(vector1)
    magB = magnitude(vector2)

    return sim / (magA * magB)


def create_vocab(question, story):
    frequency_list = story.copy()
    frequency_list.append(question)
    first_pass_frequency = word_frequency(frequency_list)

    vocab = {}

    # Create vocab dict where each word points to its index
    frequency_words = list(first_pass_frequency.keys())
    for word_index in range(len(frequency_words)):
        freq_word = frequency_words[word_index]
        # If the word has a frequency of at least 2
        if first_pass_frequency[freq_word] > 1:
            vocab[freq_word] = word_index

    return vocab.copy()


def sentence_similarity(vocab, question, story, starting_sentence_index, sentence_context_size):
    question_vector = create_vector_from_sentence(vocab, question)
    answer_vector = create_context_window(vocab, story, starting_sentence_index, sentence_context_size)
    return vector_similarity(question_vector, answer_vector)


for story_index in range(len(all_stories)):
    # Current variables
    text_lines = all_stories[story_index]
    current_qIDs = all_questions_lists[story_index][0]
    current_qTexts = all_questions_lists[story_index][1]

    # An array of tuples that each have a term and a sentence index
    located_terms = []

    for text_index in range(len(text_lines)):
        story_text_line = text_lines[text_index]
        # Make sure the list of tokens being generated for each line is valid
        tokens = nltk.word_tokenize(story_text_line)

        # Maybe reconstruct the pos_tag? Or check that the tokens are correct
        postag = nltk.pos_tag(tokens)

        tree = cp.parse(postag)
        terms = get_terms_array(tree)
        features = []

        for term in terms:
            _term = ''
            for word in term:
                _term += ' ' + word
            features.append(_term.strip())

        for feature in features:
            located_terms.append((feature, text_index))

    # For each question:
    for question_index in range(len(current_qTexts)):
        question = current_qTexts[question_index]
        ID = QIDs[question_index]

        combined_vocab = create_vocab(question, text_lines)

        # Dictionary where keys are the terms and values are the sum of all sent_sims of all occurrences of the term
        answer_chances = {}

        # For each possible answer
        for term in located_terms:
            phrase = term[0]
            sentence = text_lines[term[1]]

            if phrase not in list(answer_chances.keys()):
                answer_chances[phrase] = sentence_similarity(combined_vocab, question, text_lines, term[1], 1)
            else:
                answer_chances[phrase] = max(
                    answer_chances[phrase],
                    sentence_similarity(combined_vocab, question, text_lines, term[1], 1)
                )

        # filter the chances through the similarity of the phrase itself
        for key in list(answer_chances.keys()):
            phrase_vector = create_vector_from_sentence(combined_vocab, key)
            question_vector = create_vector_from_sentence(combined_vocab, question)
            vector_sim = vector_similarity(phrase_vector, question_vector)
            if vector_sim > 0:
                answer_chances[key] *= vector_sim

        # Get max similarity
        temp_answers = answer_chances.copy()
        max_sim = None
        max_phrase = None
        for key in list(temp_answers.keys()):
            if max_sim is None:
                max_sim = temp_answers[key]
                max_phrase = key
            elif temp_answers[key] > max_sim:
                max_sim = temp_answers[key]
                max_phrase = key

        print("QuestionID: " + ID)
        print("Answer: " + max_phrase)
        print("")
