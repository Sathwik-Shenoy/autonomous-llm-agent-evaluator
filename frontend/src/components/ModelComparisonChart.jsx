import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

export function ModelComparisonChart({ data }) {
  return (
    <div className="panel chart-panel">
      <h3>Model Performance Comparison</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="4 4" />
          <XAxis dataKey="model" tick={{ fontSize: 11 }} interval={0} angle={-8} textAnchor="end" height={60} />
          <YAxis domain={[0, 1]} />
          <Tooltip />
          <Bar dataKey="score" fill="#ce4a2b" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
