"use client"

import { useState } from "react"
import {
  TREE_SPECIES_DB,
  calculateChaveResult,
} from "@/lib/carbon-calculations"
import type { ChaveResult, TreeSpecies } from "@/lib/types"
import {
  TreePine,
  Camera,
  Upload,
  FlaskConical,
  Scale,
  Ruler,
  Gauge,
  Loader2,
} from "lucide-react"

interface TreeIdentification {
  species: string
  scientificName: string
  confidence: number
  woodDensity: number
  avgDbh: number
  avgHeight: number
  growthRate: string
}

export function ChaveAnalysisPanel() {
  const [selectedSpecies, setSelectedSpecies] = useState<string>("neem")
  const [chaveResult, setChaveResult] = useState<ChaveResult | null>(null)
  const [identification, setIdentification] =
    useState<TreeIdentification | null>(null)
  const [isIdentifying, setIsIdentifying] = useState(false)
  const [imagePreview, setImagePreview] = useState<string | null>(null)

  const species = TREE_SPECIES_DB[selectedSpecies]

  function handleSpeciesChange(key: string) {
    setSelectedSpecies(key)
    const sp = TREE_SPECIES_DB[key]
    if (sp) {
      const result = calculateChaveResult(sp)
      setChaveResult(result)
      setIdentification(null)
      setImagePreview(null)
    }
  }

  async function handleImageUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return

    // Show preview
    const reader = new FileReader()
    reader.onload = (ev) => {
      setImagePreview(ev.target?.result as string)
    }
    reader.readAsDataURL(file)

    setIsIdentifying(true)

    try {
      const formData = new FormData()
      formData.append("image", file)

      const res = await fetch("/api/identify-tree", {
        method: "POST",
        body: formData,
      })
      const data = await res.json()

      if (data.success) {
        setIdentification(data.identification)
        setChaveResult(data.chaveAnalysis)

        // Find matching species key
        const matchKey = Object.keys(TREE_SPECIES_DB).find(
          (k) => TREE_SPECIES_DB[k].name === data.identification.species
        )
        if (matchKey) {
          setSelectedSpecies(matchKey)
        }
      }
    } catch (err) {
      console.error("Identification failed:", err)
    } finally {
      setIsIdentifying(false)
    }
  }

  // Calculate on mount for default species
  if (!chaveResult && species) {
    const result = calculateChaveResult(species)
    setChaveResult(result)
  }

  return (
    <div className="rounded-lg border border-border bg-card p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Chave Equation Analysis
        </h2>
        <FlaskConical className="h-4 w-4 text-muted-foreground" />
      </div>

      {/* ESP32-CAM Image Upload */}
      <div className="mb-4">
        <p className="text-xs text-muted-foreground mb-2">
          Upload bark image from ESP32-CAM for identification
        </p>
        <label
          className={`flex flex-col items-center justify-center rounded-md border-2 border-dashed cursor-pointer transition-colors ${
            imagePreview
              ? "border-primary/30 bg-primary/5"
              : "border-border hover:border-primary/30 hover:bg-primary/5"
          } p-4`}
        >
          {isIdentifying ? (
            <div className="flex items-center gap-2">
              <Loader2 className="h-5 w-5 text-primary animate-spin" />
              <span className="text-sm text-muted-foreground">
                Identifying tree species...
              </span>
            </div>
          ) : imagePreview ? (
            <div className="flex flex-col items-center gap-2">
              <img
                src={imagePreview}
                alt="Bark capture"
                className="h-20 w-20 rounded-md object-cover"
              />
              <span className="text-xs text-primary">
                {identification
                  ? `${identification.species} (${(identification.confidence * 100).toFixed(0)}%)`
                  : "Processing..."}
              </span>
            </div>
          ) : (
            <>
              <div className="flex items-center gap-2 mb-1">
                <Camera className="h-4 w-4 text-muted-foreground" />
                <Upload className="h-4 w-4 text-muted-foreground" />
              </div>
              <span className="text-xs text-muted-foreground">
                Capture or upload bark image
              </span>
            </>
          )}
          <input
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleImageUpload}
            className="hidden"
          />
        </label>
      </div>

      {/* Species Selector */}
      <div className="mb-4">
        <label className="text-xs text-muted-foreground mb-1.5 block">
          Tree Species
        </label>
        <select
          value={selectedSpecies}
          onChange={(e) => handleSpeciesChange(e.target.value)}
          className="w-full rounded-md border border-border bg-secondary px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
        >
          {Object.entries(TREE_SPECIES_DB).map(
            ([key, sp]: [string, TreeSpecies]) => (
              <option key={key} value={key}>
                {sp.name} ({sp.scientificName})
              </option>
            )
          )}
        </select>
      </div>

      {/* Species Properties */}
      {species && (
        <div className="grid grid-cols-2 gap-2 mb-4">
          <div className="rounded-md bg-secondary p-2.5">
            <div className="flex items-center gap-1.5">
              <Scale className="h-3 w-3 text-muted-foreground" />
              <span className="text-[10px] text-muted-foreground">
                Wood Density
              </span>
            </div>
            <p className="text-sm font-mono text-foreground mt-0.5">
              {species.woodDensity} g/cm3
            </p>
          </div>
          <div className="rounded-md bg-secondary p-2.5">
            <div className="flex items-center gap-1.5">
              <Ruler className="h-3 w-3 text-muted-foreground" />
              <span className="text-[10px] text-muted-foreground">DBH</span>
            </div>
            <p className="text-sm font-mono text-foreground mt-0.5">
              {species.avgDbh} cm
            </p>
          </div>
          <div className="rounded-md bg-secondary p-2.5">
            <div className="flex items-center gap-1.5">
              <TreePine className="h-3 w-3 text-muted-foreground" />
              <span className="text-[10px] text-muted-foreground">Height</span>
            </div>
            <p className="text-sm font-mono text-foreground mt-0.5">
              {species.avgHeight} m
            </p>
          </div>
          <div className="rounded-md bg-secondary p-2.5">
            <div className="flex items-center gap-1.5">
              <Gauge className="h-3 w-3 text-muted-foreground" />
              <span className="text-[10px] text-muted-foreground">Growth</span>
            </div>
            <p className="text-sm font-mono text-foreground mt-0.5">
              {species.growthRate}
            </p>
          </div>
        </div>
      )}

      {/* Chave Formula */}
      <div className="rounded-md bg-secondary/50 border border-border p-3 mb-4">
        <p className="text-[10px] text-muted-foreground mb-1 uppercase tracking-wider">
          Chave et al. (2014) Model
        </p>
        <p className="text-xs font-mono text-foreground">
          {'AGB = 0.0673 * (p * D\u00B2 * H)^0.976'}
        </p>
        <p className="text-[10px] text-muted-foreground mt-1">
          {'p = wood density, D = DBH, H = height'}
        </p>
      </div>

      {/* Results */}
      {chaveResult && (
        <div className="space-y-2">
          <div className="flex items-center justify-between rounded-md bg-secondary p-2.5">
            <span className="text-xs text-muted-foreground">
              Above Ground Biomass
            </span>
            <span className="text-sm font-mono text-foreground">
              {chaveResult.agb.toFixed(2)} kg
            </span>
          </div>
          <div className="flex items-center justify-between rounded-md bg-secondary p-2.5">
            <span className="text-xs text-muted-foreground">
              Carbon Stored
            </span>
            <span className="text-sm font-mono text-foreground">
              {chaveResult.carbonStored.toFixed(2)} kg
            </span>
          </div>
          <div className="flex items-center justify-between rounded-md bg-secondary p-2.5">
            <span className="text-xs text-muted-foreground">
              CO2 Sequestered
            </span>
            <span className="text-sm font-mono text-primary">
              {chaveResult.co2Sequestered.toFixed(2)} kg
            </span>
          </div>
          <div className="flex items-center justify-between rounded-md border border-primary/20 bg-primary/5 p-2.5">
            <span className="text-xs text-muted-foreground">
              Carbon Credits
            </span>
            <span className="text-sm font-semibold font-mono text-primary">
              {chaveResult.carbonCredits.toFixed(4)} tCO2e
            </span>
          </div>
          <div className="flex items-center justify-between rounded-md border border-primary/20 bg-primary/5 p-2.5">
            <span className="text-xs text-muted-foreground">Market Value</span>
            <span className="text-sm font-semibold font-mono text-foreground">
              ${chaveResult.creditValueUSD.toFixed(2)}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
