import { useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  type Edge,
  MarkerType,
  MiniMap,
  type Node,
} from "reactflow";
import "reactflow/dist/style.css";

import type { WorkflowGraph } from "../lib/types";

const TYPE_COLOR: Record<string, string> = {
  approval: "#f59e0b",
  review: "#a78bfa",
  decision: "#f472b6",
  notification: "#38bdf8",
  data_entry: "#fb923c",
  storage: "#34d399",
  integration: "#22d3ee",
  task: "#94a3b8",
};

export function WorkflowCanvas({ graph }: { graph: WorkflowGraph }) {
  const nodes: Node[] = useMemo(
    () =>
      graph.nodes.map((n) => ({
        id: n.id,
        position: n.position,
        data: { label: `${n.label}` },
        style: {
          borderColor: TYPE_COLOR[n.type] ?? "#475569",
          borderWidth: 2,
          width: 200,
          padding: 8,
        },
      })),
    [graph.nodes],
  );

  const edges: Edge[] = useMemo(
    () =>
      graph.edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label ?? undefined,
        animated: true,
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: "#64748b" },
      })),
    [graph.edges],
  );

  return (
    <div className="h-[560px] w-full rounded-xl border border-slate-800 bg-slate-950">
      <ReactFlow nodes={nodes} edges={edges} fitView proOptions={{ hideAttribution: true }}>
        <Background color="#1e293b" gap={20} />
        <MiniMap pannable zoomable maskColor="rgba(2,6,23,0.7)" nodeColor="#334155" />
        <Controls />
      </ReactFlow>
    </div>
  );
}
