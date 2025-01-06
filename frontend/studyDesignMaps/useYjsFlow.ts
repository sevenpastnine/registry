import { useState } from 'react';
import { HocuspocusProvider } from "@hocuspocus/provider";
import { Node, Edge } from '@xyflow/react';

import useNodesStateSynced from './useNodesStateSynced';
import useEdgesStateSynced from './useEdgesStateSynced';
import { type Cursor, useCursorStateSynced } from './useCursorStateSynced';

import { useStrictModeAwareEffect } from './utils';

export function useYjsFlow(studyDesignId: string) {

  const [{
    ydoc,
    provider,
    nodesMap,
    edgesMap,
    cursorsMap }] = useState(() => {
      const provider = new HocuspocusProvider({
        url: "ws://localhost:1234",
        name: studyDesignId,
      });

      const nodesMap = provider.document.getMap<Node>('nodes');
      const edgesMap = provider.document.getMap<Edge>('edges');
      const cursorsMap = provider.document.getMap<Cursor>('cursors');

      return {
        ydoc: provider.document,
        provider,
        nodesMap,
        edgesMap,
        cursorsMap
      };
    });

  const [nodes, setNodes, onNodesChange] = useNodesStateSynced(nodesMap, edgesMap);
  const [edges, setEdges, onEdgesChange] = useEdgesStateSynced(edgesMap);
  const [cursors, onMouseMove] = useCursorStateSynced(cursorsMap, ydoc.clientID.toString());

  useStrictModeAwareEffect(() => {
    return () => {
      provider.disconnect();
    };
  }, []);

  return {
    nodes, setNodes, onNodesChange,
    edges, setEdges, onEdgesChange,
    cursors, onMouseMove
  };
}
