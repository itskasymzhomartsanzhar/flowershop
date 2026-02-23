import React, { useState } from 'react';
import Navbar from '../components/Navbar/Navbar';
import Tabs from '../components/Tabs/Tabs';
import Product from '../components/Product/Product';
import SearchOverlay from '../components/SearchOverlay/SearchOverlay';
import Poster from '../components/Poster/Poster';

const Search = () => {
  const [activeTab, setActiveTab] = useState('Все');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchVisible, setSearchVisible] = useState(true);

  return (
    <>
      <Navbar
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        setSearchVisible={setSearchVisible}
      />
        <SearchOverlay
          value={searchQuery}
          onChange={setSearchQuery}
          onClose={() => {
            setSearchQuery('');
            setSearchVisible(false);
          }}
        />

      <Product activeTab={activeTab} searchQuery={searchQuery} />
    </>
  );
};

export default Search;
