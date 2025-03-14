import { useCallback, useEffect, useMemo, useState, useRef } from 'react';
import { Awareness } from 'y-protocols/awareness';
import { useReactFlow } from '@xyflow/react';
import { getUserColor, throttle } from './utils';
import { UserInfo } from './main';

export type Cursor = {
  id: string;
  username: string;
  color: string;
  x: number;
  y: number;
};

type AwarenessState = {
  cursor: Cursor;
  user: {
    id: string;
    username: string;
    color: string;
  };
};

export function useCursorStateSynced(awareness: Awareness, userInfo: UserInfo) {
  const [cursors, setCursors] = useState<Cursor[]>([]);
  const { screenToFlowPosition } = useReactFlow();

  const userId = userInfo.id;
  const username = userInfo.username;

  // Generate a stable color based on user ID
  const cursorColor = useMemo(() => getUserColor(), [userId]);

  // Set initial user state - this persists across reconnections
  useEffect(() => {
    awareness.setLocalState({
      user: {
        id: userId,
        username: username,
        color: cursorColor
      }
    });
  }, [awareness, userId, username, cursorColor]);

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
          username,
          color: cursorColor,
          x: position.x,
          y: position.y,
        }
      });
    },
    [awareness, screenToFlowPosition, userId, username, cursorColor]
  );

  // Create a throttled version that limits updates
  const throttledUpdateRef = useRef(throttle(updateCursorPosition, 30));

  // Mouse move handler
  const onMouseMove = useCallback(
    (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
      throttledUpdateRef.current(event);
    },
    [throttledUpdateRef]
  );

  useEffect(() => {
    // Update cursors when awareness changes
    const updateCursors = () => {
      const states = awareness.getStates() as Map<number, AwarenessState>;
      const cursorList: Cursor[] = [];

      states.forEach((state, clientId) => {
        if (state.cursor && state.user.id !== userId) {
          cursorList.push({
            ...state.cursor,
            // Use a composite key of clientId and user ID to ensure uniqueness
            id: `${clientId}-${state.user.id}`,
            username: state.user.username,
            color: state.user.color || state.cursor.color
          });
        }
      });

      setCursors(cursorList);
    };

    // Initial update
    updateCursors();

    // Subscribe to awareness changes
    awareness.on('change', updateCursors);

    return () => {
      awareness.off('change', updateCursors);
    };
  }, [awareness, userId]);

  return [cursors, onMouseMove] as const;
}

export default useCursorStateSynced;
