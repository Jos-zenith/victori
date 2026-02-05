<script setup lang="ts">
import { computed } from 'vue'
import type { TreeSpecies, ChaveResult } from '../types'

const props = defineProps<{
  species: TreeSpecies
  chaveResult: ChaveResult
}>()

const biomassFormatted = computed(() => props.chaveResult.agb.toLocaleString())
const co2Formatted = computed(() => props.chaveResult.co2Sequestered.toLocaleString())
</script>

<template>
  <div class="chave-panel">
    <div class="chave-header">
      <div class="chave-title-row">
        <h3>Chave Equation Analysis</h3>
        <span class="chave-badge">Chave et al. 2014</span>
      </div>
      <p class="chave-subtitle">Pantropical allometric model for above-ground biomass estimation</p>
    </div>

    <!-- Formula Display -->
    <div class="formula-box">
      <div class="formula-label">Model Formula</div>
      <div class="formula-text">
        AGB = 0.0673 &times; (&rho; &times; D&sup2; &times; H)<sup>0.976</sup>
      </div>
    </div>

    <!-- Species Info -->
    <div class="species-info">
      <div class="species-name">
        <strong>{{ species.name }}</strong>
        <em>({{ species.scientificName }})</em>
      </div>
    </div>

    <!-- Parameters Grid -->
    <div class="param-grid">
      <div class="param-item">
        <span class="param-symbol">&rho;</span>
        <span class="param-label">Wood Density</span>
        <span class="param-value">{{ species.woodDensity }} g/cm&sup3;</span>
      </div>
      <div class="param-item">
        <span class="param-symbol">D</span>
        <span class="param-label">DBH</span>
        <span class="param-value">{{ species.avgDbh }} cm</span>
      </div>
      <div class="param-item">
        <span class="param-symbol">H</span>
        <span class="param-label">Height</span>
        <span class="param-value">{{ species.avgHeight }} m</span>
      </div>
      <div class="param-item">
        <span class="param-symbol">C<sub>f</sub></span>
        <span class="param-label">Carbon Fraction</span>
        <span class="param-value">{{ species.carbonFraction }}</span>
      </div>
    </div>

    <!-- Results Chain -->
    <div class="results-chain">
      <div class="chain-step">
        <div class="chain-label">Above-Ground Biomass</div>
        <div class="chain-value">{{ biomassFormatted }} kg</div>
      </div>
      <div class="chain-arrow">&darr;</div>
      <div class="chain-step">
        <div class="chain-label">Carbon Stored (AGB &times; C<sub>f</sub>)</div>
        <div class="chain-value">{{ chaveResult.carbonStored.toLocaleString() }} kg</div>
      </div>
      <div class="chain-arrow">&darr;</div>
      <div class="chain-step">
        <div class="chain-label">CO&sub2; Sequestered (&times; 44/12)</div>
        <div class="chain-value highlight">{{ co2Formatted }} kg</div>
      </div>
      <div class="chain-arrow">&darr;</div>
      <div class="chain-step final">
        <div class="chain-label">Carbon Credits (1 credit = 1 tonne)</div>
        <div class="chain-value credits">{{ chaveResult.carbonCredits.toFixed(4) }} credits</div>
        <div class="chain-usd">&asymp; ${{ chaveResult.creditValueUSD.toFixed(2) }} USD</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chave-panel {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #e8eef7;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.chave-header {
  margin-bottom: 20px;
}

.chave-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.chave-title-row h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
}

.chave-badge {
  font-size: 0.6rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 10px;
  background: #0284c714;
  color: #0284c7;
  letter-spacing: 0.3px;
}

.chave-subtitle {
  font-size: 0.8rem;
  color: #94a3b8;
}

.formula-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 16px;
  text-align: center;
}

.formula-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.formula-text {
  font-size: 1.05rem;
  font-weight: 600;
  color: #1e293b;
  font-family: 'Georgia', serif;
}

.formula-text sup {
  font-size: 0.7rem;
}

.species-info {
  margin-bottom: 16px;
  padding: 10px 14px;
  background: #f0fdf4;
  border-radius: 8px;
  border-left: 3px solid #16a34a;
}

.species-name strong {
  font-size: 0.95rem;
  color: #1e293b;
  margin-right: 6px;
}

.species-name em {
  font-size: 0.8rem;
  color: #64748b;
}

.param-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.param-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 10px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #f1f5f9;
}

.param-symbol {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0284c7;
  font-family: 'Georgia', serif;
  margin-bottom: 2px;
}

.param-label {
  font-size: 0.65rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 4px;
}

.param-value {
  font-size: 0.85rem;
  font-weight: 700;
  color: #1e293b;
}

.results-chain {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.chain-step {
  width: 100%;
  text-align: center;
  padding: 10px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.chain-step.final {
  background: #f0fdf4;
  border-color: #16a34a33;
}

.chain-label {
  font-size: 0.7rem;
  color: #64748b;
  margin-bottom: 4px;
}

.chain-value {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
}

.chain-value.highlight {
  color: #0284c7;
}

.chain-value.credits {
  color: #16a34a;
  font-size: 1.15rem;
}

.chain-usd {
  font-size: 0.8rem;
  color: #16a34a;
  font-weight: 600;
  margin-top: 2px;
}

.chain-arrow {
  font-size: 1.2rem;
  color: #cbd5e1;
  line-height: 1;
}
</style>
