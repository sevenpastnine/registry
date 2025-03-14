import { useCallback, useEffect, useMemo, useState, useRef } from 'react';
import { Awareness } from 'y-protocols/awareness';
import { useReactFlow } from '@xyflow/react';
import { getUserColor, throttle } from './utils';
import { UserInfo } from './main';
import { OnlineUser } from './OnlineUsers';

export type Cursor = {
  id: string;
  displayName: string;
  color: string;
  x: number;
  y: number;
};

type AwarenessState = {
  cursor: Cursor;
  user: {
    id: string;
    displayName: string;
    color: string;
  };
};

export function useAwarenessState(awareness: Awareness, userInfo: UserInfo) {
  const [cursors, setCursors] = useState<Cursor[]>([]);
  const [onlineUsers, setOnlineUsers] = useState<OnlineUser[]>([]);
  const { screenToFlowPosition } = useReactFlow();

  const userId = userInfo.id;
  const displayName = userInfo.displayName;

  // Store the user's color in a ref to keep it stable
  const userColorRef = useRef<string | null>(null);
  
  // Initialize the color only once
  if (userColorRef.current === null) {
    userColorRef.current = getUserColor([]);
  }
  
  // Use the stable color reference
  const cursorColor = userColorRef.current;

  // Set initial user state - this persists across reconnections
  useEffect(() => {
    awareness.setLocalState({
      user: {
        id: userId,
        displayName: displayName,
        color: cursorColor
      }
    });
  }, [awareness, userId, displayName, cursorColor]);

  // Throttled cursor update function
  const updateCursorPosition = useCallback(
    (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      // Update only the cursor part of the local state
      const currentState = awareness.getLocalState() as AwarenessState || {};

      awareness.setLocalState({
        ...currentState,
        cursor: {
          id: userId,
          displayName: displayName,
          color: cursorColor,
          x: position.x,
          y: position.y,
        }
      });
    },
    [awareness, screenToFlowPosition, userId, displayName, cursorColor]
  );

  // Create a throttled version that limits updates
  const throttledUpdateRef = useRef(throttle(updateCursorPosition, 50));

  // Mouse move handler
  const onMouseMove = useCallback(
    (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
      throttledUpdateRef.current(event);
    },
    [throttledUpdateRef]
  );

  useEffect(() => {
    // Update cursors and online users when awareness changes
    const updateAwareness = () => {
      const states = awareness.getStates() as Map<number, AwarenessState>;
      const cursorList: Cursor[] = [];
      const usersList: OnlineUser[] = [];

      states.forEach((state, clientId) => {
        // Skip the current user
        if (state.user && state.user.id !== userId) {
          // Add to online users list if they have user info
          if (state.user) {
            // Avoid duplicates
            const exists = usersList.some(u => u.id === state.user.id);
            if (!exists) {
              usersList.push({
                id: state.user.id,
                displayName: state.user.displayName,
                color: state.user.color
              });
            }
          }
          
          // Add to cursor list if they have cursor info
          if (state.cursor) {
            cursorList.push({
              ...state.cursor,
              // Use a composite key of clientId and user ID to ensure uniqueness
              id: `${clientId}-${state.user.id}`,
              displayName: state.user.displayName,
              color: state.user.color || state.cursor.color
            });
          }
        }
      });
      
      setCursors(cursorList);
      setOnlineUsers(usersList);
    };

    // Initial update
    updateAwareness();

    // Subscribe to awareness changes
    awareness.on('change', updateAwareness);

    return () => {
      awareness.off('change', updateAwareness);
    };
  }, [awareness, userId]);

  // Return cursors, online users, and the mouse move handler
  return [cursors, onlineUsers, onMouseMove] as const;
}

export default useAwarenessState;
