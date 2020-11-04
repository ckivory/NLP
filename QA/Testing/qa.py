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

story_lines = story_file.readlines()

for line in story_lines:
    text = nltk.word_tokenize(line)
    tagged_text = nltk.pos_tag(text)
    for entry in tagged_text:
        print("Word: " + entry[0] + "\t\tTag: " + entry[1])


# TODO: Create a function that can return the dot product similarity of the question and each potential answer
#   1. Create vocabulary based on words from story (and questions and answers?). Frequency of two or higher.
#   2. Create context vector of question and phrase in story, probably given a start and end index of the phrase.
#   3. Create dictionary indexed by vocab_index of each word, pointing to frequency in context window.
#   4. Return dot-product similarity.

# TODO: (Partner) Create an algorithm that returns every phrase of a given type from a list of sentences given a grammar
# TODO: Create a grammar that can identify potential answers to different 'wh' questions    Together tomorrow
