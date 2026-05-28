import type { DemoCamera } from '../api/types';

type Props = {
  cameras: DemoCamera[];
  selectedId: string | null;
  onSelect: (projectId: string) => void;
};

export function CameraCards({ cameras, selectedId, onSelect }: Props) {
  return (
    <section className="camera-grid">
      {cameras.map((camera) => {
        const spreadsheet = camera.last_evaluation?.context_updates.spreadsheet;
        const ok = spreadsheet?.outputs.master_result ?? null;
        return (
          <button
            key={camera.project_id}
            className={`camera-card ${selectedId === camera.project_id ? 'selected' : ''}`}
            onClick={() => onSelect(camera.project_id)}
          >
            <span className="camera-title">{camera.name}</span>
            <span className={`result ${ok === false ? 'ng' : 'ok'}`}>{ok === false ? 'NG' : 'OK'}</span>
            <span className="muted">{camera.last_snapshot?.frame_id ?? 'bez frame'}</span>
          </button>
        );
      })}
    </section>
  );
}
