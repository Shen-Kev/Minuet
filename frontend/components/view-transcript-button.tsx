"use client"

import { Button } from "@/components/ui/button"

interface ViewTranscriptButtonProps {
  onClick: () => void
}

export default function ViewTranscriptButton({ onClick }: ViewTranscriptButtonProps) {
  return (
    <Button
      onClick={onClick}
      className="w-full bg-orange-200 hover:bg-orange-300 text-purple-900 py-4 rounded-3xl text-xl font-medium transition-all duration-300"
    >
      view transcript
    </Button>
  )
}
