import React from 'react';
import ReactDOM from 'react-dom/client';

import App from './App';
import { type StudyDesignMapNodeType } from './Node';

export default function StudyDesignMap(
  studyDesignId: string,
  nodeTypes: Array<StudyDesignMapNodeType>,
  organisations: Record<string, string>,
) {
  ReactDOM.createRoot(document.getElementById('studyDesignMap')!).render(
    // <React.StrictMode>
      <App studyDesignId={studyDesignId} nodeTypes={nodeTypes} organisations={organisations} />
    // </React.StrictMode>
  );
}
