<template>
  <div v-if="imageSources.length" class="image-display">
    <img
        v-for="(image, index) in imageSources"
        :key="index"
        :src="image.src"
        :alt="alt"
        :class="`image-${index+1}`"
        @error="handleImageError"
        :style="{ opacity: image.opacity }"
    />
  </div>
</template>

<script>
import {ref, onMounted, watch} from 'vue';

export default {
  name: 'ImageDisplay',
  props: {
    src: {
      type: String,
      required: true
    },
    alt: {
      type: String,
      default: 'Vocabulary image'
    }
  },
  setup(props) {
    const imageSources = ref([]);

    const loadImage = () => {
      if (!props.src) return;

      const images = props.src.split('|').filter(src => src.trim() !== '');
      const opacities = [1, 0.4, 0.2];
      imageSources.value = images.map((image, index) => ({
        src: image,
        opacity: opacities[images.length - index - 1]
      }));
      console.log('Loaded image sources:', imageSources.value.map(image => image.src));
    };

    onMounted(loadImage);
    watch(() => props.src, loadImage);

    const handleImageError = (e) => {
      console.error(`Error loading image: ${e.target.src}`);
      e.target.src = '';
      return {};
    };

    return {
      imageSources,
      handleImageError
    };
  }
}
</script>

<!--height: 500px;-->
<style scoped>
.image-display {
  position: relative;
  width: 500px;
  height: 500px;
  margin: 20px auto;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  background-color: black;
  color: #ffffff;
}

.image-display img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}
</style>

