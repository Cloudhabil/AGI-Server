import React, { useRef, useState, useEffect, useCallback } from 'react';
import ForceGraph3D, { type ForceGraphMethods, type NodeObject, type LinkObject } from 'react-force-graph-3d';
import SpriteText from 'three-spritetext';
import { useDropzone } from 'react-dropzone';
import { emitBusTask } from './api';
import AgentConfigModal from './AgentConfigModal';

interface GraphNode extends NodeObject {
  id: string;
  label?: string;
  x?: number;
  y?: number;
  z?: number;
}

interface GraphLink extends LinkObject {
  source: string;
  target: string;
}

const initialData = {
  nodes: [
    { id: 'orchestrator', label: 'Orchestrator' },
    { id: 'generator_primary', label: 'generator_primary' },
    { id: 'assistant_qc', label: 'assistant_qc' }
  ],
  links: [
    { source: 'orchestrator', target: 'generator_primary' },
    { source: 'orchestrator', target: 'assistant_qc' }
  ]
};

const BUS_WS_URL = 'ws://127.0.0.1:8765/ui';

const CLI_IAMindMap: React.FC = () => {
  const fgRef = useRef<ForceGraphMethods<GraphNode, GraphLink> | undefined>(undefined);
  const [graph, setGraph] = useState<{ nodes: GraphNode[]; links: GraphLink[] }>(initialData);
  const [modalState, setModalState] = useState<{ open: boolean; pos?: { x: number; y: number; z: number } }>({ open: false });

  const handleDoubleClick = useCallback((event: MouseEvent) => {
    const coords = fgRef.current?.screen2GraphCoords(event.clientX, event.clientY, 0);
    if (!coords) return;
    setModalState({ open: true, pos: coords });
  }, []);

  useEffect(() => {
    const fg = fgRef.current;
    if (!fg) return;
    const elem = fg.renderer().domElement;
    elem.addEventListener('dblclick', handleDoubleClick);
    return () => elem.removeEventListener('dblclick', handleDoubleClick);
  }, [handleDoubleClick]);

  const { getRootProps } = useDropzone({
    noClick: true,
    onDrop: files => {
      files.forEach(file => {
        const id = `asset_${Date.now()}`;
        setGraph(g => ({
          nodes: [...g.nodes, { id, label: file.name }],
          links: [...g.links, { source: 'orchestrator', target: id }]
        }));
      });
    }
  });

  useEffect(() => {
    const ws = new WebSocket(BUS_WS_URL);
    ws.onmessage = ev => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === 'bus.event') {
          // Placeholder for particle animation logic
          console.debug('bus.event', msg);
        }
      } catch (err) {
        console.error('WS message parse error', err);
      }
    };
    return () => ws.close();
  }, []);

  const handleSubmit = async (cfg: any) => {
    const id = `agent_${Date.now()}`;
    setGraph(g => ({
      nodes: [...g.nodes, { id, label: cfg.name, x: modalState.pos?.x, y: modalState.pos?.y, z: modalState.pos?.z }],
      links: [...g.links, { source: 'orchestrator', target: id }]
    }));
    await emitBusTask({ agent_id: id, cfg, initial_task: cfg.bootTask });
    setModalState({ open: false });
  };

  return (
    <div {...getRootProps()} style={{ width: '100vw', height: '100vh' }}>
      <ForceGraph3D
        ref={fgRef}
        graphData={graph}
        nodeLabel="label"
        nodeAutoColorBy="id"
        linkDirectionalParticles={2}
        linkDirectionalParticleWidth={2}
        nodeThreeObject={(node: any) => {
          const sprite = new SpriteText(node.label || node.id);
          sprite.color = 'white';
          sprite.textHeight = 4;
          return sprite;
        }}
      />
      {modalState.open && (
        <AgentConfigModal
          onSubmit={handleSubmit}
          onCancel={() => setModalState({ open: false })}
        />
      )}
    </div>
  );
};

export default CLI_IAMindMap;
