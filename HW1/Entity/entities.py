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
    prev_word_features = {}
    next_word_features = {}
    pos_features = {}
    prev_pos_features = {}
    next_pos_features = {}
    abbr_index = -1
    cap_index = -1
    unk_index = -1
    unk_pos_index = -1
    prev_unk_index = -1
    next_unk_index = -1
    prevpos_unk_index = -1
    nextpos_unk_index = -1
    phi_index = -1
    phipos_index = -1
    omega_index = -1
    omegapos_index = -1

    feature_number = 0
    vectors = []

    def __init__(self, selected):
        self.selected_ftypes = selected

    def process_all(self):
        arg_count = len(sys.argv)
        if 4 > arg_count or arg_count > 9 or sys.argv[3] != "WORD":
            raise Exception("Please provide the training and testing data, WORD, and 1-5 other ftypes")

        self.selected_ftypes = []

        # Detect which ftypes were entered as arguments
        for i in range(3, len(sys.argv)):
            ftype = sys.argv[i]
            if ftype in valid_ftypes:
                self.selected_ftypes.append(ftype)
            else:
                raise Exception("Invalid ftype")

        self.process_file(sys.argv[1], True)
        self.process_file(sys.argv[2], False)



    def process_file(self, filename, training):

        file = open(filename, "r").read().split('\n')

        readable_file = open(filename + ".readable", "w")

        self.vectors = []
        file_length = len(file)

        for line_index in range(file_length):
            line = file[line_index]
            tokens = line.split()
            if line != '' and len(tokens) > 0:
                current_vector = {}
                # Add label as item 0
                if len(tokens) > 0:
                    current_vector[0] = labels[tokens[0]]
                else:
                    print("No tokens?")


                if "WORDCON" in self.selected_ftypes:
                    # Find previous
                    prev_words = []
                    if len(self.vectors) > 0:
                        prev_index = line_index - 1
                        prev = file[prev_index]
                        if len(prev.split()) == 3:
                            prev_tokens = prev.split()
                            prev_words.append(prev_tokens[2])
                        else:
                            prev_words.append("PHI")
                    else:
                        prev_words.append("PHI")

                    # Find next
                    next_words = []
                    if line_index < len(file) - 1:
                        next_index = line_index + 1
                        next_line = file[next_index]
                        if len(next_line.split()) == 3:
                            next_tokens = next_line.split()
                            next_words.append(next_tokens[2])
                        else:
                            next_words.append("OMEGA")
                    else:
                        next_words.append("OMEGA")
                    # Strange bug where next_word is not set even though it should be
                    if len(next_words) < 1:
                        next_words.append("OMEGA")

                if "POSCON" in self.selected_ftypes:
                    # Find previous
                    prev_pos_list = []
                    if len(self.vectors) > 0:
                        prev_index = line_index - 1
                        prev = file[prev_index]
                        if len(prev.split()) == 3:
                            prev_tokens = prev.split()
                            prev_pos_list.append(prev_tokens[1])
                        else:
                            prev_pos_list.append("PHIPOS")
                    else:
                        prev_pos_list.append("PHIPOS")

                    # Find next
                    next_pos_list = []
                    if line_index < len(file) - 1:
                        next_index = line_index + 1
                        next_line = file[next_index]
                        if len(next_line.split()) == 3:
                            next_tokens = next_line.split()
                            next_pos_list.append(next_tokens[1])
                        else:
                            next_pos_list.append("OMEGAPOS")
                    else:
                        next_pos_list.append("OMEGAPOS")
                    # Strange bug where next_word is not set even though it should be
                    if len(next_pos_list) < 1:
                        next_pos_list.append("OMEGAPOS")

                # Define features
                if training:
                    # First time index setup
                    if len(self.vectors) < 1:
                        if "ABBR" in self.selected_ftypes and self.abbr_index == -1:
                            self.feature_number += 1
                            self.abbr_index = self.feature_number

                        if "CAP" in self.selected_ftypes and self.cap_index == -1:
                            self.feature_number += 1
                            self.cap_index = self.feature_number

                        if self.unk_index == -1:
                            self.feature_number += 1
                            self.unk_index = self.feature_number

                        if "POS" in self.selected_ftypes and self.unk_pos_index == -1:
                            self.feature_number += 1
                            self.unk_pos_index = self.feature_number

                        if "WORDCON" in self.selected_ftypes:
                            if self.prev_unk_index == -1:
                                self.feature_number += 1
                                self.prev_unk_index = self.feature_number

                            if self.next_unk_index == -1:
                                self.feature_number += 1
                                self.next_unk_index = self.feature_number

                            if self.phi_index == -1:
                                self.feature_number += 1
                                self.phi_index = self.feature_number

                            if self.omega_index == -1:
                                self.feature_number += 1
                                self.omega_index = self.feature_number

                        if "POSCON" in self.selected_ftypes:
                            if self.prevpos_unk_index == -1:
                                self.feature_number += 1
                                self.prevpos_unk_index = self.feature_number

                            if self.nextpos_unk_index == -1:
                                self.feature_number += 1
                                self.nextpos_unk_index = self.feature_number

                            if self.phipos_index == -1:
                                self.feature_number += 1
                                self.phipos_index = self.feature_number

                            if self.omegapos_index == -1:
                                self.feature_number += 1
                                self.omegapos_index = self.feature_number

                    # Add previously undiscovered tags to feature dictionaries
                    if "POS" in self.selected_ftypes and tokens[1] not in self.pos_features:
                        self.feature_number += 1
                        self.pos_features[tokens[1]] = self.feature_number
                    if tokens[2] not in self.word_features:
                        self.feature_number += 1
                        self.word_features[tokens[2]] = self.feature_number

                    if "WORDCON" in self.selected_ftypes:
                        if not (prev_words[0] == "UNK" or prev_words[0] == "PHI"):
                            if prev_words[0] not in self.prev_word_features:
                                self.feature_number += 1
                                self.prev_word_features[prev_words[0]] = self.feature_number
                        if not (next_words[0] == "UNK" or next_words[0] == "OMEGA"):
                            if next_words[0] not in self.next_word_features:
                                self.feature_number += 1
                                self.next_word_features[next_words[0]] = self.feature_number

                        # Make sure not to miss beginning and end
                        if prev_words[0] == "PHI":
                            if tokens[2] not in self.next_word_features:
                                self.feature_number += 1
                                self.next_word_features[tokens[2]] = self.feature_number
                        if next_words[0] == "OMEGA":
                            if tokens[2] not in self.prev_word_features:
                                self.feature_number += 1
                                self.prev_word_features[tokens[2]] = self.feature_number

                    if "POSCON" in self.selected_ftypes:
                        if not (prev_pos_list[0] == "UNKPOS" or prev_pos_list[0] == "PHIPOS"):
                            if prev_pos_list[0] not in self.prev_pos_features:
                                self.feature_number += 1
                                self.prev_pos_features[prev_pos_list[0]] = self.feature_number
                        if not (next_pos_list[0] == "UNKPOS" or next_pos_list[0] == "OMEGAPOS"):
                            if next_pos_list[0] not in self.next_pos_features:
                                self.feature_number += 1
                                self.next_pos_features[next_pos_list[0]] = self.feature_number

                        # Make sure not to miss beginning and end
                        if prev_pos_list[0] == "PHIPOS":
                            if tokens[1] not in self.next_pos_features:
                                self.feature_number += 1
                                self.next_pos_features[tokens[1]] = self.feature_number
                        if next_pos_list[0] == "OMEGA":
                            if tokens[1] not in self.prev_pos_features:
                                self.feature_number += 1
                                self.prev_pos_features[tokens[1]] = self.feature_number

                # Begin writing readable output
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

                # Set correct word feature
                if tokens[2] not in self.word_features:
                    current_vector[self.unk_index] = 1
                    ftype_values["WORD"] = "UNK"
                else:
                    current_vector[self.word_features[tokens[2]]] = 1

                # Set correct POS feature
                if "POS" in self.selected_ftypes:
                    if tokens[1] in self.pos_features:
                        current_vector[self.pos_features[tokens[1]]] = 1
                    else:
                        current_vector[self.unk_pos_index] = 1
                        ftype_values["POS"] = "UNKPOS"

                # Determine if token is an abbreviation
                if "ABBR" in self.selected_ftypes:
                    if abbreviation(tokens[2]):
                        current_vector[self.abbr_index] = 1
                    else:
                        current_vector[self.abbr_index] = 0

                # Determine if token is capitalized
                if "CAP" in self.selected_ftypes:
                    if (tokens[2][0] == tokens[2].upper()[0]) and (tokens[2][0] != tokens[2][0].lower()):
                        current_vector[self.cap_index] = 1
                    else:
                        current_vector[self.cap_index] = 0

                # Set values for WORDCON
                if "WORDCON" in self.selected_ftypes:
                    if prev_words[0] == "PHI":
                        current_vector[self.phi_index] = 1
                    elif prev_words[0] not in self.prev_word_features:
                        prev_words[0] = "UNK"
                        current_vector[self.prev_unk_index] = 1
                    else:
                        current_vector[self.prev_word_features[prev_words[0]]] = 1

                    if next_words[0] == "OMEGA":
                        current_vector[self.omega_index] = 1
                    elif next_words[0] not in self.next_word_features:
                        next_words[0] = "UNK"
                        current_vector[self.next_unk_index] = 1
                    else:
                        current_vector[self.next_word_features[next_words[0]]] = 1

                # Set values for POSCON
                if "POSCON" in self.selected_ftypes:
                    if prev_pos_list[0] == "PHIPOS":
                        current_vector[self.phipos_index] = 1
                    elif prev_pos_list[0] not in self.prev_pos_features:
                        prev_pos_list[0] = "UNKPOS"
                        current_vector[self.prevpos_unk_index] = 1
                    else:
                        current_vector[self.prev_pos_features[prev_pos_list[0]]] = 1

                    if next_pos_list[0] == "OMEGAPOS":
                        current_vector[self.omegapos_index] = 1
                    elif next_pos_list[0] not in self.next_pos_features:
                        next_pos_list[0] = "UNKPOS"
                        current_vector[self.nextpos_unk_index] = 1
                    else:
                        current_vector[self.next_pos_features[next_pos_list[0]]] = 1

                self.vectors.append(current_vector)

                if "POS" in self.selected_ftypes:
                    ftype_values["POS"] = tokens[1]
                if "ABBR" in self.selected_ftypes:
                    ftype_values["ABBR"] = "yes" if current_vector[self.abbr_index] > 0 else "no"
                if "CAP" in self.selected_ftypes:
                    ftype_values["CAP"] = "yes" if current_vector[self.cap_index] > 0 else "no"
                if "WORDCON" in self.selected_ftypes:
                    ftype_values["WORDCON"] = prev_words[0] + " " + next_words[0]
                if "POSCON" in self.selected_ftypes:
                    ftype_values["POSCON"] = prev_pos_list[0] + " " + next_pos_list[0]

                for i in range(len(list(ftype_values))):
                    ftype = list(ftype_values.keys())[i]
                    readable_file.write(ftype + ": " + str(ftype_values[ftype]))
                    if i < len(list(ftype_values)) - 1:
                        readable_file.write("\n")

        # Write vector files
        file
        f = open(filename + ".vector", "w")
        for i in range(len(self.vectors)):
            vector_string = str(self.vectors[i][0])
            key_list = sorted(list(self.vectors[i].keys()))
            ascending = True
            last_val = -1
            for j in range(1, len(key_list)):
                feature_index = key_list[j]
                if self.vectors[i][feature_index] > 0:
                    vector_string += " " + str(feature_index) + ":" + str(self.vectors[i][feature_index])
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