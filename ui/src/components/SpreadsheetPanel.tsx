import type { DemoCamera } from '../api/types';

type Props = {
  camera: DemoCamera | null;
};

export function SpreadsheetPanel({ camera }: Props) {
  const spreadsheet = camera?.last_evaluation?.context_updates.spreadsheet;
  const rows = [
    ['A1', 'project_id', spreadsheet?.project_id ?? '-'],
    ['A2', 'frame_id', spreadsheet?.frame_id ?? '-'],
    ['A3', 'master_result', String(spreadsheet?.outputs.master_result ?? '-')],
    ['A4', 'allow_branch_default', String(spreadsheet?.outputs.allow_branch_default ?? '-')],
    ['A5', 'reason', spreadsheet?.reason ?? '-'],
    ['A6', 'mode', spreadsheet?.mode ?? '-'],
  ];

  return (
    <main className="panel spreadsheet-panel">
      <div className="panel-title-row">
        <h2>Workbook / Coordinator sheet</h2>
        <span className="muted">MVP mock spreadsheet</span>
      </div>
      <table className="sheet-table">
        <thead>
          <tr><th>Cell</th><th>Name</th><th>Value</th></tr>
        </thead>
        <tbody>
          {rows.map(([cell, name, value]) => (
            <tr key={cell}>
              <td className="cell-id">{cell}</td>
              <td>{name}</td>
              <td>{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
