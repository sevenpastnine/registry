import { useCallback, useEffect, useState, useRef } from 'react';
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
  lastActive: number; // Timestamp of last activity at the root level
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
    const now = Date.now();
    awareness.setLocalState({
      user: {
        id: userId,
        displayName: displayName,
        color: cursorColor
      },
      lastActive: now // Track activity time at the root level
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

      const now = Date.now();
      awareness.setLocalState({
        ...currentState,
        cursor: {
          id: userId,
          displayName: displayName,
          color: cursorColor,
          x: position.x,
          y: position.y
        },
        lastActive: now // Track activity time at the root level
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

  // Constant for inactivity threshold (10 seconds)
  const INACTIVITY_THRESHOLD_MS = 10000;

  // Check if a user is active based on lastActive timestamp
  const isActive = (lastActive: number) => {
    return (Date.now() - lastActive < INACTIVITY_THRESHOLD_MS);
  };

  // Check if a user is active based on lastActive timestamp
  const isInactive = (lastActive: number) => {
    return (Date.now() - lastActive >= INACTIVITY_THRESHOLD_MS);
  };

  useEffect(() => {
    // Update cursors and online users when awareness changes
    const updateAwareness = () => {
      const states = awareness.getStates() as Map<number, AwarenessState>;
      const cursorList: Cursor[] = [];
      const usersList: OnlineUser[] = [];

      states.forEach((state, clientId) => {
        // Skip the current user
        if (state.user && state.user.id !== userId) {
          // Determine if the user is active or inactive
          const userIsActive = isActive(state.lastActive);
          const userIsInactive = isInactive(state.lastActive);

          // Include both active and inactive users in the online users list
          if ((userIsActive || userIsInactive) && state.user) {
            // Avoid duplicates
            const exists = usersList.some(u => u.id === state.user.id);
            if (!exists) {
              usersList.push({
                id: state.user.id,
                displayName: state.user.displayName,
                color: state.user.color,
                active: Boolean(userIsActive) // Flag indicating if user is active
              });
            }
          }

          // Add to cursor list ONLY if they are active
          if (userIsActive && state.cursor) {
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

    // Set up a timer to periodically check for inactive users
    // This will re-check which users are active based on their lastActive timestamp
    const checkInactivity = () => {
      updateAwareness(); // Re-run filtering to remove inactive users
    };

    // Check every 2 seconds for inactive users
    const activityIntervalId = setInterval(checkInactivity, 2000);

    return () => {
      clearInterval(activityIntervalId);
      awareness.off('change', updateAwareness);
      awareness.setLocalState(null);
    };
  }, [awareness, userId]);

  // Return cursors, online users, and the mouse move handler
  return [cursors, onlineUsers, onMouseMove] as const;
}

export default useAwarenessState;
