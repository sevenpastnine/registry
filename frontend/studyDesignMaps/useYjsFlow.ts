import * as Y from 'yjs'
import { useState, useEffect } from 'react';
import { Node, Edge } from '@xyflow/react';
import { WebsocketProvider } from 'y-websocket'

import useNodesStateSynced from './useNodesStateSynced';
import useEdgesStateSynced from './useEdgesStateSynced';
import { useCursorStateSynced } from './useCursorStateSynced';
import { OnlineUser } from './CurrentUsers';

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
  // Get cursor information
  const [cursors, onMouseMove] = useCursorStateSynced(provider.awareness, userInfo);

  // Track other online users (excluding the current user)
  const [onlineUsers, setOnlineUsers] = useState<OnlineUser[]>([]);
  
  useEffect(() => {
    // Update the list of online users from awareness states
    // Ensures user avatars use the same colors as cursors
    const updateOnlineUsers = () => {
      const states = provider.awareness.getStates() as Map<number, { user: { id: string, displayName: string, color: string } }>;
      const users: OnlineUser[] = [];
      
      states.forEach((state, clientId) => {
        // Only include other users (not the current user)
        if (state.user && state.user.id !== userInfo.id) {
          // Check if this user is already in the list (avoid duplicates)
          const exists = users.some(u => u.id === state.user.id);
          if (!exists) {
            users.push({
              id: state.user.id,
              displayName: state.user.displayName,
              color: state.user.color // Use the same color as their cursor
            });
          }
        }
      });
      
      setOnlineUsers(users);
    };
    
    // Initial update
    updateOnlineUsers();
    
    // Subscribe to awareness changes to update when users join/leave
    provider.awareness.on('change', updateOnlineUsers);
    
    return () => {
      provider.awareness.off('change', updateOnlineUsers);
    };
  }, [provider.awareness, userInfo.id]);

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
