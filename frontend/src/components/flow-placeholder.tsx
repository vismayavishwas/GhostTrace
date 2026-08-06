"use client";

import React, { useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  Node,
  Edge,
  Position,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { STATE_MACHINE_NODES } from "@/lib/constants";

export const FlowPlaceholder: React.FC = () => {
  const initialNodes: Node[] = useMemo(() => {
    return STATE_MACHINE_NODES.map((item, index) => {
      const col = index % 5;
      const row = Math.floor(index / 5);
      return {
        id: item.id,
        position: { x: 50 + col * 230, y: 80 + row * 140 },
        data: { label: `${index + 1}. ${item.label}` },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
        style: {
          background: index === 0 ? "#1e1b4b" : "#0f172a",
          color: index === 0 ? "#818cf8" : "#94a3b8",
          border: index === 0 ? "1px solid #6366f1" : "1px solid #334155",
          borderRadius: "8px",
          padding: "10px 14px",
          fontSize: "12px",
          fontWeight: 600,
          width: 180,
          boxShadow: index === 0 ? "0 0 15px rgba(99, 102, 241, 0.2)" : "none",
        },
      };
    });
  }, []);

  const initialEdges: Edge[] = useMemo(() => {
    const edges: Edge[] = [];
    for (let i = 0; i < STATE_MACHINE_NODES.length - 1; i++) {
      edges.push({
        id: `e-${STATE_MACHINE_NODES[i].id}-${STATE_MACHINE_NODES[i + 1].id}`,
        source: STATE_MACHINE_NODES[i].id,
        target: STATE_MACHINE_NODES[i + 1].id,
        animated: true,
        style: { stroke: "#475569", strokeWidth: 1.5 },
      });
    }
    return edges;
  }, []);

  return (
    <div className="w-full h-full min-h-[320px] glass-panel rounded-xl overflow-hidden relative border border-surface-border">
      <div className="absolute top-3 left-4 z-10 bg-slate-900/80 px-3 py-1 rounded border border-slate-800 text-xs font-medium text-slate-400">
        LangGraph Orchestrator Flow (Placeholder)
      </div>
      <ReactFlow
        nodes={initialNodes}
        edges={initialEdges}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#334155" gap={16} size={1} />
        <Controls className="bg-slate-900 border-slate-800 fill-slate-300" />
      </ReactFlow>
    </div>
  );
};
