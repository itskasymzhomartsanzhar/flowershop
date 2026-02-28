import { useEffect, useRef, useState } from 'react';
import './SearchOverlay.scss';

const SearchOverlay = ({ value, onChange, onClear, onClose, haveCloseBtn }) => {
  const inputRef = useRef(null);
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
      setIsFocused(true);
    }
  }, []);

  return (
    <div className="search-overlay">
      <div
        className={`search-input-container ${isFocused ? 'is-focused' : ''} ${!value ? 'is-empty' : ''}`}
      >
        <input
          ref={inputRef}
          type="text"
          placeholder="Введите название"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
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
