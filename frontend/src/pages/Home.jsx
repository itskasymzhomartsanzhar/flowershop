import React, { useState } from 'react';
import Navbar from '../components/Navbar/Navbar';
import Tabs from '../components/Tabs/Tabs';
import Product from '../components/Product/Product';
import SearchOverlay from '../components/SearchOverlay/SearchOverlay';
import Poster from '../components/Poster/Poster';

const Home = () => {
  const [activeTab, setActiveTab] = useState('Все');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchVisible, setSearchVisible] = useState(false);
  const [filterState, setFilterState] = useState(0);

  return (
    <>
      <Navbar
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        setSearchVisible={setSearchVisible}
      />

      <Tabs activeTab={activeTab} onTabChange={setActiveTab} onFilterChange={setFilterState}/>

      {searchVisible && (
        <SearchOverlay
          value={searchQuery}
          onChange={setSearchQuery}
          onClose={() => {
            setSearchQuery('');
            setSearchVisible(false);
          }}
          haveCloseBtn={true}
        />
      )}

      <Poster />

      <Product activeTab={activeTab} searchQuery={searchQuery} filterState={filterState}/>
    </>
  );
};

export default Home;
