import { Fragment, DragEvent, useState } from 'react';
import { type StudyDesignMapNodeType } from './Node';

const onDragStart = (event: DragEvent, nodeType: string) => {
  event.dataTransfer.setData('application/reactflow', nodeType);
  event.dataTransfer.effectAllowed = 'move';
};

type NodeListProps = {
  close: () => void;
  nodeTypes: Array<StudyDesignMapNodeType>;
};

function NodeList({ close, nodeTypes }: NodeListProps) {
  return (
    <div className="node-creator">
      <div className='flex items-center justify-between mb-2'>
        <div className='text-base font-semibold'>Add nodes</div>
        <button onClick={() => close()}>
          <span className="material-symbols-outlined">close</span>
        </button>
      </div>

      <p className="mb-5">Drag nodes onto the canvas.</p>

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
      {!isOpen &&
        <button className='btn btn-primary inline-flex items-center' onClick={() => setIsOpen(!isOpen)}>
          <span className="material-symbols-outlined mr-1 -ml-1">add</span>
          <span>Add nodes</span>
        </button>
      }
      {isOpen &&
        <NodeList close={() => setIsOpen(!isOpen)} nodeTypes={nodeTypes} />
      }
    </div>
  );
}
