import React, { useState } from 'react';

type TooltipProps = {
  children: React.ReactNode;
  content: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
};

export function Tooltip({ children, content, placement = 'top' }: TooltipProps) {
  const [visible, setVisible] = useState(false);

  // Placement class
  const placementClass = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2',
  }[placement];

  return (
    <div className="relative flex" 
      onMouseEnter={() => setVisible(true)} 
      onMouseLeave={() => setVisible(false)}
    >
      {children}
      {visible && (
        <div className={`absolute z-50 ${placementClass} px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap`}>
          {content}
        </div>
      )}
    </div>
  );
}