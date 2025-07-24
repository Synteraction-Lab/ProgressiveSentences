<template>
    <div id="app">
    <div v-if="!showVocabularyCard">
      <div>
        <label for="participantId">Enter Participant ID:</label>
        <input 
          type="text" 
          id="participantId" 
          v-model="participantId" 
          placeholder="Enter ID"
          @keyup.enter="toggleStart"
        />
      </div>
    
      <button id="startBtn" @click="toggleStart">Start</button>
    </div>

    <div v-if="showVocabularyCard">
      <VocabularyCard :participant_id="participantId" />
    </div>
  </div>
</template>


<script>
import VocabularyCard from './components/VocabularyCard.vue'

export default {
  name: 'App',
  components: {
    VocabularyCard
  },
  data() {
    return {
      showVocabularyCard: false,
      participantId: ''
    }
  },
  methods: {
    toggleStart() {
      if (this.participantId) {
        this.showVocabularyCard = !this.showVocabularyCard;
      } else {
        alert('Please enter a participant ID.');
      }
    }
  }
}


</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  background-color: black;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: white;
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: black;
}

label {
  display: block;
  margin-bottom: 5px;
}

input[type="text"] {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 10px;
}
</style>