export function FailureLogTable({ rows }) {
  return (
    <div className="panel">
      <h3>Failure Case Logs</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Agent</th>
              <th>Category</th>
              <th>Reason</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan="4">No failures in current window.</td>
              </tr>
            ) : (
              rows.map((r, idx) => (
                <tr key={`${r.agent}-${idx}`}>
                  <td>{r.agent}</td>
                  <td>{r.category}</td>
                  <td>{r.reason}</td>
                  <td>{Math.round(r.score * 100)}%</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
