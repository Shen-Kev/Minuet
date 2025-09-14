"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"

export default function VoiceLogReplay() {
  const [isPlaying, setIsPlaying] = useState(false)

  const togglePlayback = () => {
    setIsPlaying(!isPlaying)
  }

  return (
    <div className="border-2 border-orange-300 rounded-3xl p-6" style={{ backgroundColor: "#1a0a3a" }}>
      <div className="flex items-center justify-between">
        <h2 className="text-orange-300 text-xl font-medium">replay voice log</h2>

        <div className="flex space-x-3">
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
    </div>
  )
}
