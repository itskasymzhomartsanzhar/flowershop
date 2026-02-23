import React, { useEffect, useState } from 'react';
import API_ENDPOINTS from '../../utils/api';
import './Tabs.scss';

const Tabs = ({ activeTab, onTabChange, onFilterChange }) => {
  const [categories, setCategories] = useState([]);
  const [filterState, setFilterState] = useState(0);

  useEffect(() => {
    fetch(API_ENDPOINTS.CATEGORY.LIST)
      .then(res => res.json())
      .then(data => {
        const staticCategories = [
          { id: -1, name: 'Все' },
          { id: -2, name: 'Новинки' },
          { id: -3, name: 'Популярные' },
        ];

        const allCategories = [...staticCategories, ...data];
        setCategories(allCategories);

        if (!activeTab) {
          onTabChange('Все');
        }
      })
      .catch(err => console.error('Ошибка категорий:', err));
  }, []);

  const handleFilterClick = () => {
    const newState = (filterState + 1) % 3; // 0 → 1 → 2 → 0
    setFilterState(newState);
    if (onFilterChange) {
      onFilterChange(newState);
    }
  };

  const renderFilterIcon = () => {
    if (filterState === 1) {
      return (
          <svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" fill="currentColor"
             className="bi bi-sort-up filter-svg" viewBox="0 0 16 16">
          <path d="M3.5 12.5a.5.5 0 0 1-1 0V3.707L1.354 
            4.854a.5.5 0 1 1-.708-.708l2-1.999.007-.007a.5.5 
            0 0 1 .7.006l2 2a.5.5 
            0 1 1-.707.708L3.5 3.707zm3.5-9a.5.5 
            0 0 1 .5-.5h7a.5.5 
            0 0 1 0 1h-7a.5.5 
            0 0 1-.5-.5M7.5 6a.5.5 
            0 0 0 0 1h5a.5.5 
            0 0 0 0-1zm0 3a.5.5 
            0 0 0 0 1h3a.5.5 
            0 0 0 0-1zm0 3a.5.5 
            0 0 0 0 1h1a.5.5 
            0 0 0 0-1z"/>
        </svg>

      );
    } else if (filterState === 2) {
      return (
        <svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" fill="currentColor"
             className="bi bi-sort-down filter-svg" viewBox="0 0 16 16">
          <path d="M3.5 2.5a.5.5 0 0 0-1 0v8.793l-1.146-1.147a.5.5 0 0 0-.708.708l2 
            1.999.007.007a.497.497 0 0 0 .7-.006l2-2a.5.5 
            0 0 0-.707-.708L3.5 11.293zm3.5 1a.5.5 
            0 0 1 .5-.5h7a.5.5 
            0 0 1 0 1h-7a.5.5 
            0 0 1-.5-.5M7.5 6a.5.5 
            0 0 0 0 1h5a.5.5 
            0 0 0 0-1zm0 3a.5.5 
            0 0 0 0 1h3a.5.5 
            0 0 0 0-1zm0 3a.5.5 
            0 0 0 0 1h1a.5.5 
            0 0 0 0-1z"/>
        </svg>
      );
    }
    return (
      <svg xmlns="http://www.w3.org/2000/svg" width="34" height="34" fill="currentColor"
           className="bi bi-filter-circle filter-svg" viewBox="0 0 16 16">
        <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 
          1A8 8 0 1 0 8 0a8 8 0 0 0 0 
          16"/>
        <path d="M7 11.5a.5.5 0 0 1 .5-.5h1a.5.5 
          0 0 1 0 1h-1a.5.5 
          0 0 1-.5-.5m-2-3a.5.5 
          0 0 1 .5-.5h5a.5.5 
          0 0 1 0 1h-5a.5.5 
          0 0 1-.5-.5m-2-3a.5.5 
          0 0 1 .5-.5h9a.5.5 
          0 0 1 0 1h-9a.5.5 
          0 0 1-.5-.5"/>
      </svg>
    );
  };

  return (
    <div className="tabs-wrapper">
      <div className="tabs">
        <button
          className={`tabs-btn filter-btn ${filterState !== 0 ? 'active' : ''}`}
          onClick={handleFilterClick}
        >
          {renderFilterIcon()}
        </button>

        {categories.map((category) => (
          <button
            key={category.id}
            className={`tabs-btn ${activeTab === category.name ? 'active' : ''}`}
            onClick={() => onTabChange(category.name)}
          >
            {category.name}
          </button>
        ))}
      </div>
    </div>
  );
};

export default Tabs;