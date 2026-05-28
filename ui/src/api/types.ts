export type SpreadsheetOutputs = {
  master_result?: boolean;
  allow_branch_default?: boolean;
};

export type SpreadsheetState = {
  project_id: string;
  frame_id: string;
  mode: string;
  last_update_ts: string;
  result: boolean;
  reason: string;
  outputs: SpreadsheetOutputs;
};

export type Evaluation = {
  ok: boolean;
  context_updates: {
    spreadsheet?: SpreadsheetState;
  };
  global_updates: Record<string, unknown>;
  control: {
    exit: boolean;
    override_result: boolean | null;
  };
};

export type DemoSnapshot = {
  project_id: string;
  frame_id: string;
  timestamp: string;
  mode: string;
  context: Record<string, unknown>;
  global_data: Record<string, unknown>;
};

export type DemoCamera = {
  project_id: string;
  name: string;
  frame_index: number;
  last_snapshot: DemoSnapshot | null;
  last_evaluation: Evaluation | null;
};

export type DemoState = {
  running: boolean;
  tick_index: number;
  cameras: DemoCamera[];
};
