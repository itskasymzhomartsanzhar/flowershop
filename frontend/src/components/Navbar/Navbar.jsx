import React from 'react';
import { Link } from 'react-router-dom';
import logoimg from '../../assets/logo.png';
import buttonimg from '../../assets/button.png';
import useCart from '../../hooks/useCart';
import './Navbar.scss';

const Navbar = ({ setSearchVisible }) => {
  const { counts } = useCart();
  const itemsCount = Object.keys(counts).length;

  return (
    <div className="navbar">
      <div className="logo">
         <img src={logoimg} alt="logo" className="logoimg" />
      </div>

      <div className="navbar-group">
        <a href="https://t.me/srezru" target="_blank" rel="noopener noreferrer">
          <button className="navbar-button">
            <img src={buttonimg} alt="logo" className="navbar-icon" />
          </button>
        </a>

      </div>
    </div>
  );
};

export default Navbar;
