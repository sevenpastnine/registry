import { useReactFlow, useNodesData } from '@xyflow/react';

import useStudyDesignMapState from './useStudyDesignMapState';
import { type StudyDesignMapNode, type StudyDesignMapNodeData, type Resource } from './Node';
import ResourceSelector from './ResourceSelector';
import { useFetch, UseFetchState } from './useFetch';

type FormProps = {
    nodeId: string;
    data: StudyDesignMapNodeData;
    organisations: Record<string, string>;
    resources: UseFetchState<Resource[]>;
}

function Form({ nodeId, data, organisations, resources }: FormProps) {
    const { updateNodeData } = useReactFlow();

    const onNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        updateNodeData(nodeId, { name: event.target.value });
    };

    const onDescriptionChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        updateNodeData(nodeId, { description: event.target.value });
    };

    const onOrganisationChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        updateNodeData(nodeId, { organisation: event.target.value });
    };

    const onResourcesChange = (resources: Resource[]) => {
        updateNodeData(nodeId, { resources: resources });
    };

    return (
        <div className='mt-gap text-sm space-y-gap'>
            <div>
                <label className='form-label'>Name</label>
                <input type="text" spellCheck={false} className='form-text-input' value={data.name} onChange={onNameChange} />
            </div>
            <div>
                <label className='form-label'>Description</label>
                <textarea rows={2} spellCheck={false} className='resize-none form-text-input' value={data.description} onChange={onDescriptionChange}></textarea>
            </div>
            <div>
                <label className='form-label'>Organisation responsible</label>
                <select className='form-select' value={data.organisation === null ? '' : data.organisation} onChange={onOrganisationChange}>
                    <option key='empty'>------</option>
                    {Object.entries(organisations).map(([organisationId, organisationName]) =>
                        <option key={organisationId} value={organisationId}>{organisationName}</option>)}
                </select>
            </div>
            <div>
                <label className='form-label'>Resources</label>
                <ResourceSelector resources={resources} initialChosen={data.resources} onChange={onResourcesChange} />
            </div>
        </div>
    )
}

type NodeEditorProps = {
    nodeId: string;
    organisations: Record<string, string>;
}

export function NodeEditor({ nodeId, organisations }: NodeEditorProps) {
    const setCurrentlyEditingNode = useStudyDesignMapState((state) => state.setCurrentlyEditingNode);

    const node = useNodesData(nodeId) as StudyDesignMapNode;

    const resources = useFetch<Resource[]>('/api/resources/', {
        headers: {'Content-Type': 'application/json'},
        transform: (data) => data.map((resource: any) => ({ id: resource.id, name: resource.name })),
    });

    return (
        <div className="study-design-map__node-editor absolute top-0 right-0 w-[350px] h-full max-h-full p-gap overflow-y-scroll drop-shadow-sm bg-white border-l">
            <div className='material-symbols-outlined absolute top-2 right-2 text-md cursor-pointer' onClick={() => setCurrentlyEditingNode(null)}>close</div>
            <Form
                nodeId={nodeId}
                data={node.data}
                organisations={organisations}
                resources={resources}
            />
        </div>
    )
}
