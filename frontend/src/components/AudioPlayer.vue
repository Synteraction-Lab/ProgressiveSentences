<template>
  <div class="audio-player">
  </div>
</template>


<script>
export default {
  name: 'AudioPlayer',
  props: {
    src: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: 'Play'
    }
  },
  data() {
    return {
      isPlaying: false,
      audio: null
    }
  },
  watch: {
    src: {
      immediate: true,
      handler(newSrc) {
        this.loadAudio(newSrc);
      }
    }
  },
  methods: {
    loadAudio(src) {
      if (this.audio) {
        this.audio.pause();
        this.audio.removeEventListener('ended', this.audioEnded);
      }

      if (src) {
        // Assume the audio file is in the public folder
        const audioSrc = `${src}`;
        this.audio = new Audio(audioSrc);
        this.audio.addEventListener('ended', this.audioEnded);
        this.audio.addEventListener('canplaythrough', this.attemptPlay);
        this.audio.load();
      } else {
        this.audio = null;
      }
    },
    attemptPlay() {
      this.audio.play().catch(error => {
        console.error('Error playing audio:', error);
      });
    },
    togglePlay() {
      if (this.isPlaying) {
        this.audio.pause();
      } else {
        this.audio.play().catch(error => {
          console.error('Error playing audio:', error);
        });
      }
      this.isPlaying = !this.isPlaying;
    },
    audioEnded() {
      this.isPlaying = false;
    }
  },
  beforeUnmount() {
    if (this.audio) {
      this.audio.pause();
      this.audio.removeEventListener('ended', this.audioEnded);
    }
  },
  mounted() {
    this.loadAudio(this.src);
  }
}
</script>

