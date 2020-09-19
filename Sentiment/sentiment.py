import sys

def string_is_int(test_string):
    try:
        int(test_string)
        return True
    except ValueError:
        return False


if len(sys.argv) != 4 + 1:
    raise Exception("Please provide the training, testing, and feature documents, and k")

input_files = []

for i in range(1, len(sys.argv) - 1):
    f = open(sys.argv[i], "r")
    input_files.append(f.read().split())

k = int(sys.argv[len(sys.argv) - 1])

# Create dictionary of features
features = {}
for i in range(k):
    features[input_files[2][i]] = i;

training_vectors = []
current_vector = []

# For every token in the training file
for i in range(len(input_files[0])):
    token = input_files[0][i]
    # If the token is the beginning of a sentence
    if string_is_int(token):
        # If there was a previous vector being built
        if len(current_vector) > 0:
            training_vectors.append(current_vector)
        # Create zero vector to begin adding to
        current_vector = [int(token)]
        for j in range(len(features)):
            current_vector.append(0)
    # If the token is a normal string
    else:
        if token in features:
            # Count the token
            current_vector[features[token] + 1] = 1

if len(current_vector) > 0:
    training_vectors.append(current_vector)

filename = sys.argv[1] + ".vector"
f = open(filename, "w")
for i in range(len(training_vectors)):

    if i == 0:
        sentence = "Sentence: "
        j = i + 1
        while not string_is_int(input_files[0][j]):
            sentence += " " + input_files[0][j]
            j += 1
        print(sentence)
        print("Label: " + str(training_vectors[i][0]))

    vector_string = str(training_vectors[i][0])
    for j in range(1, len(training_vectors[i])):
        if training_vectors[i][j] > 0:

            if i == 0:
                print("Feature: " + list(features.keys())[j] + " Exists: " + str(training_vectors[i][j]))

            vector_string += " " + str(j) + ":" + str(training_vectors[i][j])
    if len(vector_string) == 1:
        vector_string += " "
    f.write(vector_string + "\n")
