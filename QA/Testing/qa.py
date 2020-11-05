import nltk
import sys

if len(sys.argv) != 4:
    raise Exception("Please provide story, questions, and answers files")

story_filename = sys.argv[1]
questions_filename = sys.argv[2]
answers_filename = sys.argv[3]

split_story = story_filename.split('.')
split_questions = questions_filename.split('.')
split_answers = answers_filename.split('.')

if len(split_story) != 2 or split_story[1] != "story":
    raise Exception("Story filename must end with .story")
if len(split_questions) != 2 or split_questions[1] != "questions":
    raise Exception("Questions filename must end with .questions")
if len(split_answers) != 2 or split_answers[1] != "answers":
    raise Exception("Answers filename must end with .answers")

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
        QIDs.append(line[12:])
    elif tag == "Question":
        QTexts.append(line[10:])
    elif tag == "Difficulty":
        QDiffs.append(line[12:])

# Split story into headline, date, ID, and text
headline = story_lines[0][10:]
date = story_lines[1][6:]
storyID = story_lines[2][9:]

story_text_lines = []
for line_index in range(4, len(story_lines)):
    story_text_lines.append(story_lines[line_index])


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
    return mag


# Where question is the sentence from the questions, and story is a list of sentences from the story text
def vector_similarity(question, story, starting_sentence_index, sentence_context_size):

    frequency_list = story.copy()
    frequency_list.append(question)

    first_pass_frequency = word_frequency(frequency_list)
    vocab = {}

    # Create vocab dict where each word points to its index
    frequency_words = list(first_pass_frequency.keys())
    for word_index in range(len(frequency_words)):
        word = frequency_words[word_index]
        # If the word has a frequency of at least 2
        if first_pass_frequency[word] > 1:
            vocab[word] = word_index

    # Create question context vector
    print("Question: " + question)
    question_vector = {}
    for word in question:
        if word in list(vocab.keys()):
            if vocab[word] in list(question_vector.keys()):
                question_vector[vocab[word]] += 1
            else:
                question_vector[vocab[word]] = 1

    answer_vector = {}
    sentence_index = starting_sentence_index - sentence_context_size
    sentence_index = max(sentence_index, 0)

    # From bottom of context window to top
    print("Story lines in context:")
    while sentence_index <= starting_sentence_index + sentence_context_size and sentence_index < len(story):
        candidate = story[sentence_index]
        print(candidate)
        for word in candidate:
            if word in list(vocab.keys()):
                if vocab[word] in list(answer_vector.keys()):
                    answer_vector[vocab[word]] += 1
                else:
                    answer_vector[vocab[word]] = 1

        sentence_index += 1

    used_indeces = set([])
    for index in list(question_vector.keys()):
        used_indeces.add(index)
    for index in list(answer_vector.keys()):
        used_indeces.add(index)

    sim = 0
    for index in list(used_indeces):
        a = 0
        b = 0
        if index in list(question_vector.keys()):
            a = question_vector[index]
        if index in list(answer_vector.keys()):
            b = answer_vector[index]
        sim += (a * b)

    magA = magnitude(question_vector)
    magB = magnitude(answer_vector)

    return sim / (magA * magB)


print(vector_similarity(QTexts[4], story_text_lines, 5, 1))


# TODO: Create a function that can return the cosine similarity of the question and each potential answer
#   1. Create vocabulary based on words from story (and questions and answers?). Frequency of two or higher.
#   2. Create context vector of question and phrase in story, probably given a start and end index of the phrase.
#   3. Create dictionary indexed by vocab_index of each word, pointing to frequency in context window.
#   4. Return dot-product similarity.

# TODO: (Partner) Create an algorithm that returns every phrase of a given type from a list of sentences given a grammar
# TODO: Create a grammar that can identify potential answers to different 'wh' questions    Together tomorrow
