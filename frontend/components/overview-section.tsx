"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

const mockData = [
  { day: "Mon", mood: 7 },
  { day: "Tue", mood: 5 },
  { day: "Wed", mood: 8 },
  { day: "Thu", mood: 6 },
  { day: "Fri", mood: 9 },
  { day: "Sat", mood: 7 },
  { day: "Sun", mood: 8 },
]

const chartConfig = {
  mood: {
    label: "Mood Score",
    color: "#fed7aa",
  },
}

export default function OverviewSection() {
  return (
    <div className="border-2 border-orange-300 rounded-3xl p-6" style={{ backgroundColor: "#1a0a3a" }}>
      <h2 className="text-orange-300 text-2xl font-bold mb-6 text-center">overview</h2>

      <div className="h-64 text-orange-200">
        <ChartContainer config={chartConfig}>
          <LineChart data={mockData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#fed7aa" opacity={0.2} />
            <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "#fed7aa", fontSize: 12 }} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: "#fed7aa", fontSize: 12 }} domain={[0, 10]} />
            <ChartTooltip
              content={<ChartTooltipContent />}
              cursor={{ stroke: "#fed7aa", strokeWidth: 1, strokeDasharray: "5 5" }}
            />
            <Line
              type="monotone"
              dataKey="mood"
              stroke="#fed7aa"
              strokeWidth={3}
              dot={{ fill: "#fed7aa", strokeWidth: 2, r: 6 }}
              activeDot={{ r: 8, fill: "#fb923c", stroke: "#fed7aa", strokeWidth: 2 }}
            />
          </LineChart>
        </ChartContainer>
      </div>

      <p className="text-orange-200 text-center mt-4 italic">
        {"<be able to insert a graph here based on data from backend>"}
      </p>
    </div>
  )
}
