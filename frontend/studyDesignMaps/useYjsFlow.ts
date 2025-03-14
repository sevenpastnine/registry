import * as Y from 'yjs'
import { useState, useEffect } from 'react';
import { Node, Edge } from '@xyflow/react';
import { WebsocketProvider } from 'y-websocket'

import useNodesStateSynced from './useNodesStateSynced';
import useEdgesStateSynced from './useEdgesStateSynced';
import { useAwarenessState } from './useAwarenessState';
import { OnlineUser } from './OnlineUsers';

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
  
  // Use awareness hook to handle both cursor positions and online users
  const [cursors, onlineUsers, onMouseMove] = useAwarenessState(provider.awareness, userInfo);

  useEffect(() => {
    // Handle page unload/refresh explicitly
    // Needed to remove the local state from the awareness
    const handleBeforeUnload = () => {
      provider.awareness.setLocalState(null);
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [provider]);

  return {
    nodes, setNodes, onNodesChange,
    edges, setEdges, onEdgesChange,
    cursors, onMouseMove,
    onlineUsers
  };
}
