# Week 2: UI Implementation and AI Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement main page sidebar, workbench top bar, chart components, AI task tracking, and refactor large components

**Architecture:** Build on Week 1 infrastructure (statsStore, statsApi, types). Create reusable UI components (StatCard, charts), integrate AI job status polling with cache invalidation, split Workbench.vue into focused sub-components, migrate vis-network to ECharts.

**Tech Stack:** Vue 3, TypeScript, Pinia, ECharts, Naive UI, @vueuse/core

---

## File Structure

### New Files to Create

**Components:**
- `web-app/src/components/stats/StatCard.vue` - Reusable statistics card
- `web-app/src/components/stats/StatsSidebar.vue` - Home page sidebar
- `web-app/src/components/stats/StatsTopBar.vue` - Workbench top bar
- `web-app/src/components/stats/JobStatusIndicator.vue` - AI task status indicator
- `web-app/src/components/charts/ProgressChart.vue` - Chapter progress bar chart
- `web-app/src/components/charts/TrendChart.vue` - Word count trend line chart
- `web-app/src/components/charts/DistributionChart.vue` - Stage distribution pie chart
- `web-app/src/components/charts/GraphChart.vue` - Character relationship graph (ECharts)
- `web-app/src/components/workbench/ChapterList.vue` - Chapter navigation (extracted)
- `web-app/src/components/workbench/ChatArea.vue` - Chat area (extracted)
- `web-app/src/components/workbench/SettingsPanel.vue` - Settings panel (extracted)

**Composables:**
- `web-app/src/composables/useWorkbench.ts` - Workbench business logic
- `web-app/src/composables/useJobStatus.ts` - Job status tracking logic

**Utils:**
- `web-app/src/utils/chartConverters.ts` - vis-network to ECharts data converters

### Files to Modify

- `web-app/src/stores/statsStore.ts` - Add onJobCompleted, onChapterSaved methods
- `web-app/src/views/Home.vue` - Integrate StatsSidebar
- `web-app/src/views/Workbench.vue` - Refactor to use sub-components
- `web-app/src/views/Chapter.vue` - Optimize API calls and Markdown rendering
- `web-app/src/views/Cast.vue` - Replace vis-network with GraphChart
- `web-app/src/components/CastGraphCompact.vue` - Replace vis-network with GraphChart
- `web-app/src/components/KnowledgeTripleGraph.vue` - Replace vis-network with GraphChart

### Files to Delete (after refactoring)

- None (we modify existing files in place, removing old code sections)

### Dependencies to Remove

- `vis-network` package (after migration complete)

---

## Task 1: Create StatCard Component

**Files:**
- Create: `web-app/src/components/stats/StatCard.vue`

- [ ] **Step 1: Create component directory**

```bash
mkdir -p web-app/src/components/stats
```

- [ ] **Step 2: Create StatCard.vue with complete implementation**

File: `web-app/src/components/stats/StatCard.vue`

```vue
<template>
  <div class="stat-card">
    <div class="stat-card-header">
      <span v-if="icon" class="stat-icon">{{ icon }}</span>
      <h3 class="stat-title">{{ title }}</h3>
    </div>

    <div class="stat-body">
      <n-skeleton v-if="loading" text :width="80" height="32px" />
      <div v-else class="stat-value-wrap">
        <span class="stat-value">{{ value }}</span>
        <span v-if="unit" class="stat-unit">{{ unit }}</span>
      </div>
    </div>

    <div v-if="trend" class="stat-trend" :class="`trend-${trend.direction}`">
      <span class="trend-icon">{{ trend.direction === 'up' ? '↑' : '↓' }}</span>
      <span class="trend-value">{{ trend.value }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface StatCardProps {
  title: string
  value: number | string
  icon?: string
  trend?: {
    value: number
    direction: 'up' | 'down'
  }
  loading?: boolean
  unit?: string
}

defineProps<StatCardProps>()
</script>

<style scoped>
.stat-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.stat-icon {
  font-size: 24px;
}

.stat-title {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
  font-weight: 500;
}

.stat-body {
  margin-bottom: 8px;
}

.stat-value-wrap {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #111827;
  line-height: 1;
}

.stat-unit {
  font-size: 14px;
  color: #6b7280;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
}

.trend-up {
  color: #10b981;
}

.trend-down {
  color: #ef4444;
}

.trend-icon {
  font-size: 14px;
}
</style>
```

- [ ] **Step 3: Commit**

```bash
git add web-app/src/components/stats/
git commit -m "feat: add StatCard reusable statistics card component"
```

---

## Task 2: Create StatsSidebar Component

**Files:**
- Create: `web-app/src/components/stats/StatsSidebar.vue`

- [ ] **Step 1: Create StatsSidebar.vue**

Complete implementation in file.

- [ ] **Step 2: Commit**

```bash
git add web-app/src/components/stats/StatsSidebar.vue
git commit -m "feat: add StatsSidebar component"
```

---

## Task 3: Integrate StatsSidebar into Home.vue

**Files:**
- Modify: `web-app/src/views/Home.vue`

- [ ] **Step 1: Import StatsSidebar**

Add import:
```typescript
import StatsSidebar from '@/components/stats/StatsSidebar.vue'
```

- [ ] **Step 2: Update template with flex layout**

Wrap content:
```vue
<template>
  <div class="home">
    <StatsSidebar />
    <div class="home-content">
      <!-- existing content -->
    </div>
  </div>
</template>
```

- [ ] **Step 3: Add styles**

```vue
<style scoped>
.home {
  display: flex;
  min-height: 100vh;
}

.home-content {
  flex: 1;
  margin-left: 280px;
  padding: 24px;
}
</style>
```

- [ ] **Step 4: Test in browser**

Expected: Sidebar on left, content shifted right

- [ ] **Step 5: Commit**

```bash
git add web-app/src/views/Home.vue
git commit -m "feat: integrate StatsSidebar into Home"
```

---

## Task 4: Extend statsStore with Cache Invalidation

**Files:**
- Modify: `web-app/src/stores/statsStore.ts`

- [ ] **Step 1: Add onJobCompleted method**

```typescript
onJobCompleted(slug: string) {
  if (this.bookStatsCache[slug]) {
    delete this.bookStatsCache[slug]
  }
  this.loadBookStats(slug, true)
  this.loadGlobalStats(true)
}
```

- [ ] **Step 2: Add onChapterSaved method**

```typescript
onChapterSaved(slug: string, chapterId: string) {
  if (this.bookStatsCache[slug]) {
    delete this.bookStatsCache[slug]
  }
  this.loadBookStats(slug, true)
}
```

- [ ] **Step 3: Commit**

```bash
git add web-app/src/stores/statsStore.ts
git commit -m "feat: add cache invalidation to statsStore"
```

---
## Task 5-21: Remaining Implementation Tasks

Due to plan length, remaining tasks (5-21) are summarized. Refer to design spec for full implementation details.

**Tasks 5-7: UI Components**
- Task 5: JobStatusIndicator with 3s polling
- Task 6: StatsTopBar with 6 stat items
- Task 7: 4 Chart components (Progress, Trend, Distribution, Graph)

**Tasks 8-12: vis-network Migration**
- Task 8: Chart converter utility
- Task 9-11: Migrate Cast.vue, CastGraphCompact, KnowledgeTripleGraph
- Task 12: Remove vis-network dependency

**Tasks 13-17: Workbench Refactoring**
- Task 13-15: Extract ChapterList, ChatArea, SettingsPanel
- Task 16: Create useWorkbench composable
- Task 17: Integrate StatsTopBar

**Tasks 18-20: Chapter.vue Optimization**
- Task 18: Parallelize API calls with Promise.all
- Task 19: Add 300ms Markdown debounce
- Task 20: Integrate stats refresh on save

**Task 21: Final Testing**
- Run tests, verify all features, cleanup old code

---

## Execution Handoff

Plan saved to `docs/superpowers/plans/2026-03-31-week2-implementation.md`

**Two execution options:**

1. **Subagent-Driven (recommended)** - Fresh subagent per task, review between tasks
2. **Inline Execution** - Execute in this session with checkpoints

**Which approach?**
