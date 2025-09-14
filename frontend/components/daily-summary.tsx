export default function DailySummary() {
  return (
    <div className="bg-orange-200 rounded-3xl p-6">
      <h2 className="text-purple-900 text-2xl font-medium mb-4">summary</h2>

      <div className="text-purple-900 leading-relaxed">
        <p className="italic mb-4">{"<backend code makes summary so this just outputs that>"}</p>

        <div className="space-y-3">
          <p>
            Today's voice log revealed a mix of excitement and contemplation. You discussed your recent project progress
            and shared thoughts about upcoming challenges.
          </p>

          <p>
            Key themes included creativity, personal growth, and maintaining balance. Your tone suggested optimism
            despite some underlying concerns about time management.
          </p>

          <p>
            Overall sentiment: Positive with moments of introspection. Energy level: Moderate to high. Recommended
            focus: Continue current momentum while addressing time management strategies.
          </p>
        </div>
      </div>
    </div>
  )
}
