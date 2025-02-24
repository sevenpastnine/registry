import { Fragment, DragEvent, useState } from 'react';
import { type StudyDesignMapNodeType } from './Node';

const onDragStart = (event: DragEvent, nodeType: string) => {
  event.dataTransfer.setData('application/reactflow', nodeType);
  event.dataTransfer.effectAllowed = 'move';
};

function NodeList({ nodeTypes }: { nodeTypes: Array<StudyDesignMapNodeType> }) {
  return (
    <div className="node-creator">
      <p className="mb-5">Drag nodes onto the canvas:</p>

      {nodeTypes.map((nodeType) => (
        <Fragment key={nodeType.id}>
          <div className={`react-flow__node react-flow__node-${nodeType.id}`}
            onDragStart={(event: DragEvent) => onDragStart(event, nodeType.id)}
            draggable>
            <div className='study-design-map__node'>
              <div className='data-icon-container'></div>
              <div className='my-3 ml-[45px]'>{nodeType.name}</div>
            </div>
          </div>
          <p className='description'>{nodeType.description}</p>
        </Fragment>
      ))}
    </div>
  );
};

export default function NodeCreator({ nodeTypes }: { nodeTypes: Array<StudyDesignMapNodeType> }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <button className='btn btn-primary flex items-center justify-between w-[265px]' onClick={() => setIsOpen(!isOpen)}>
        <span>Add nodes</span>
        <span className={`material-symbols-outlined -mr-1 ${isOpen && 'rotate-90'} transition`}>chevron_right</span>
      </button>
      {isOpen && <NodeList nodeTypes={nodeTypes} />}
    </div>
  );
}
