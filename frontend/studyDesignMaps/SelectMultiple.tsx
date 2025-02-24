import React, { useState, useRef, useEffect } from 'react';

interface SelectMultipleProps {
  options: Record<string, string>;
  onChange?: (selected: string[]) => void;
  placeholder?: string;
}

const SelectMultiple: React.FC<SelectMultipleProps> = ({
  options = [],
  onChange = () => { },
  placeholder = "Select options..."
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [selected, setSelected] = useState<string[]>([]);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent): void => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleOption = (option: string): void => {
    const updatedSelection = selected.includes(option)
      ? selected.filter(item => item !== option)
      : [...selected, option];

    setSelected(updatedSelection);
    onChange(updatedSelection);
  };

  return (
    <div className="relative w-[265px]" ref={dropdownRef}>
      <button
        className="btn flex items-center justify-between w-full"
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        {selected.length === 0 ? (
          <span>{placeholder}</span>
        ) : (
          <span>
            {selected.length} item{selected.length !== 1 ? 's' : ''} selected
          </span>
        )}
        <span className={`material-symbols-outlined -mr-1 ${isOpen && 'rotate-90'} transition`}>chevron_right</span>
      </button>

      {isOpen && (
        <div
          className="absolute z-10 w-full mt-1 bg-white border rounded-lg drop-shadow-sm max-h-60 overflow-auto"
          role="listbox"
          aria-multiselectable="true"
        >
          {Object.entries(options).map(([id, label]) => (
            <div
              key={id}
              className="flex items-center px-4 py-2 cursor-pointer"
              onClick={() => toggleOption(id)}
              role="option"
              aria-selected={selected.includes(label)}
            >
              <div className="w-5 h-5 border rounded mr-2 flex items-center justify-center">
                {selected.includes(id) && (
                  <span className="material-symbols-outlined text-primary-500">check_small</span>
                )}
              </div>
              <span className="text-gray-900">{label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SelectMultiple;
