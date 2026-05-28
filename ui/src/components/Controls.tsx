type Props = {
  onStart: () => void;
  onTick: () => void;
  onReset: () => void;
  loading: boolean;
};

export function Controls({ onStart, onTick, onReset, loading }: Props) {
  return (
    <section className="panel controls-panel">
      <button onClick={onStart} disabled={loading}>Start demo</button>
      <button onClick={onTick} disabled={loading}>Tick frame</button>
      <button className="secondary" onClick={onReset} disabled={loading}>Reset</button>
    </section>
  );
}
