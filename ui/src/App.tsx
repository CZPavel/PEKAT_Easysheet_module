import { useEffect, useMemo, useState } from 'react';
import { api } from './api/client';
import type { Cell, ContextTree, DemoState, Sheet, Workbook, WorkbookEvaluateResponse } from './api/types';
import './styles/app.css';

const COLUMNS = Array.from({ length: 26 }, (_, index) => String.fromCharCode(65 + index));

function ensureCell(sheet: Sheet, address: string): Cell {
  return sheet.cells[address] ?? { address, raw: '', value: null, status: 'ok', error: null };
}

function flattenContext(projectId: string, value: unknown, prefix: string): Array<{ path: string; value: unknown }> {
  if (value === null || typeof value !== 'object') return [{ path: `${projectId}.${prefix}`, value }];
  if (Array.isArray(value)) return value.flatMap((item, index) => flattenContext(projectId, item, `${prefix}.${index}`));
  return Object.entries(value as Record<string, unknown>).flatMap(([key, item]) => flattenContext(projectId, item, `${prefix}.${key}`));
}

export function App() {
  const [workbook, setWorkbook] = useState<Workbook | null>(null);
  const [demoState, setDemoState] = useState<DemoState | null>(null);
  const [contextTree, setContextTree] = useState<ContextTree | null>(null);
  const [evaluation, setEvaluation] = useState<WorkbookEvaluateResponse | null>(null);
  const [activeSheet, setActiveSheet] = useState('Camera_1');
  const [activeProject, setActiveProject] = useState('Camera_1');
  const [selectedCell, setSelectedCell] = useState('B2');
  const [formulaDraft, setFormulaDraft] = useState('');
  const [apiError, setApiError] = useState<string | null>(null);

  const sheet = useMemo(() => workbook?.sheets.find((item) => item.name === activeSheet) ?? null, [activeSheet, workbook]);
  const selected = sheet ? ensureCell(sheet, selectedCell) : null;
  const contextItems = useMemo(() => {
    if (!contextTree) return [];
    return [
      ...flattenContext(contextTree.project_id, contextTree.tree.context, 'context'),
      ...flattenContext(contextTree.project_id, contextTree.tree.global_data, 'global_data'),
    ];
  }, [contextTree]);

  async function loadAll() {
    try {
      setApiError(null);
      const [nextWorkbook, nextDemo] = await Promise.all([api.getWorkbook(), api.getDemoState()]);
      setWorkbook(nextWorkbook);
      setDemoState(nextDemo);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : 'Nezn?m? chyba');
    }
  }

  async function loadContext(projectId: string) {
    try {
      setActiveProject(projectId);
      setContextTree(await api.getContextTree(projectId));
    } catch (error) {
      setContextTree(null);
      setApiError(error instanceof Error ? `${error.message} ? klikni Tick frame.` : 'Context zat?m nen? dostupn?');
    }
  }

  async function tickAndEvaluate() {
    try {
      setApiError(null);
      const nextDemo = await api.tickDemo();
      setDemoState(nextDemo);
      const contexts = Object.fromEntries(
        nextDemo.cameras
          .filter((camera) => camera.last_snapshot)
          .map((camera) => [camera.project_id, { context: camera.last_snapshot?.context, global_data: camera.last_snapshot?.global_data }]),
      );
      const result = await api.evaluateWorkbook(contexts);
      setWorkbook(result.workbook);
      setEvaluation(result);
      await loadContext(activeProject);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : 'Nezn?m? chyba');
    }
  }

  async function saveCellRaw(raw: string) {
    if (!workbook || !sheet) return;
    const nextWorkbook: Workbook = {
      ...workbook,
      sheets: workbook.sheets.map((item) => item.name === sheet.name
        ? { ...item, cells: { ...item.cells, [selectedCell]: { ...ensureCell(item, selectedCell), raw } } }
        : item),
    };
    setWorkbook(nextWorkbook);
    setFormulaDraft(raw);
    setWorkbook(await api.saveWorkbook(nextWorkbook));
  }

  async function bindPathToCell(sourcePath: string, cellAddress = selectedCell) {
    const updated = await api.addBinding({ sheet_name: activeSheet, cell: cellAddress, source_path: sourcePath });
    setWorkbook(updated);
    if (cellAddress === selectedCell) setFormulaDraft(`=PV("${sourcePath}")`);
  }

  useEffect(() => { void loadAll(); }, []);
  useEffect(() => { if (selected) setFormulaDraft(String(selected.raw ?? '')); }, [selectedCell, activeSheet, workbook]);

  return (
    <div className="app-shell light">
      <header className="topbar">
        <div><strong>PEKAT Easysheet</strong><span>Spreadsheet mapping workspace nad PEKAT Context JSON</span></div>
        <div className="toolbar-actions">
          <button onClick={() => void tickAndEvaluate()}>Tick frame + evaluate</button>
          <button className="secondary" onClick={() => void api.resetDemo().then(setDemoState)}>Reset demo</button>
        </div>
      </header>
      <section className="workbook-tabs">
        {workbook?.sheets.map((item) => <button key={item.name} className={item.name === activeSheet ? 'tab active' : 'tab'} onClick={() => setActiveSheet(item.name)}>{item.name}</button>)}
      </section>
      <main className="workspace">
        <section className="spreadsheet-area">
          <div className="formula-bar"><span className="cell-name">{selectedCell}</span><input value={formulaDraft} onChange={(event) => setFormulaDraft(event.target.value)} onBlur={() => void saveCellRaw(formulaDraft)} onKeyDown={(event) => { if (event.key === 'Enter') void saveCellRaw(formulaDraft); }} /></div>
          <div className="sheet-scroll"><table className="grid-table"><thead><tr><th className="corner" />{COLUMNS.map((col) => <th key={col}>{col}</th>)}</tr></thead><tbody>
            {Array.from({ length: sheet?.rows ?? 50 }, (_, rowIndex) => rowIndex + 1).map((row) => <tr key={row}><th className="row-head">{row}</th>{COLUMNS.map((col) => {
              const address = `${col}${row}`;
              const cell = sheet ? ensureCell(sheet, address) : null;
              const display = cell?.value ?? cell?.raw ?? '';
              return <td key={address} className={`${selectedCell === address ? 'selected' : ''} ${cell?.status ?? 'ok'}`} onClick={() => setSelectedCell(address)} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); void bindPathToCell(event.dataTransfer.getData('text/plain'), address); }} title={String(cell?.raw ?? '')}>{String(display)}</td>;
            })}</tr>)}
          </tbody></table></div>
        </section>
        <aside className="context-side">
          <div className="context-header"><h2>PEKAT Context JSON</h2><select value={activeProject} onChange={(event) => void loadContext(event.target.value)}>{(demoState?.cameras ?? []).map((camera) => <option key={camera.project_id}>{camera.project_id}</option>)}</select></div>
          <p className="hint">P?et?hni polo?ku do bu?ky. Vlo?? se vazba =PV(...), ne statick? hodnota.</p>
          <div className="context-tree">{contextItems.map((item) => <div key={item.path} draggable onDragStart={(event) => event.dataTransfer.setData('text/plain', item.path)} className="context-item"><code>{item.path}</code><span>{String(item.value)}</span></div>)}</div>
          <details><summary>Raw JSON</summary><pre>{JSON.stringify(contextTree?.tree ?? {}, null, 2)}</pre></details>
        </aside>
      </main>
      <footer className="bottom-panel">
        <section><strong>Output mappings</strong><div className="mapping-list">{workbook?.output_mappings.map((item) => <span key={`${item.sheet_name}-${item.cell}-${item.target}`}>{item.sheet_name}!{item.cell} ? {item.target_type}.{item.target}</span>)}</div></section>
        <section><strong>Evaluation</strong><pre>{JSON.stringify({ context_updates: evaluation?.context_updates, global_updates: evaluation?.global_updates }, null, 2)}</pre></section>
        {apiError && <span className="error-text">{apiError}</span>}
      </footer>
    </div>
  );
}
