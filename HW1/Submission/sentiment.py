import sys

def string_is_int(test_string):
    try:
        int(test_string)
        return True
    except ValueError:
        return False


if len(sys.argv) != 4 + 1:
    raise Exception("Please provide the training, testing, and feature documents, and k")

k = int(sys.argv[len(sys.argv) - 1])

# Create dictionary of features
words = open(sys.argv[3], "r").read().split('\n')
features = {}
for i in range(k):
    features[words[i]] = i + 1;

def generate_vectors_from_filename(filename):
    vectors = []
    current_vector = []
    file = open(filename, "r").read().split('\n')
    # For every token in the training file
    for i in range(len(file)):
        token = file[i]
        # If the token is the beginning of a sentence
        if string_is_int(token) and (i == 0 or file[i - 1] == ''):
            # If there was a previous vector being built
            if len(current_vector) > 0:
                vectors.append(current_vector)
            # Create zero vector to begin adding to
            current_vector = [int(token)]
            for j in range(len(features)):
                current_vector.append(0)
        # If the token is a normal string
        else:
            if token in features:
                # Count the token
                current_vector[features[token]] = 1

    if len(current_vector) > 0:
        vectors.append(current_vector)

    filename += ".vector"
    f = open(filename, "w")
    for i in range(len(vectors)):

        vector_string = str(vectors[i][0])
        for j in range(1, len(vectors[i])):
            if vectors[i][j] > 0:
                vector_string += " " + str(j) + ":" + str(vectors[i][j])
        if len(vector_string) == 1:
            vector_string += " "
        f.write(vector_string + "\n")

generate_vectors_from_filename(sys.argv[1])
generate_vectors_from_filename(sys.argv[2])