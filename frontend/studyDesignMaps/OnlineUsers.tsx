import React from 'react';
import { Tooltip } from './Tooltip';

export type OnlineUser = {
  id: string;
  displayName: string; // User's display name for tooltips and initials
  color: string;
};

type OnlineUsersProps = {
  users: OnlineUser[];
};

/**
 * Component to display avatars of users currently editing the map
 * Shows colored circles with user initials in the top-right corner
 */
function OnlineUsers({ users }: OnlineUsersProps) {
  if (users.length === 0) {
    return null;
  }

  const getInitials = (name: string): string => {
    if (!name) return '?';
    
    const parts = name.split(' ');
    if (parts.length === 1) {
      return name.substring(0, 2).toUpperCase();
    }
    
    return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
  };

  return (
    <div className="absolute top-4 right-4 flex flex-col space-y-2 z-50">
      {users.map(user => (
        <Tooltip key={user.id} content={user.displayName} placement="left">
          <div 
            className="user-avatar cursor-default"
            style={{ backgroundColor: user.color }}
          >
            {getInitials(user.displayName)}
          </div>
        </Tooltip>
      ))}
    </div>
  );
}

export default OnlineUsers;