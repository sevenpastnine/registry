import React from 'react';

type TooltipProps = {
  children: React.ReactNode;
  content: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
};

export function Tooltip({ children, content, placement = 'top' }: TooltipProps) {
  // Placement class
  const placementClass = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2',
  }[placement];

  return (
    <div className="tooltip-container relative flex group">
      {children}
      <div
        className={`
          absolute z-50 ${placementClass} px-2 py-1
          bg-gray-800 text-white text-xs rounded whitespace-nowrap
          opacity-0 invisible
          group-hover:opacity-100 group-hover:visible
          transition-all duration-75 delay-200
        `}
      >
        {content}
      </div>
    </div>
  );
}
