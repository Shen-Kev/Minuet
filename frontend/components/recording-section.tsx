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
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [audioUrl, setAudioUrl] = useState<string>("")
  const [transcript, setTranscript] = useState<string>("")
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [backendUrl, setBackendUrl] = useState("http://localhost:8000/transcribe")

  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    const savedUrl = localStorage.getItem("stt_url")
    if (savedUrl) {
      setBackendUrl(savedUrl)
    }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      let mimeType = "audio/mp4"
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        if (MediaRecorder.isTypeSupported("audio/webm")) {
          mimeType = "audio/webm"
        } else if (MediaRecorder.isTypeSupported("audio/ogg")) {
          mimeType = "audio/ogg"
        } else {
          mimeType = ""
        }
      }

      const mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mediaRecorder.mimeType || "audio/mp4" })
        setAudioBlob(blob)
        const url = URL.createObjectURL(blob)
        setAudioUrl(url)

        const reader = new FileReader()
        reader.onload = () => {
          const audioData = reader.result as string
          localStorage.setItem("minuet_audio_data", audioData)
        }
        reader.readAsDataURL(blob)

        // Stop all tracks to release microphone
        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
      setRecordingTime(0)
      setTranscript("")

      intervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1)
      }, 1000)
    } catch (error) {
      console.error("Error starting recording:", error)
      alert("Could not access microphone. Please check permissions.")
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop()
    }

    setIsRecording(false)
    setHasRecording(true)

    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }
  }

  const transcribeAudio = async () => {
    if (!audioBlob) return

    setIsTranscribing(true)
    try {
      const formData = new FormData()
      formData.append("audio", new File([audioBlob], "recording.webm", { type: audioBlob.type || "audio/webm" }))

      const response = await fetch(backendUrl, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const result = await response.json()
      const transcriptText = result.text?.trim() || "(no speech detected)"
      setTranscript(transcriptText)

      const entry = {
        date: new Date().toISOString().slice(0, 10),
        text: transcriptText,
        audioUrl: audioUrl,
        audioData: localStorage.getItem("minuet_audio_data"), // Include audio data for replay
        timestamp: new Date().toISOString(),
      }

      localStorage.setItem("minuet_last", JSON.stringify(entry))

      // Add to entries list
      const entries = JSON.parse(localStorage.getItem("minuet_entries") || "[]")
      entries.push(entry)
      localStorage.setItem("minuet_entries", JSON.stringify(entries))
    } catch (error) {
      console.error("Transcription failed:", error)
      setTranscript("Transcription failed. Please check your backend connection.")
    } finally {
      setIsTranscribing(false)
    }
  }

  const reRecord = () => {
    setHasRecording(false)
    setRecordingTime(0)
    setAudioBlob(null)
    setTranscript("")
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
      setAudioUrl("")
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const handleSubmit = () => {
    onSubmit()
    // Keep the recording data for replay in daily report
  }

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl)
      }
    }
  }, [audioUrl])

  return (
    <div className="border-2 border-orange-300 rounded-3xl p-6" style={{ backgroundColor: "#1a0a3a" }}>
      <h2 className="text-orange-300 text-2xl font-bold mb-6 text-center">record your entry here</h2>

      <div className="space-y-6">
        <div className="flex items-center space-x-2 text-sm">
          <label className="text-orange-200">Backend:</label>
          <input
            type="text"
            value={backendUrl}
            onChange={(e) => setBackendUrl(e.target.value)}
            className="flex-1 px-3 py-1 border border-orange-300 rounded text-orange-200 text-sm"
            style={{ backgroundColor: "#2a1a4a" }} // Darker, deeper color instead of purple-900
            placeholder="http://localhost:8000/transcribe"
          />
          <Button
            onClick={() => localStorage.setItem("stt_url", backendUrl)}
            className="bg-transparent border border-orange-300 text-orange-300 hover:bg-orange-300 hover:text-purple-900 px-3 py-1 text-sm"
          >
            Save
          </Button>
        </div>

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

        {hasRecording && audioUrl && (
          <div className="space-y-4">
            <audio ref={audioRef} controls src={audioUrl} className="w-full" style={{ filter: "hue-rotate(30deg)" }} />

            <div className="flex justify-center space-x-4">
              <Button
                onClick={transcribeAudio}
                disabled={isTranscribing}
                className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-full transition-all duration-300"
              >
                {isTranscribing ? "Transcribing..." : "Transcribe"}
              </Button>
            </div>

            {transcript && (
              <div className="border border-orange-300 rounded-lg p-4" style={{ backgroundColor: "#2a1a4a" }}>
                {" "}
                {/* Darker, deeper color */}
                <h4 className="text-orange-300 font-medium mb-2">Transcript:</h4>
                <p className="text-orange-200 whitespace-pre-wrap">{transcript}</p>
              </div>
            )}
          </div>
        )}

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
