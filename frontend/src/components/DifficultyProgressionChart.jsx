import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

export function DifficultyProgressionChart({ data }) {
  return (
    <div className="panel chart-panel">
      <h3>Scenario Difficulty Progression</h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="difficultyFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#124559" stopOpacity={0.8} />
              <stop offset="100%" stopColor="#124559" stopOpacity={0.2} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="index" />
          <YAxis domain={[0, 1]} />
          <Tooltip />
          <Area type="monotone" dataKey="difficulty" stroke="#124559" fill="url(#difficultyFill)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
