<template>
  <div class="chart-wrapper">
    <svg :viewBox="`0 0 ${width} ${height}`" preserveAspectRatio="none">
      <defs>
        <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="var(--accent-color)" stop-opacity="0.35" />
          <stop offset="100%" stop-color="var(--accent-color)" stop-opacity="0" />
        </linearGradient>
      </defs>

      <g class="grid-lines">
        <line v-for="tick in yTicks" :key="`y-${tick}`" :x1="padding" :x2="width - padding" :y1="yForValue(tick)" :y2="yForValue(tick)" />
      </g>
      <g class="y-ticks">
        <text
          v-for="tick in yTicks"
          :key="`y-label-${tick}`"
          :x="padding - 10"
          :y="yForValue(tick)"
          text-anchor="end"
          dominant-baseline="middle"
        >
          {{ currency(tick) }}
        </text>
      </g>

      <path class="area" :d="areaPath" />
      <path class="line" :d="linePath" />

      <g class="points">
        <g v-for="p in points" :key="p.label">
          <circle :cx="p.x" :cy="p.y" r="4" @mouseenter="onEnter(p)" @mouseleave="onLeave" />
          <text :x="p.x" :y="height - padding / 2" text-anchor="middle">{{ shortLabel(p.label) }}</text>
        </g>
      </g>
    </svg>

    <div v-if="hover" class="chart-tooltip" :style="tooltipStyle">
      <div class="tooltip-date">{{ hover.label }}</div>
      <div class="tooltip-value">{{ currency(hover.revenue) }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  series: { type: Array, default: () => [] },
  width: { type: Number, default: 800 },
  height: { type: Number, default: 320 },
  padding: { type: Number, default: 48 },
});

const hover = ref(null);

const maxRevenue = computed(() => Math.max(...(props.series?.map(p => p.revenue) || [0]), 1));
const yTicks = computed(() => [0, maxRevenue.value / 2, maxRevenue.value]);
const stepX = computed(() => (props.series?.length > 1 ? (props.width - props.padding * 2) / (props.series.length - 1) : 0));

const points = computed(() => (props.series || []).map((p, idx) => ({
  x: props.padding + stepX.value * idx,
  y: props.padding + (props.height - props.padding * 2) * (1 - p.revenue / maxRevenue.value),
  label: p.date,
  revenue: p.revenue,
})));

const linePath = computed(() => {
  if (!points.value.length) return '';
  const coords = points.value.map(p => `${p.x} ${p.y}`).join(' L ');
  return `M ${coords}`;
});

const areaPath = computed(() => {
  if (!points.value.length) return '';
  const start = `M ${points.value[0].x} ${props.height - props.padding}`;
  const line = points.value.map(p => `L ${p.x} ${p.y}`).join(' ');
  const end = `L ${points.value[points.value.length - 1].x} ${props.height - props.padding} Z`;
  return `${start} ${line} ${end}`;
});

function yForValue(value) {
  if (!maxRevenue.value) return props.height - props.padding;
  return props.padding + (props.height - props.padding * 2) * (1 - value / maxRevenue.value);
}

function shortLabel(label) {
  if (!label) return '';
  const parts = label.split(' ');
  return parts.length > 1 ? parts[1] : label;
}

function currency(v) {
  if (typeof v !== 'number') return '¥0.00';
  return `¥${v.toFixed(2)}`;
}

function onEnter(p) {
  hover.value = p;
}
function onLeave() {
  hover.value = null;
}

const tooltipStyle = computed(() => {
  if (!hover.value) return {};
  const leftPct = (hover.value.x / props.width) * 100;
  const topPct = (hover.value.y / props.height) * 100;
  return { left: `${leftPct}%`, top: `${topPct}%` };
});
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  overflow: hidden;
  position: relative;
}
svg { width: 100%; height: auto; }
.line { fill: none; stroke: var(--accent-color); stroke-width: 2.5; }
.area { fill: url(#revenueGradient); stroke: none; }
.points circle { fill: var(--accent-color); stroke: var(--card-bg-color); stroke-width: 2; }
.points text { fill: var(--primary-text-color); font-size: 0.75rem; }
.grid-lines line { stroke: rgba(255,255,255,0.15); stroke-dasharray: 4 4; stroke-width: 1; }
.y-ticks text { fill: var(--primary-text-color); font-size: 0.75rem; }
.chart-tooltip {
  position: absolute; transform: translate(-50%, -120%);
  background: rgba(0, 0, 0, 0.75); color: #fff;
  padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15);
  pointer-events: none; white-space: nowrap; box-shadow: 0 8px 20px rgba(0,0,0,0.35);
}
.tooltip-date { font-size: 0.8rem; margin-bottom: 0.2rem; color: var(--secondary-text-color); }
.tooltip-value { font-size: 0.95rem; font-weight: 600; color: var(--primary-text-color); }
</style>