from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import Word, Sentence, Participant, LogMessage
import logging
from backend.sentence_utility import get_all_participants_sentences

logger = logging.getLogger()
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

all_participants = get_all_participants_sentences()


@app.post("/api/log")
async def log_to_file(message: LogMessage):
    logger.info(message)


@app.get("/api/next-sentence/{participant_id}")
async def next_sentence(participant_id: str):
    global all_participants

    try:
        participant = all_participants.get(participant_id)

        all_sentences = participant.sentences
        sentence_index = participant.currentSentenceIndex + 1

        if sentence_index >= len(all_sentences):
            sentence_index = 0

        vars(participant).update({'currentSentenceIndex': sentence_index})

        sentence = all_sentences[sentence_index]

        logger.info(
            f"Returning sentence:: participant:{participant_id}, sentence index:{sentence_index}, word_count:{len(sentence.subWords)}")

        return sentence
    except AttributeError as e:
        logging.error("Unable to find participant_id: " + str(participant_id))
        raise HTTPException(status_code=404, detail="Participant ID not found")


if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(
        filename='backend.log',
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )

    uvicorn.run(app, host="0.0.0.0", port=8000)
