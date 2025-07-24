from pydantic import BaseModel
from typing import List

class LogMessage(BaseModel):
    message: str
    timestamp: str


# Define the data model
class Word(BaseModel):
    id: int
    foreignText: str
    englishTranslation: str
    foreignPronunciation: str
    englishPronunciation: str
    displayDuration: int
    imageUrl: str


class Sentence(BaseModel):
    id: int
    subWords: List[Word]


class Participant(BaseModel):
    participantId: str
    currentSentenceIndex: int
    sentences:  List[Sentence]
