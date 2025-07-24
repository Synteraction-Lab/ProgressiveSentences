<template>
  <div class="vocabulary-card">
    <div class="content-wrapper">
      <div v-if="loading" class="status"></div>
      <!-- <div v-if="loading" class="status">Loading...</div> -->
      <div v-else-if="error" class="status">Error: {{ error }}</div>
      <div v-else>
        <h2 v-html="curWord.foreignText" class="foreign-text"></h2>
        <AudioPlayer
            v-show="curWord.foreignPronunciation"
            :src="curWord.foreignPronunciation"
            class="audio-player"
        />
        <h3 v-html="curWord.englishTranslation" class="english-text"></h3>
        <AudioPlayer
            v-show="curWord.englishPronunciation"
            :src="curWord.englishPronunciation"
            class="audio-player"
        />
        <ImageDisplay
            v-show="curWord.imageUrl"
            :src="curWord.imageUrl"
            :alt="curWord.foreignText"
            class="image-display"
        />
      </div>
      <div v-if="showContinueBtn">
        <button id="continueBtn" @click="toggleBtn">Continue</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ImageDisplay from './ImageDisplay.vue';
import AudioPlayer from './AudioPlayer.vue';

const TRIGGER_WORDS = ["Session starts", "Session ends",
  "S1", "S2", "S3", "S4", "S5",
  "Style: S1", "Style: S2", "Style: S3", "Style: S4", "Style: S5",
  "W1", "W2", "W3", "W4", "W5",
  "Style: W1", "Style: W2", "Style: W3", "Style: W4", "Style: W5"];

const API_ENDPOINT_SENTENCE = "http://localhost:8000/api/next-sentence/";

const API_ENDPOINT_LOG = 'http://localhost:8000/api/log';

export default {
  name: 'VocabularyCard',
  components: {ImageDisplay, AudioPlayer},
  props: {
    participant_id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      curWord: {},
      sentence: [],
      sentenceCount: 0,
      currentIdx: -1,
      showTranslation: false,
      loading: true,
      error: null,
      showContinueBtn: false,
    };
  },
  methods: {
    async fetchSentence() {
      this.loading = true;
      this.error = null;
      this.showTranslation = false;

      try {
        const url = API_ENDPOINT_SENTENCE + this.participant_id;
        const response = await axios.get(url);

        let log_message = "Successfully fetched next sentence " + this.sentenceCount;
        axios.post(API_ENDPOINT_LOG, {
          message: log_message,
          timestamp: new Date().toISOString()
        });

        this.sentence = response.data.subWords || [];
        this.currentIdx = -1;
        this.nextWord();
      } catch (error) {
        const error_msg = "Error fetching sentence " + this.sentenceCount + ": " + error;
        axios.post(API_ENDPOINT_LOG, {
          message: error_msg,
          timestamp: new Date().toISOString()
        });
        this.error = 'Failed to fetch sentence. Please try again.';
      } finally {
        this.loading = false;
      }
    },

    nextWord() {
      let log_message = "Attempting to fetch next word with id " + (this.currentIdx + 1) + " in sentence " + this.sentenceCount;
      axios.post(API_ENDPOINT_LOG, {
        message: log_message,
        timestamp: new Date().toISOString()
      });

      if (this.currentIdx < this.sentence.length - 1) {
        this.currentIdx += 1;
        this.curWord = this.sentence[this.currentIdx];
        this.showTranslation = false;

        if (this.shouldShowContinueBtn()) {
          this.showContinueBtn = true;
          return;
        }

        const nextWordDuration = this.curWord.displayDuration;

        setTimeout(() => {
          this.nextWord();
        }, nextWordDuration);
      } else {
        let log_message = "Finished current sentence " + this.sentenceCount + "; Fetching next sentence";
        axios.post(API_ENDPOINT_LOG, {
          message: log_message,
          timestamp: new Date().toISOString()
        });

        this.sentenceCount += 1;
        this.fetchSentence();
      }
    },

    toggleBtn() {
      this.showContinueBtn = false;
      this.fetchSentence();
    },

    shouldShowContinueBtn() {
      // Define the trigger words that should display the start button
      return TRIGGER_WORDS.includes(this.curWord.foreignText);
    }
  },
  mounted() {
    this.fetchSentence();
  },
};
</script>

<style scoped>
.vocabulary-card {
  display: absolute;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  padding: 20px;
  box-sizing: border-box;
  background-color: black;
  color: #ffffff;
  min-height: 400px; /* Adjust as needed */
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.status {
  font-size: 2rem;
}

.foreign-text {
  font-size: 4rem;
  margin-bottom: 10px;
  position: absolute;
  top: 10%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.english-text {
  font-size: 3rem;
  margin-bottom: 10px;
  position: absolute;
  top: 20%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.image-display {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.translation, .image-display {
  /* Ensure consistent space is reserved for these elements */
  min-height: 100px; /* Adjust as needed based on component size */
}

#continueBtn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 10px 20px;
  font-size: 1.5rem;
}
</style>

