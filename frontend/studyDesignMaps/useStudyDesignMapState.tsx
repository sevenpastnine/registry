import { create } from 'zustand';

type StudyDesignMapState = {
  currentlyEditingNode: null | string,
  setCurrentlyEditingNode: (nodeId: string | null) => void,
  selectedOrganisationsFilter: string[],
  setSelectedOrganisationsFilter: (selectedItems: string[]) => void,
}

export default create<StudyDesignMapState>((set) => ({
    currentlyEditingNode: null,
    setCurrentlyEditingNode: (nodeId: string | null) => set({ currentlyEditingNode: nodeId }),
    selectedOrganisationsFilter: [],
    setSelectedOrganisationsFilter: (selectedItems: string[]) => set({ selectedOrganisationsFilter: selectedItems }),
  }))
