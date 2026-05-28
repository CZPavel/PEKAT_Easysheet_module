import type { DemoCamera } from '../api/types';

type Props = {
  camera: DemoCamera | null;
};

export function ContextExplorer({ camera }: Props) {
  const snapshot = camera?.last_snapshot;

  return (
    <aside className="panel context-panel">
      <h2>Context Explorer</h2>
      {!snapshot ? (
        <p className="muted">Klikni na Tick frame pro vytvo?en? demo Contextu.</p>
      ) : (
        <pre>{JSON.stringify({ context: snapshot.context, global_data: snapshot.global_data }, null, 2)}</pre>
      )}
    </aside>
  );
}
