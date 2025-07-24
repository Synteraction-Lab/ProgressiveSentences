# Progressive Sentences

Learning secondary langauge (L2) sentences and their meaning (e.g., English, L1) using a progressive presentation technique.

## Publications
- [Progressive Sentences: Combining the Benefits of Word and Sentence Learning](https://www.doi.org/10.1145/3737821.3749564), MobileHCI '25 Adjunct
  - Camera Ready [PDF](paper/MobileHCI2025_ProgressiveSentences.pdf)
```
@inproceedings{janaka_progressive_2025,
    author = {Janaka, Nuwan and Zhao, Shengdong and Ram, Ashwin and Sun, Ruoxin and Tan Jing Wen, Sherisse and Li, Danae and Hsu, David},
    title = {{Progressive} {Sentences}: {Combining} the {Benefits} of {Word} and {Sentence} {Learning},
    year = {2025},
    month = sep,
    doi = {10.1145/3737821.3749564},
    booktitle = {Adjunct Proceedings of the 27th International Conference on Mobile Human-Computer Interaction},
    series = {MobileHCI '25 Adjunct},
}
```

## Contact person
- [Nuwan Janaka](https://synteraction.org/our-team) ([In](https://www.linkedin.com/in/nuwan-janaka/))


## Project links
- (private) Project folder: [here](https://drive.google.com/drive/u/1/folders/1hGbxMdgC_lC73Gn7y6Qu99wa9ipbBwOw)
- Documentation: [here](guide_link)
- [Version info](VERSION.md)


## Requirements

- Make sure Python3 (>=3.10) is installed (
  e.g., [Miniconda](https://docs.conda.io/en/latest/miniconda.html) )
- Make sure [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
  and [node](https://nodejs.org/en) is installed
    - Tested with Node.js v20.* (LTS)

## Installation

- Install required libraries
    - [wuggy](https://pypi.org/project/wuggy/) using `pip install wuggy`
    - [pandas](https://pandas.pydata.org/) using `pip install pandas`
    - [OpenAI TTS](https://platform.openai.com/docs/guides/text-to-speech)
      using `pip install openai`
    - [fastapi](https://github.com/tiangolo/fastapi) using `pip install fastapi uvicorn`
    - [pygit2](https://pypi.org/project/pygit2/) using `pip install pygit2`
- [Optional] Install following for text-to-speech
    - [OpenAI TTS](https://platform.openai.com/docs/guides/text-to-speech) using `pip install openai`
    - [GoogleCloud TextToSpeech](https://cloud.google.com/python/docs/reference/texttospeech/latest)
      using `pip install google-cloud-texttospeech`
- [Optional] Install following for the analysis
    - [scipy](https://pypi.org/project/scipy) using `pip install scipy`
    - [statsmodels](https://pypi.org/project/statsmodels) using `pip install statsmodels`
    - [pingouin](https://pypi.org/project/pingouin) using `pip install pingouin`
    - [seaborn](https://pypi.org/project/seaborn) using `pip install seaborn`
    - [matplotlib](https://pypi.org/project/matplotlib) using `pip install matplotlib`
- [Optional] Create the required credential files inside `credential` folder (if you want to use OpenAI/GoogleCloud
  audio generation)
    - Create a file `credential/openai_credential.json` with OpenAI credentials such
      as `{"openai_api_key": "KEY"}`
    - Create a file `credential/google_cloud_credentials.json` with Google Service Account credentials

- Install the libraries for the [frontend](frontend)
    - `cd frontend`
    - `npm install`
    - `npm run format`

## Application Execution

- Running the sentence learning
    - Run by `python main.py`
        - Then open the hosted url (e.g., [http://localhost:5173/](http://localhost:5173/)) in a
          browser

- Generating L2 words
    - Run the L2 word generation via `python generate_words.py` after adding `text/L1-words.csv`
        - Results will be in `output/L1-L2-words.csv`
        - If there are issues with `numpy` downgrade it using `pip install numpy==1.*`

- Generating L2 sentences
    - Run the L2 sentence generation via `python generate_sentences.py` after
      adding `text/L1-sentences.csv` and `text/L1-L2-mapping.csv`
        - Results will be in `output/L1-L2-sentences.csv`

- Generating audio (for L2/L1 words/sentences)
    - Run the L2 audio generation via `python generate_audio.py` after adding `text/L2-sentences.csv`
        - Results will be in `output/audio/` directory

- Analyze results
    - Run the marking via `python mark_answers.py` after adding `user_data/participants_answers.csv`
        - If the script can not detect the correct one, you need to add marks by inputting correct values by commas
        - Results will be in `output/participants_answers_marks.csv` or `output/participants_marks_summary.csv`
    - To analyze marks run `python analyze_marks.py` (assuming marks are at `output/participants_marks_summary.csv`)
    - To analyze ratings, use `python analyze_ratings.py` after adding `user_data/participants_ratings.csv`
    - To convert the long format data to wide format (e.g., JASP), use `python convert_csv_to_anova_wide.py`


- Generate L1 sentences from groups
    - Update the `generate_mix_sentences.py` with correct groups, and the nouns/verbs/adjectives based on groups
    - Generate the sentences using `python generate_mix_sentences.py`
    - To verify the generated sentences have mix of groups,
        - Copy the sentences to `text/L1-sentences.csv`
        - Generate L2 sentences using `python generate_sentences.py`
        - Copy the generate L2 sentences to `text/L2-sentences.csv`
        - Run `python analyze_sentences.py` to get the results

- Verify all multimedia files (images, audios) are available
    - Run the analysis via `python analyze_multimedia_files.py` which verifies all the mentioned multimedia files
      in `backend/data/Sentence_elements.csv` are available

## References

- [Vue.js](https://vuejs.org/guide/quick-start)
- [OpenAI Text to speech](https://platform.openai.com/docs/guides/text-to-speech)
