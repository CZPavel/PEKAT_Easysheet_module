import type { DemoCamera } from '../api/types';

type Props = {
  camera: DemoCamera | null;
  apiError: string | null;
};

export function DiagnosticsPanel({ camera, apiError }: Props) {
  return (
    <footer className="panel diagnostics-panel">
      <strong>Diagnostics</strong>
      {apiError ? <span className="danger-text">{apiError}</span> : <span>Backend online</span>}
      <span>Selected: {camera?.project_id ?? 'none'}</span>
      <span>Last update: {camera?.last_evaluation?.context_updates.spreadsheet?.last_update_ts ?? '-'}</span>
    </footer>
  );
}
