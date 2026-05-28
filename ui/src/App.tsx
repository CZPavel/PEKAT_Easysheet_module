import { useEffect, useMemo, useState } from 'react';
import { api } from './api/client';
import type { DemoState } from './api/types';
import { CameraCards } from './components/CameraCards';
import { ContextExplorer } from './components/ContextExplorer';
import { Controls } from './components/Controls';
import { DetailPanel } from './components/DetailPanel';
import { DiagnosticsPanel } from './components/DiagnosticsPanel';
import { SpreadsheetPanel } from './components/SpreadsheetPanel';
import { StatusBar } from './components/StatusBar';
import './styles/app.css';

export function App() {
  const [state, setState] = useState<DemoState | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>('Camera_1');
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const selectedCamera = useMemo(() => {
    return state?.cameras.find((camera) => camera.project_id === selectedId) ?? state?.cameras[0] ?? null;
  }, [selectedId, state]);

  async function loadState() {
    try {
      setApiError(null);
      const nextState = await api.getDemoState();
      setState(nextState);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : 'Nezn?m? API chyba');
    }
  }

  async function runAction(action: () => Promise<DemoState>) {
    setLoading(true);
    try {
      setApiError(null);
      const nextState = await action();
      setState(nextState);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : 'Nezn?m? API chyba');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadState();
  }, []);

  return (
    <div className="app-shell">
      <StatusBar state={state} apiError={apiError} />
      <Controls
        loading={loading}
        onStart={() => runAction(api.tickDemo)}
        onTick={() => runAction(api.tickDemo)}
        onReset={() => runAction(api.resetDemo)}
      />
      <CameraCards
        cameras={state?.cameras ?? []}
        selectedId={selectedCamera?.project_id ?? null}
        onSelect={setSelectedId}
      />
      <div className="workspace-grid">
        <ContextExplorer camera={selectedCamera} />
        <SpreadsheetPanel camera={selectedCamera} />
        <DetailPanel camera={selectedCamera} />
      </div>
      <DiagnosticsPanel camera={selectedCamera} apiError={apiError} />
    </div>
  );
}
