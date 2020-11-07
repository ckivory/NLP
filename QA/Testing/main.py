import sys
import re
import nltk
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet


#Read the input file and generate the path for each question and story file.
input_file = sys.argv[1]
story_file = []
question_file = []
with open(input_file, "r") as f:
    for line in f.readlines():
        story_file.append(line.strip('\n'))
        question_file.append("")
for i in range(1, len(story_file)):
    question_file[i] = story_file[0] + "/" + story_file[i] + ".questions"
    story_file[i] = story_file[0] + "/" + story_file[i] + ".story"
story_file = story_file[1:]
question_file = question_file[1:]


#set the grammar rule
lemmatizer = nltk.WordNetLemmatizer()
grammar = r"""
    NBAR:
        {<DT>?<CD>?<NN.*|JJ>*<NN.*>}  
        

    NP:
        {<NBAR>}
        {<NBAR><IN><NBAR>} 

"""
cp = nltk.RegexpParser(grammar)


# functions to find the NP in sentence
def leaves(tree):
    for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
        print(subtree.leaves())
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
    for leaf in leaves(tree):
        terms = [normalise(w) for w, t in leaf]
        yield terms


# Give the path list of story file, generate a list for each story, each element in a list is the NP in one sentence.
for i in range(len(story_file)):
    with open(story_file[i], "r") as f:
        pre_process = []
        after_process = []
        for line in f.readlines():
            pre_process.append(line)
        start_idx = pre_process.index("TEXT:\n") + 2
        sentences = [""]
        sentence_idx = 0
        for j in range(start_idx, len(pre_process)):
            if pre_process[j] != "\n":
                sentences[sentence_idx] = (sentences[sentence_idx] + pre_process[j]).replace('\n', " ")
            else:
                sentences.append("")
                sentence_idx += 1
        for s in sentences:
            tokens = [nltk.word_tokenize(t) for t in [s]]
            postag = [nltk.pos_tag(p) for p in tokens][0]
            tree = cp.parse(postag)
            terms = get_terms(tree)
            features = []
            for term in terms:
                _term = ''
                for word in term:
                    _term += ' ' + word
                features.append(_term.strip())
            after_process.append(features)










