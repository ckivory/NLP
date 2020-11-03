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


# TODO: Create a grammar that can identify potential answers to different 'wh' questions
# TODO: Create an algorithm that ranks story sentences by their similarity to the question
# TODO: Create a way to determine the most likely answer by selecting a phrase that is compatible with the grammar from
#   the sentences that are most similar to the question. Figure out how to use training data to determine best phrase
