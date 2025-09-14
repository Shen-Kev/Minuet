"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"

export default function TuneOfTheDay() {
  const [isPlaying, setIsPlaying] = useState(false)

  const togglePlayback = () => {
    setIsPlaying(!isPlaying)
  }

  return (
    <div className="border-2 border-orange-300 rounded-3xl p-6" style={{ backgroundColor: "#1a0a3a" }}>
      <div className="flex items-start justify-between mb-4">
        <h2 className="text-orange-300 text-xl font-medium">tune of the day</h2>

        <div className="flex space-x-2">
          <Button
            onClick={togglePlayback}
            className="w-12 h-12 rounded-full bg-pink-400 hover:bg-pink-500 text-purple-900 flex items-center justify-center transition-all duration-300"
          >
            {isPlaying ? "⏸" : "▶"}
          </Button>

          <Button
            onClick={() => setIsPlaying(false)}
            className="w-12 h-12 rounded-full bg-pink-400 hover:bg-pink-500 text-purple-900 flex items-center justify-center transition-all duration-300"
          >
            ⏹
          </Button>
        </div>
      </div>

      <div className="text-orange-200 leading-relaxed">
        <p className="italic mb-4">
          {"<chatbot will introduce a vibe and then give a generated song from sona- we have backend for this>"}
        </p>

        <div className="rounded-2xl p-4" style={{ backgroundColor: "#1a0a3a" }}>
          <p className="mb-3">
            Based on today's voice log, I sense a contemplative and hopeful energy. Here's a song that captures your
            current mood:
          </p>

          <div className="rounded-xl p-3" style={{ backgroundColor: "#1a0a3a" }}>
            <h3 className="font-medium text-orange-300 mb-2">"Gentle Reflections"</h3>
            <p className="text-sm">
              A soothing melody with soft piano and ambient sounds, perfect for your thoughtful state of mind today.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
