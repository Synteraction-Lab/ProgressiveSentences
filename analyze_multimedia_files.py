from utilities.file_utility import get_files_with_extension, compare_files
from backend.sentence_utility import get_all_sentences_content, clean_audio

_DIRECTORY_IMAGES = "frontend/public/images"
_DIRECTORY_L2_AUDIO = "frontend/public/audios/l2"
_DIRECTORY_L1_AUDIO = "frontend/public/audios/l1"

_all_sentences = get_all_sentences_content()

l2_texts = []
l1_texts = []
images = []

# Iterate over the dictionary returned by get_all_sentences_content
for _sentence_id, (_id, _sentence_l2, _sentence_l1, _sentence_image, _sentence_parts) in _all_sentences.items():
    # Add the main L2 sentence
    if _sentence_l2:
        l2_texts.append(_sentence_l2)

    if _sentence_l1:
        l1_texts.append(_sentence_l1)

    if _sentence_image:
        images.append(_sentence_image)

    # Add the L2 text from each part
    for part in _sentence_parts.values():
        for subpart in part.values():
            if subpart['L2']:
                l2_texts.append(subpart['L2'])
            if subpart['L1']:
                l1_texts.append(subpart['L1'])
            if subpart['Image']:
                images.append(subpart['Image'])

all_l2_audio_files = get_files_with_extension(_DIRECTORY_L2_AUDIO, ".mp3")
all_l1_audio_files = get_files_with_extension(_DIRECTORY_L1_AUDIO, ".mp3")
all_image_files = get_files_with_extension(_DIRECTORY_IMAGES, ".png")

l2_texts = [clean_audio(l2_text) for l2_text in l2_texts]
extra_l2, missing_l2 = compare_files([filename.replace(".mp3", "") for filename in all_l2_audio_files], l2_texts)
print("Missing L2: ", missing_l2)

l1_texts = [clean_audio(l1_text) for l1_text in l1_texts]
extra_l1, missing_l1 = compare_files([filename.replace(".mp3", "") for filename in all_l1_audio_files], l1_texts)
print("Missing L1: ", missing_l1)

extra_img, missing_img = compare_files([filename.replace(".png", "") for filename in all_image_files], images)
print("Missing Image: ", missing_img)
