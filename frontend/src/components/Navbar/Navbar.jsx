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
        <Link to="/cart" className="navbar-link">
          <button className="navbar-button navbar-button--cart">
            {itemsCount > 0 && <span className="navbar-badge">{itemsCount}</span>}
            <svg width="22" height="22" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M1.08334 1.08337H5.41668L8.32001 15.5892C8.41907 16.088 8.69041 16.536 9.08652 16.8549C9.48262 17.1737 9.97827 17.3431 10.4867 17.3334H21.0167C21.5251 17.3431 22.0207 17.1737 22.4168 16.8549C22.8129 16.536 23.0843 16.088 23.1833 15.5892L24.9167 6.50004H6.50001M10.8333 22.75C10.8333 23.3483 10.3483 23.8334 9.75001 23.8334C9.1517 23.8334 8.66668 23.3483 8.66668 22.75C8.66668 22.1517 9.1517 21.6667 9.75001 21.6667C10.3483 21.6667 10.8333 22.1517 10.8333 22.75ZM22.75 22.75C22.75 23.3483 22.265 23.8334 21.6667 23.8334C21.0684 23.8334 20.5833 23.3483 20.5833 22.75C20.5833 22.1517 21.0684 21.6667 21.6667 21.6667C22.265 21.6667 22.75 22.1517 22.75 22.75Z" stroke="currentColor" strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </Link>
        <a href="https://t.me/swiftagencyru" target="_blank" rel="noopener noreferrer">
          <button className="navbar-button">
            <img src={buttonimg} alt="logo" className="navbar-icon" />
          </button>
        </a>
        <a href="https://t.me/swiftagencyru" target="_blank" rel="noopener noreferrer">
          <button className="navbar-button">
            <svg xmlns="http://www.w3.org/2000/svg" width="21" height="21" fill="#707579" className="bi bi-instagram" viewBox="0 0 16 16">
              <path d="M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.9 3.9 0 0 0-1.417.923A3.9 3.9 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.7.01 5.555 0 5.827 0 8.001c0 2.172.01 2.444.048 3.297.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923.51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.298-.048c.851-.04 1.434-.174 1.943-.372a3.9 3.9 0 0 0 1.416-.923c.445-.445.718-.891.923-1.417.197-.509.332-1.09.372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.445-.048-3.299c-.04-.851-.175-1.433-.372-1.941a3.9 3.9 0 0 0-.923-1.417A3.9 3.9 0 0 0 13.24.42c-.51-.198-1.092-.333-1.943-.372C10.443.01 10.172 0 7.998 0zm-.717 1.442h.718c2.136 0 2.389.007 3.232.046.78.035 1.204.166 1.486.275.373.145.64.319.92.599s.453.546.598.92c.11.281.24.705.275 1.485.039.843.047 1.096.047 3.231s-.008 2.389-.047 3.232c-.035.78-.166 1.203-.275 1.485a2.5 2.5 0 0 1-.599.919c-.28.28-.546.453-.92.598-.28.11-.704.24-1.485.276-.843.038-1.096.047-3.232.047s-2.39-.009-3.233-.047c-.78-.036-1.203-.166-1.485-.276a2.5 2.5 0 0 1-.92-.598 2.5 2.5 0 0 1-.6-.92c-.109-.281-.24-.705-.275-1.485-.038-.843-.046-1.096-.046-3.233s.008-2.388.046-3.231c.036-.78.166-1.204.276-1.486.145-.373.319-.64.599-.92s.546-.453.92-.598c.282-.11.705-.24 1.485-.276.738-.034 1.024-.044 2.515-.045zm4.988 1.328a.96.96 0 1 0 0 1.92.96.96 0 0 0 0-1.92m-4.27 1.122a4.109 4.109 0 1 0 0 8.217 4.109 4.109 0 0 0 0-8.217m0 1.441a2.667 2.667 0 1 1 0 5.334 2.667 2.667 0 0 1 0-5.334"/>
            </svg>

          </button>
        </a>

      </div>
    </div>
  );
};

export default Navbar;
