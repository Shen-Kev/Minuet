"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"

interface RecordingSectionProps {
  onSubmit: () => void
}

export default function RecordingSection({ onSubmit }: RecordingSectionProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [hasRecording, setHasRecording] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const startRecording = () => {
    setIsRecording(true)
    setRecordingTime(0)
    intervalRef.current = setInterval(() => {
      setRecordingTime((prev) => prev + 1)
    }, 1000)
  }

  const stopRecording = () => {
    setIsRecording(false)
    setHasRecording(true)
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
  }

  const reRecord = () => {
    setHasRecording(false)
    setRecordingTime(0)
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const handleSubmit = () => {
    onSubmit()
    setHasRecording(false)
    setRecordingTime(0)
  }

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  return (
    <div className="border-2 border-orange-300 rounded-3xl p-6" style={{ backgroundColor: "#1a0a3a" }}>
      {/* Made heading bold */}
      <h2 className="text-orange-300 text-2xl font-bold mb-6 text-center">record your entry here</h2>

      <div className="space-y-6">
        {/* Recording Controls */}
        <div className="flex justify-center space-x-4">
          {!isRecording && !hasRecording && (
            <Button
              onClick={startRecording}
              className="bg-transparent border-2 border-orange-300 text-orange-300 hover:bg-orange-300 hover:text-purple-900 px-8 py-3 rounded-full text-lg transition-all duration-300"
            >
              start recording
            </Button>
          )}

          {isRecording && (
            <Button
              onClick={stopRecording}
              className="bg-red-500 hover:bg-red-600 text-white px-8 py-3 rounded-full text-lg transition-all duration-300"
            >
              stop
            </Button>
          )}
        </div>

        {/* Recording Timeline */}
        <div className="flex items-center justify-between text-orange-200">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-orange-300 rounded-full" />
            <span>{formatTime(0)}</span>
          </div>
          <div className="flex-1 mx-4 h-1 bg-gray-600 rounded-full">
            <div
              className="h-full bg-orange-300 rounded-full transition-all duration-1000"
              style={{ width: isRecording || hasRecording ? "100%" : "0%" }}
            />
          </div>
          <span>{formatTime(recordingTime)}</span>
        </div>

        {/* Submit and Re-record */}
        {hasRecording && (
          <div className="flex justify-center space-x-4">
            <Button
              onClick={handleSubmit}
              className="bg-green-500 hover:bg-green-600 text-white px-8 py-3 rounded-full text-lg transition-all duration-300"
            >
              submit
            </Button>
            <Button
              onClick={reRecord}
              className="bg-transparent border-2 border-orange-300 text-orange-300 hover:bg-orange-300 hover:text-purple-900 px-6 py-3 rounded-full text-lg transition-all duration-300"
            >
              re-record
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
