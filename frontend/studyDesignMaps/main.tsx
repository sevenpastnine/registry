// import React from 'react';
import ReactDOM from 'react-dom/client';

import App from './App';
import { type StudyDesignMapNodeType } from './Node';

export type UserInfo = {
  id: string;
  displayName: string; // User's display name for UI elements
};

export default function StudyDesignMap(
  studyDesignId: string,
  nodeTypes: Array<StudyDesignMapNodeType>,
  organisations: Record<string, string>,
  userInfo: UserInfo
) {
  ReactDOM.createRoot(document.getElementById('studyDesignMap')!).render(
    // <React.StrictMode>
      <App
        studyDesignId={studyDesignId}
        nodeTypes={nodeTypes}
        organisations={organisations}
        userInfo={userInfo}
      />
    // </React.StrictMode>
  );
}
