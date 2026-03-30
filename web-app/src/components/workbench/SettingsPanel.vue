<template>
  <div class="right-panel">
    <BiblePanel v-if="currentPanel === 'bible'" :key="bibleKey" :slug="slug" />
    <KnowledgePanel v-else :slug="slug" />
  </div>
</template>

<script setup lang="ts">
import BiblePanel from '../BiblePanel.vue'
import KnowledgePanel from '../KnowledgePanel.vue'

interface Props {
  slug: string
  panel?: 'bible' | 'knowledge'
  bibleKey?: number
}

// Note: While spec suggested settings/props pattern, child components (BiblePanel/KnowledgePanel)
// are fully self-contained and manage their own state internally. Using delegation pattern
// avoids unnecessary duplication and maintains clean separation of concerns.
withDefaults(defineProps<Props>(), {
  panel: 'knowledge',
  bibleKey: 0,
})
</script>

<style scoped>
.right-panel {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--aitext-panel-muted);
  border-left: 1px solid var(--aitext-split-border);
}
</style>