import random

_MAX_SENTENCES = 8

# Define the word groups
G1 = ['eat', 'orange', 'moon','shine', 'brightly', 'paint', 'picture']
G2 = ['feed', 'ducks', 'cloud', 'cover', 'sun', 'climb', 'stairs']
G3 = ['wash', 'car', 'train', 'travel', 'fast', 'sew', 'dress']
G4 = ['make', 'kite', 'bear', 'catch', 'rabbit', 'water', 'garden']

# Define word types
nouns_G1 = {'orange', 'moon', 'picture'}
verbs_G1 = {'eat','shine', 'paint'}
adjectives_G1 = {'brightly'}  # No adjectives identified in G1

nouns_G2 = {'ducks', 'cloud', 'sun', 'stairs'}
verbs_G2 = {'feed', 'cover', 'climb'}
adjectives_G2 = set()  # No adjectives identified in G2

nouns_G3 = {'car', 'train', 'dress'}
verbs_G3 = {'wash', 'travel', 'sew'}
adjectives_G3 = {'fast'}

nouns_G4 = {'kite', 'bear', 'rabbit', 'garden'}
verbs_G4 = {'make', 'catch', 'water'}
adjectives_G4 = set()  # No adjectives identified in G4

# Combine them into respective dictionaries for easier access
nouns = nouns_G1.union(nouns_G2).union(nouns_G3).union(nouns_G4)
verbs = verbs_G1.union(verbs_G2).union(verbs_G3).union(verbs_G4)
adjectives = adjectives_G1.union(adjectives_G2).union(adjectives_G3).union(adjectives_G4)

# Group dictionary for easy access
groups = [G1, G2, G3, G4]

# Initialize an empty list to store the sentences
sentences = []
group_usage = {'G1': 0, 'G2': 0, 'G3': 0, 'G4': 0}  # To track group usage

# Target usage per group
target_usage = len(groups) * 3 * (len(groups[0]) // (len(groups) * 3))


# Function to check if a sentence is grammatically correct
def is_grammatically_correct(words):
    # Assume simple SVO structure: [noun] [verb] [noun/adjective]
    if len(words) == 3:
        return words[0] in nouns and words[1] in verbs and (words[2] in nouns or words[2] in adjectives)
    return False


# Function to create a sentence from words in different groups
def create_sentence():
    while True:
        # Find groups with the least usage to balance the sentence construction
        min_usage_groups = [k for k, v in group_usage.items() if v < target_usage]

        if len(min_usage_groups) >= 3:
            selected_groups = random.sample([int(k[-1]) - 1 for k in min_usage_groups], 3)
        else:
            selected_groups = random.sample(range(len(groups)), 3)

        words = [random.choice(groups[idx]) for idx in selected_groups]

        # Ensure the words are from different groups
        if len(set(selected_groups)) == len(words):
            # Check if the sentence is grammatically correct
            if is_grammatically_correct(words):
                # Prepare group labels
                group_labels = set(f"G{idx + 1}" for idx in selected_groups)

                # Update the group usage count
                for label in group_labels:
                    group_usage[label] += 1

                # Remove used words from the respective groups
                for idx, word in zip(selected_groups, words):
                    groups[idx].remove(word)

                # Construct a simple sentence with additional words
                sentence = "The " + " ".join(words) + "."
                # Add group labels
                sentence += " [" + ", ".join(sorted(group_labels)) + "]"
                return sentence.capitalize()


# Generate mix sentences
while len(sentences) < _MAX_SENTENCES:
    sentence = create_sentence()
    print(f'Generated: {sentence}')
    sentences.append(sentence)

# Display the sentences
for i, sentence in enumerate(sentences):
    print(f"{i + 1}. {sentence}")

# Display the group usage counts
print("\nGroup usage counts:")
for group, count in group_usage.items():
    print(f"{group}: {count}")
