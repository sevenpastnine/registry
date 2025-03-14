import { EdgeLabelRenderer, useViewport } from '@xyflow/react';
import { memo } from 'react';
import { type Cursor } from './useCursorStateSynced';

// Memoized individual cursor component to optimize rendering
const CursorItem = memo(({ id, username, color, x, y, zoom }: Cursor & { zoom: number }) => {
  const translate = `translate(${x}px, ${y}px)`;
  const scale = `scale(${1 / zoom})`;

  return (
    <div key={id} className="cursor" style={{ transform: translate, position: 'absolute', pointerEvents: 'none', zIndex: 1000 }}>
      <div
        title={username}
        style={{
          position: 'absolute',
          transform: scale,
          transformOrigin: '0 0'
        }}
      >
        <svg width="10" height="10" viewBox="0 0 10 10">
          <circle
            cx="5"
            cy="5"
            r="4"
            fill={color}
            stroke="white"
            strokeWidth="1"
          />
        </svg>
      </div>
    </div>
  );
});

function Cursors({ cursors }: { cursors: Cursor[] }) {
  const viewport = useViewport();

  if (cursors.length === 0) {
    return null;
  }

  return (
    <EdgeLabelRenderer>
      {cursors.map((cursor) => (
        <CursorItem
          key={cursor.id}
          {...cursor}
          zoom={viewport.zoom}
        />
      ))}
    </EdgeLabelRenderer>
  );
}

export default Cursors;
