import React, { useState, useCallback, useEffect } from 'react';

import { UseFetchState } from './useFetch';
import { Resource } from './Node';

type Filter = {
  value: string;
  onChange: (value: string) => void;
}

type ListBoxProps = {
  items: Resource[];
  selected: Set<string>;
  setSelected: (selected: Set<string>) => void;
  filter?: Filter;
  noItemsPlaceholder?: React.ReactElement;
  onDoubleClick?: (item: Resource) => void;
}

type ResourceSelectorProps = {
  resources: UseFetchState<Resource[]>;
  initialChosen?: Resource[];
  onChange?: (resources: Resource[]) => void;
}

const ListBox: React.FC<ListBoxProps> = ({
  items,
  selected,
  setSelected,
  filter,
  onDoubleClick = () => {},
  noItemsPlaceholder=<></>
}) => (
  <div className={`w-full rounded-md focus-within:ring-1 focus-within:ring-secondary-300 ${selected.size && 'ring-1 ring-secondary-300'}`}>
    {filter &&
      <div className="relative">
        <input
          type="text"
          placeholder="Search..."
          value={filter?.value}
          onChange={(e) => filter?.onChange(e.target.value)}
          className="w-full pl-10 pr-4 py-2 text-sm border-0 border-b border-b-gray-300 rounded-t-md bg-gray-100 focus:border-gray-300 focus:outline-none focus:ring-0"
        />
        <span className="absolute left-2 top-2">
          <span className="material-symbols-outlined text-gray-400">search</span>
        </span>
      </div>}
    <div className={`h-60 overflow-auto rounded-md bg-gray-100 ${filter && 'border-t-0 rounded-t-none'}`}>
      {items.length === 0 ? noItemsPlaceholder : (
        items.map((item) => (
          <div
            key={item.id}
            onDoubleClick={() => onDoubleClick(item)}
            onClick={() => {
              const newSelected = new Set(selected);
              if (selected.has(item.id)) {
                newSelected.delete(item.id);
              } else {
                newSelected.add(item.id);
              }
              setSelected(newSelected);
            }}
            className={`select-none px-2 py-1 cursor-pointer border-b border-white last:border-transparent hover:bg-gray-200 ${selected.has(item.id) ? 'bg-primary-200 hover:bg-primary-200' : 'bg-gray-100'} transition-colors`}
          >
            <div className="group/item flex justify-between items-start">
              <span>{item.name}</span>
              <a href={`/resources/${item.id}/`} target='registry__resource' className="ml-1 text-[22px] !no-underline group-hover/item:opacity-100 opacity-0 material-symbols-outlined" onClick={(ev) => ev.stopPropagation()}>info</a>
            </div>
          </div>
        )))}
    </div>
  </div>
);

const ResourceSelector: React.FC<ResourceSelectorProps> = ({
  resources,
  initialChosen = [],
  onChange,
}) => {
  const [availableItems, setAvailableItems] = useState<Resource[]>([]);
  const [chosenItems, setChosenItems] = useState<Resource[]>(initialChosen);

  const [availableFilter, setAvailableFilter] = useState('');

  const [selectedAvailable, setSelectedAvailable] = useState<Set<string>>(new Set());
  const [selectedChosen, setSelectedChosen] = useState<Set<string>>(new Set());

  const filteredAvailable = availableItems.filter(item =>
    item.name.toLowerCase().includes(availableFilter.toLowerCase())
  );

  useEffect(() => {
    setChosenItems(initialChosen);
  }, [initialChosen]);

  useEffect(() => {
    if (resources.data !== null) {
      setAvailableItems(resources.data.filter(resource => !chosenItems.some(chosen => chosen.id === resource.id)));
    }
  }, [resources.data, chosenItems]);

  const handleChange = useCallback((newChosen: Resource[]) => {
    onChange?.(newChosen);
  }, [onChange]);

  const moveToChosen = () => {
    const itemsToMove = availableItems.filter(item => selectedAvailable.has(item.id));
    const newChosen = [...chosenItems, ...itemsToMove];
    const newAvailable = availableItems.filter(item => !selectedAvailable.has(item.id));

    setChosenItems(newChosen);
    setAvailableItems(newAvailable);
    setSelectedAvailable(new Set());
    handleChange(newChosen);
  };

  const moveToChosenOnDoubleClick = (itemClicked: Resource) => {
    const newChosen = [itemClicked, ...chosenItems];
    const newAvailable = availableItems.filter(item => item.id != itemClicked.id);

    setChosenItems(newChosen);
    setAvailableItems(newAvailable);
    setSelectedAvailable(new Set());
    handleChange(newChosen);
  };

  const moveToAvailable = () => {
    const itemsToMove = chosenItems.filter(item => selectedChosen.has(item.id));
    const newAvailable = [...availableItems, ...itemsToMove];
    const newChosen = chosenItems.filter(item => !selectedChosen.has(item.id));

    setAvailableItems(newAvailable);
    setChosenItems(newChosen);
    setSelectedChosen(new Set());
    handleChange(newChosen);
  };

  const moveToAvailableOnDoubleClick = (itemClicked: Resource) => {
    const newAvailable = [itemClicked, ...availableItems];
    const newChosen = chosenItems.filter(item => item.id != itemClicked.id);

    setAvailableItems(newAvailable);
    setChosenItems(newChosen);
    setSelectedChosen(new Set());
    handleChange(newChosen);
  };

  const buttonClassName = `
    flex items-center justify-center h-8 w-1/2 pr-2
    rounded-md
    border border-primary-500 bg-primary-500 text-white font-medium
    disabled:border-gray-200 disabled:bg-white disabled:text-gray-500 disabled:cursor-not-allowed
    transition-colors
  `;

  return (
    <div className="flex flex-col items-start gap-2 mt-1">
      <ListBox
        items={chosenItems}
        selected={selectedChosen}
        setSelected={setSelectedChosen}
        onDoubleClick={moveToAvailableOnDoubleClick}
        noItemsPlaceholder={<div className="flex items-center justify-center w-full h-full"><p className='italic text-muted'>Select resources from the list below.</p></div>}
      />
      <div className="flex w-full gap-2">
        <button
          onClick={moveToAvailable}
          disabled={selectedChosen.size === 0}
          className={buttonClassName}
        >
          <span className="material-symbols-outlined">arrow_downward_alt</span> Remove
        </button>
        <button
          onClick={moveToChosen}
          disabled={selectedAvailable.size === 0}
          className={buttonClassName}
        >
          <span className="material-symbols-outlined">arrow_upward_alt</span> Add
        </button>
      </div>
      <ListBox
        items={filteredAvailable}
        filter={{ value: availableFilter, onChange: setAvailableFilter }}
        selected={selectedAvailable}
        setSelected={setSelectedAvailable}
        onDoubleClick={moveToChosenOnDoubleClick}
      />
    </div>
  );
};

export default ResourceSelector;
