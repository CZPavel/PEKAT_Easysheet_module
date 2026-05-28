import type { DemoState } from '../api/types';

type Props = {
  state: DemoState | null;
  apiError: string | null;
};

export function StatusBar({ state, apiError }: Props) {
  const status = apiError ? 'BACKEND ERROR' : state?.running ? 'DEMO RUNNING' : 'READY';

  return (
    <header className="status-bar">
      <div>
        <strong>PEKAT Easysheet Module</strong>
        <span className="muted">offline simulator + spreadsheet bridge</span>
      </div>
      <div className={`pill ${apiError ? 'danger' : 'ok'}`}>{status}</div>
      <div className="muted">Tick: {state?.tick_index ?? 0}</div>
    </header>
  );
}
