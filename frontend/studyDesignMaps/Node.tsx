import { Handle, Position, NodeProps, Node } from '@xyflow/react';

export type StudyDesignMapNodeType = {
    id: string;
    name: string;
    color: string;
    description: string;
}

export type StudyDesignMapNode = Node<StudyDesignMapNodeData, string>;

export type Resource = { id: string; name: string; }

export type StudyDesignMapNodeData = {
    name: string;
    description: string;
    organisation: string;
    resources: Resource[];
};

export function StudyDesignMapNode(props: NodeProps<StudyDesignMapNode>) {
    return (
        <div className={'study-design-map__node'}>
            <div className='data-icon-container'>
                {props.data.resources.length > 0 && <span className='mt-[9px] ml-[6px] material-symbols-outlined text-white text-[20px]'>equalizer</span>}
            </div>
            <div className='my-3 ml-[45px] font-medium min-h-[1rem] max-w-[130px] truncate'>{props.data.name}</div>
            <div className='edit-button material-symbols-outlined absolute top-2 right-2 text-md cursor-pointer'>more_vert</div>
            <Handle id='top' type='source' isValidConnection={() => true} position={Position.Top} />
            <Handle id='left' type='source' isValidConnection={() => true} position={Position.Left} />
            <Handle id='right' type='source' isValidConnection={() => true} position={Position.Right} />
            <Handle id='bottom' type='source' isValidConnection={() => true} position={Position.Bottom} />
        </div>
    );
}

export function studyDesignMapNodeNameOfType(type: string): string {
    switch (type) {
        case 'system':
            return 'System';
        case 'process':
            return 'Process';
        case 'characterisation':
            return 'Characterisation';
        case 'data':
            return 'Data';
    }
    return 'Unknown node type';
}
