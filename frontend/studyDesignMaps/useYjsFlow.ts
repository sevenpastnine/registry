import * as Y from 'yjs'
import { useState } from 'react';
import { Node, Edge } from '@xyflow/react';
import { WebsocketProvider } from 'y-websocket'

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
      const ydoc = new Y.Doc()
      const provider = new WebsocketProvider(`//${window.location.host}/ws/registry/study-design-maps/`, studyDesignId, ydoc);

      const nodesMap = ydoc.getMap<Node>('nodes');
      const edgesMap = ydoc.getMap<Edge>('edges');
      const cursorsMap = ydoc.getMap<Cursor>('cursors');

      return {
        ydoc: ydoc,
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
