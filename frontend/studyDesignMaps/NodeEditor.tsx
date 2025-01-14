import React, { useCallback, useRef } from 'react';
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

type SharedTextInputProps = {
    value: string;
    updateData: (value: string) => void;
}

const OnChangeSharedText = ({ value, updateData }: SharedTextInputProps) => {
    const inputRef = useRef<any>(null);

    const onChange = useCallback((event: React.ChangeEvent<HTMLInputElement|HTMLTextAreaElement>) => {
        const cursorPosition = event.target.selectionStart;
        updateData(event.target.value);

        requestAnimationFrame(() => {
            if (inputRef.current) {
                inputRef.current.setSelectionRange(cursorPosition, cursorPosition);
            }
        });
    }, [value]);

    return ({ inputRef, onChange });
}

function Form({ nodeId, data, organisations, resources }: FormProps) {
    const { updateNodeData } = useReactFlow();

    const nameInput = OnChangeSharedText({ value: data.name, updateData: (value: string) => updateNodeData(nodeId, { name: value }) });
    const descriptionInput = OnChangeSharedText({ value: data.description, updateData: (value: string) => updateNodeData(nodeId, { description: value }) });

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
                <input ref={nameInput.inputRef} type="text" spellCheck={false} className='form-text-input' value={data.name} onChange={nameInput.onChange} />
            </div>
            <div>
                <label className='form-label'>Description</label>
                <textarea ref={descriptionInput.inputRef} rows={2} spellCheck={false} className='resize-none form-text-input' value={data.description} onChange={descriptionInput.onChange}></textarea>
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
        headers: { 'Content-Type': 'application/json' },
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
