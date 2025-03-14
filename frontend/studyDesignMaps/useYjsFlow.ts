import * as Y from 'yjs'
import { useState } from 'react';
import { Node, Edge } from '@xyflow/react';
import { WebsocketProvider } from 'y-websocket'

import useNodesStateSynced from './useNodesStateSynced';
import useEdgesStateSynced from './useEdgesStateSynced';
import { useCursorStateSynced } from './useCursorStateSynced';

import { useStrictModeAwareEffect } from './utils';
import { type UserInfo } from './main';

export function useYjsFlow(studyDesignId: string, userInfo: UserInfo) {

  const [{
    provider,
    nodesMap,
    edgesMap }] = useState(() => {
      const ydoc = new Y.Doc()
      const provider = new WebsocketProvider(`//${window.location.host}/ws/registry/study-design-maps/`, studyDesignId, ydoc);

      const nodesMap = ydoc.getMap<Node>('nodes');
      const edgesMap = ydoc.getMap<Edge>('edges');

      return {
        ydoc: ydoc,
        provider,
        nodesMap,
        edgesMap
      };
    });

  const [nodes, setNodes, onNodesChange] = useNodesStateSynced(nodesMap, edgesMap);
  const [edges, setEdges, onEdgesChange] = useEdgesStateSynced(edgesMap);
  const [cursors, onMouseMove] = useCursorStateSynced(provider.awareness, userInfo);

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
