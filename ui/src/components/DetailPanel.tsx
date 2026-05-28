import type { DemoCamera } from '../api/types';

type Props = {
  camera: DemoCamera | null;
};

export function DetailPanel({ camera }: Props) {
  const spreadsheet = camera?.last_evaluation?.context_updates.spreadsheet;

  return (
    <aside className="panel detail-panel">
      <h2>Detail</h2>
      <dl>
        <dt>Projekt</dt><dd>{camera?.project_id ?? '-'}</dd>
        <dt>Frame</dt><dd>{camera?.last_snapshot?.frame_id ?? '-'}</dd>
        <dt>V?sledek</dt><dd>{spreadsheet?.result === false ? 'NG' : 'OK'}</dd>
        <dt>Reason</dt><dd>{spreadsheet?.reason ?? '-'}</dd>
      </dl>
      <h3>Live outputs</h3>
      <pre>{JSON.stringify(spreadsheet?.outputs ?? {}, null, 2)}</pre>
    </aside>
  );
}
