import sys

# Helper function to identify abbreviations
def abbreviation(test_string):
    abbr = (test_string[-1] == '.')
    letters = 0
    for i in range(len(test_string)):
        is_letter = (test_string[i].lower() != test_string[i].upper())
        if is_letter:
            letters += 1
        abbr &= (is_letter or test_string[i] == '.')
    abbr &= (len(test_string) <= 4)
    abbr &= letters > 0

    return abbr

valid_ftypes = ["WORD", "POS", "ABBR", "CAP", "WORDCON", "POSCON"]
labels = {
    "O": 0,
    "B-PER": 1,
    "I-PER": 2,
    "B-LOC": 3,
    "I-LOC": 4,
    "B-ORG": 5,
    "I-ORG": 6
}

class FileProcessor:


    selected_ftypes = []

    word_features = {}
    pos_features = {}
    abbr_index = -1
    cap_index = -1
    unk_index = -1

    feature_number = 0
    vectors = []

    def __init__(self, selected):
        self.selected_ftypes = selected

    def process_all(self):
        arg_count = len(sys.argv)
        if 4 > arg_count or arg_count > 9 or sys.argv[3] != "WORD":
            raise Exception("Please provide the training and testing data, WORD, and 1-5 other ftypes")

        selected_ftypes = []

        # Detect which ftypes were entered as arguments
        for i in range(3, len(sys.argv)):
            ftype = sys.argv[i]
            if ftype in valid_ftypes:
                selected_ftypes.append(ftype)
            else:
                raise Exception("Invalid ftype")

        self.process_file(sys.argv[1], True)
        self.process_file(sys.argv[2], False)



    def process_file(self, filename, training):
        file = open(filename, "r").read().split('\n')

        readable_file = open(filename + ".readable", "w")


        self.vectors = []
        for line in file:
            tokens = line.split()
            if(line != '' and len(tokens) > 0):
                current_vector = []
                # Add label as item 0
                if len(tokens) > 0:
                    current_vector.append(labels[tokens[0]])
                else:
                    print("No tokens?")

                if training:
                    # Add previously undiscovered tags to feature dictionaries
                    if not tokens[1] in self.pos_features:
                        self.feature_number += 1
                        self.pos_features[tokens[1]] = self.feature_number
                    if not tokens[2] in self.word_features:
                        self.feature_number += 1
                        self.word_features[tokens[2]] = self.feature_number

                    # Create abbr index if necessary
                    if self.abbr_index == -1:
                        self.feature_number += 1
                        self.abbr_index = self.feature_number

                    # Create cap index if necessary
                    if self.cap_index == -1:
                        self.feature_number += 1
                        self.cap_index = self.feature_number

                    if self.unk_index == -1:
                        self.feature_number += 1
                        self.unk_index = self.feature_number


                # Enforce vector length
                while len(current_vector) <= self.feature_number:
                    current_vector.append(0)

                # Add to output file
                if len(self.vectors) > 0:
                    readable_file.write("\n\n")

                ftype_values = {
                    "WORD": tokens[2],
                    "POS": "n/a",
                    "ABBR": "n/a",
                    "CAP": "n/a",
                    "WORDCON": "n/a",
                    "POSCON": "n/a"
                }

                # Set correct POS feature
                current_vector[self.pos_features[tokens[1]]] = 1

                # Set correct word feature
                if not tokens[2] in self.word_features:
                    current_vector[self.unk_index] = 1
                    ftype_values["WORD"] = "UNK"
                else:
                    current_vector[self.word_features[tokens[2]]] = 1


                # Determine if token is an abbreviation
                if abbreviation(tokens[2]):
                    current_vector[self.abbr_index] = 1
                else:
                    current_vector[self.abbr_index] = 0

                # Determine if token is capitalized
                if (tokens[2][0] == tokens[2].upper()[0]) and (tokens[2][0] != tokens[2][0].lower()):
                    current_vector[self.cap_index] = 1
                else:
                    current_vector[self.cap_index] = 0

                self.vectors.append(current_vector)

                if "POS" in self.selected_ftypes:
                    ftype_values["POS"] = tokens[1]
                # TODO: Replace with calculation of ABBR
                if "ABBR" in self.selected_ftypes:
                    ftype_values["ABBR"] = "yes" if current_vector[self.abbr_index] > 0 else "no"
                # TODO: Replace with calculation of CAP
                if "CAP" in self.selected_ftypes:
                    ftype_values["CAP"] = "yes" if current_vector[self.cap_index] > 0 else "no"
                # Not required to implement
                '''
                if "WORDCON" in selected_ftypes:
                    ftype_values["ABBR"] = 0
                if "POSCON" in selected_ftypes:
                    ftype_values["ABBR"] = 0
                '''

                for i in range(len(list(ftype_values))):
                    ftype = list(ftype_values.keys())[i]
                    readable_file.write(ftype + ": " + str(ftype_values[ftype]))
                    if i < len(list(ftype_values)) - 1:
                        readable_file.write("\n")

        file
        f = open(filename + ".vector", "w")
        for i in range(len(self.vectors)):

            vector_string = str(self.vectors[i][0])
            for j in range(1, len(self.vectors[i])):
                if self.vectors[i][j] > 0:
                    vector_string += " " + str(j) + ":" + str(self.vectors[i][j])
            if len(vector_string) == 1:
                vector_string += " "
            f.write(vector_string + "\n")

def main():
    arg_count = len(sys.argv)
    if 4 > arg_count or arg_count > 9 or sys.argv[3] != "WORD":
        raise Exception("Please provide the training and testing data, WORD, and 1-5 other ftypes")

    input_ftypes = []

    # Detect which ftypes were entered as arguments
    for i in range(3, len(sys.argv)):
        ftype = sys.argv[i]
        if ftype in valid_ftypes:
            input_ftypes.append(ftype)
        else:
            raise Exception("Invalid ftype")

    fp = FileProcessor(input_ftypes)
    fp.process_all()


if __name__ == "__main__":
    main()