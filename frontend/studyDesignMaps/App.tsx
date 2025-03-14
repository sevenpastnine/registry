import { DragEvent, useCallback } from 'react';
import {
  ReactFlow,
  MarkerType,
  ReactFlowProvider,
  Controls,
  Panel,
  Background,
  BackgroundVariant,
  NodeMouseHandler,
  useReactFlow,
  OnConnect,
  Edge,
  addEdge,
  ConnectionMode
} from '@xyflow/react';

import ShortUUID from './shortUUID';
import Cursors from './Cursors';
import OnlineUsers from './OnlineUsers';
import NodeCreator from './NodeCreator';
import { StudyDesignMapNode, type StudyDesignMapNodeType } from './Node';
import { NodeEditor } from './NodeEditor';
import { OrganisationFilter } from './NodeFilters';

import { useYjsFlow } from './useYjsFlow';
import useStudyDesignMapState from './useStudyDesignMapState';

import { type UserInfo } from './main';

type StudyDesignMapProps = {
  studyDesignId: string;
  nodeTypes: Array<StudyDesignMapNodeType>;
  organisations: Record<string, string>;
  userInfo: UserInfo;
}

function StudyDesignMap({ studyDesignId, nodeTypes, organisations, userInfo }: StudyDesignMapProps) {
  const { screenToFlowPosition } = useReactFlow();

  const currentlyEditingNode = useStudyDesignMapState((state) => state.currentlyEditingNode);
  const setCurrentlyEditingNode = useStudyDesignMapState((state) => state.setCurrentlyEditingNode);

  const studyDesignMapNodeTypes = nodeTypes.reduce(
    (acc: Record<string, typeof StudyDesignMapNode>, nodeType) => {
      acc[nodeType.id] = StudyDesignMapNode;
      return acc;
    }, {});

  const studyDesignMapNodeTypeNames = nodeTypes.reduce(
    (acc: Record<string, string>, nodeType) => {
      acc[nodeType.id] = nodeType.name;
      return acc;
    }, {});

  const {
    nodes, setNodes, onNodesChange,
    edges, setEdges, onEdgesChange,
    cursors, onMouseMove,
    onlineUsers
  } = useYjsFlow(studyDesignId, userInfo);

  const onDragOver = (event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  };

  const onDrop = (event: DragEvent) => {
    event.preventDefault();

    const type = event.dataTransfer.getData('application/reactflow');

    const position = screenToFlowPosition({
      x: event.clientX - 80,
      y: event.clientY - 20,
    });

    const newNode: StudyDesignMapNode = {
      id: ShortUUID(),
      type: type,
      position,
      data: {
        name: studyDesignMapNodeTypeNames[type],
        description: '',
        organisation: '',
        resources: [],
      },
    };

    setNodes((prev) => [...prev, newNode]);
  };

  const onConnect: OnConnect = useCallback(
    (params) => {
      const newEdge: Edge = {
        id: ShortUUID(),
        ...params
      };
      setEdges((edges) => addEdge(newEdge, edges));
    },
    [setEdges]
  );

  /**
   * Handles the click event on a node. If the meta key is not pressed, it toggles the currently editing node.
   *
   * @param event - The mouse event triggered by clicking on a node.
   * @param clickedNode - The node that was clicked.
   */
  const onNodeClick: NodeMouseHandler =
    (event, clickedNode) => {
      if (!event.metaKey) {
        if (currentlyEditingNode === clickedNode.id) {
          setCurrentlyEditingNode(null);
        } else {
          setCurrentlyEditingNode(clickedNode.id);
        }
      }
    };

  // When nodes are deleted, clear the currently editing node.
  function onNodesDelete(): void {
    setCurrentlyEditingNode(null);
  }

  /**
   * Handles the background click event.
   * If the clicked target has the class 'react-flow__pane', it sets the currently editing node to null.
   *
   * @param event - The mouse event triggered by clicking on the background.
   */
  const onBackgroundClick = (event: React.MouseEvent): void => {
    if ((event.target as HTMLElement).classList.contains('react-flow__pane')) {
      setCurrentlyEditingNode(null);
    }
  }

  return (
    <>
      <ReactFlow
        fitView={true}
        nodeTypes={studyDesignMapNodeTypes}
        nodes={nodes}
        edges={edges}
        onEdgesChange={onEdgesChange}
        onNodesChange={onNodesChange}
        onNodesDelete={onNodesDelete}
        onNodeClick={onNodeClick}
        onClick={onBackgroundClick}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onPointerMove={onMouseMove}
        connectionMode={ConnectionMode.Loose}
        snapToGrid={true}
        snapGrid={[20, 20]}
        defaultEdgeOptions={{
          markerEnd: {
            type: MarkerType.Arrow,
            width: 20,
            height: 20,
            color: '#aaa',
          }
        }}
      >
        <Cursors cursors={cursors} />
        <Controls showInteractive={false} />
        <Background
          color="#aaa"
          variant={BackgroundVariant.Dots}
          gap={10}
          offset={0} />
        <Panel position='top-left' className="">
          <NodeCreator nodeTypes={nodeTypes} />
        </Panel>
        <Panel position='top-left' className="!left-[280px]">
          <OrganisationFilter organisations={organisations} />
        </Panel>
        <OnlineUsers users={onlineUsers} />
      </ReactFlow>
      {currentlyEditingNode && <NodeEditor nodeId={currentlyEditingNode} organisations={organisations} />}
    </>
  );
}

export default function App(props: StudyDesignMapProps) {
  return (
    <ReactFlowProvider>
      <StudyDesignMap {...props} />
    </ReactFlowProvider>
  );
}
