import { useEffect, useRef } from 'react';
import './SearchOverlay.scss';

const SearchOverlay = ({ value, onChange, onClear, onClose, haveCloseBtn }) => {
  const inputRef = useRef(null);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  return (
    <div className="search-overlay">
      <div className="search-input-container">
        <input
          ref={inputRef}
          type="text"
          placeholder="Введите название"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="search-input"
          maxLength={120}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
          spellCheck={false}
        />
      </div>
    </div>
  );
};

export default SearchOverlay;
