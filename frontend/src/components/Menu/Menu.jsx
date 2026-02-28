import { Link, useLocation } from 'react-router-dom';
import useCart from '../../hooks/useCart';
import './Menu.scss';

const Menu = () => {
  const location = useLocation();
  const current = location.pathname;
  const { counts } = useCart();
  const itemsCount = Object.keys(counts).length;

  return (
    <div className="menu">
      <Link to="/">
        <button className="menu-icon">
          <div className={`icon-wrapper ${current === '/' ? 'active-icon' : ''}`}>
            <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 16 16" fill="currentColor" className="bi bi-grid">
            <path d="M1 2.5A1.5 1.5 0 0 1 2.5 1h3A1.5 1.5 0 0 1 7 2.5v3A1.5 1.5 0 0 1 5.5 7h-3A1.5 1.5 0 0 1 1 5.5zM2.5 2a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5zm6.5.5A1.5 1.5 0 0 1 10.5 1h3A1.5 1.5 0 0 1 15 2.5v3A1.5 1.5 0 0 1 13.5 7h-3A1.5 1.5 0 0 1 9 5.5zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5zM1 10.5A1.5 1.5 0 0 1 2.5 9h3A1.5 1.5 0 0 1 7 10.5v3A1.5 1.5 0 0 1 5.5 15h-3A1.5 1.5 0 0 1 1 13.5zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5zm6.5.5A1.5 1.5 0 0 1 10.5 9h3a1.5 1.5 0 0 1 1.5 1.5v3a1.5 1.5 0 0 1-1.5 1.5h-3A1.5 1.5 0 0 1 9 13.5zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5z"  stroke="currentColor"/>
          </svg>
          </div>
        </button>
      </Link>
      <Link to="/search">
        <button className="menu-icon">
          <div  className={`icon-wrapper ${current.startsWith('/search') ? 'active-icon' : ''}`}>
          <svg  width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"  stroke='currentColor' strokeWidth='1.5'>
            <path d="M19.6 21L13.3 14.7C12.8 15.1 12.225 15.4167 11.575 15.65C10.925 15.8833 10.2333 16 9.5 16C7.68333 16 6.14583 15.3708 4.8875 14.1125C3.62917 12.8542 3 11.3167 3 9.5C3 7.68333 3.62917 6.14583 4.8875 4.8875C6.14583 3.62917 7.68333 3 9.5 3C11.3167 3 12.8542 3.62917 14.1125 4.8875C15.3708 6.14583 16 7.68333 16 9.5C16 10.2333 15.8833 10.925 15.65 11.575C15.4167 12.225 15.1 12.8 14.7 13.3L21 19.6L19.6 21ZM9.5 14C10.75 14 11.8125 13.5625 12.6875 12.6875C13.5625 11.8125 14 10.75 14 9.5C14 8.25 13.5625 7.1875 12.6875 6.3125C11.8125 5.4375 10.75 5 9.5 5C8.25 5 7.1875 5.4375 6.3125 6.3125C5.4375 7.1875 5 8.25 5 9.5C5 10.75 5.4375 11.8125 6.3125 12.6875C7.1875 13.5625 8.25 14 9.5 14Z"/>
            </svg>
          </div>
        </button>
      </Link>

      <Link to="/cart">
        <button className="menu-icon">
          <div  className={`icon-wrapper ${current.startsWith('/cart') || current === '/confirm' ? 'active-icon' : '' || current === '/another-city' ? 'active-icon' : '' || current === '/payment-success' ? 'active-icon' : '' || current === '/choose-city' ? 'active-icon' : ''}`}>
            {itemsCount > 0 && <span className="cart-badge">{itemsCount}</span>}
            <svg width="26" height="26" className='cart' viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M1.08334 1.08337H5.41668L8.32001 15.5892C8.41907 16.088 8.69041 16.536 9.08652 16.8549C9.48262 17.1737 9.97827 17.3431 10.4867 17.3334H21.0167C21.5251 17.3431 22.0207 17.1737 22.4168 16.8549C22.8129 16.536 23.0843 16.088 23.1833 15.5892L24.9167 6.50004H6.50001M10.8333 22.75C10.8333 23.3483 10.3483 23.8334 9.75001 23.8334C9.1517 23.8334 8.66668 23.3483 8.66668 22.75C8.66668 22.1517 9.1517 21.6667 9.75001 21.6667C10.3483 21.6667 10.8333 22.1517 10.8333 22.75ZM22.75 22.75C22.75 23.3483 22.265 23.8334 21.6667 23.8334C21.0684 23.8334 20.5833 23.3483 20.5833 22.75C20.5833 22.1517 21.0684 21.6667 21.6667 21.6667C22.265 21.6667 22.75 22.1517 22.75 22.75Z" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        </button>
      </Link>

      <Link to="/favorite">
        <button className="menu-icon">
        <div className={`icon-wrapper ${current.startsWith('/favorite') ? 'active-icon' : ''}`}>
          <svg xmlns="http://www.w3.org/2000/svg" className='fav' width="26" height="26" fill='none' stroke='currentColor' strokeWidth='60' viewBox="-28 -28 565 565">
            <path d="M241 87.1l15 20.7 15-20.7C296 52.5 336.2 32 378.9 32 452.4 32 512 91.6 512 165.1l0 2.6c0 112.2-139.9 242.5-212.9 298.2-12.4 9.4-27.6 14.1-43.1 14.1s-30.8-4.6-43.1-14.1C139.9 410.2 0 279.9 0 167.7l0-2.6C0 91.6 59.6 32 133.1 32 175.8 32 216 52.5 241 87.1z"/>
          </svg>
        </div>
        </button>
      </Link>

      <Link to="/profile">
        <button className="menu-icon">
          <div className={`icon-wrapper ${current === '/profile' ? 'active-icon' : ''}`}>
            <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M25 26.25V23.75C25 22.4239 24.4732 21.1521 23.5355 20.2145C22.5979 19.2768 21.3261 18.75 20 18.75H10C8.67392 18.75 7.40215 19.2768 6.46447 20.2145C5.52678 21.1521 5 22.4239 5 23.75V26.25M20 8.75C20 11.5114 17.7614 13.75 15 13.75C12.2386 13.75 10 11.5114 10 8.75C10 5.98858 12.2386 3.75 15 3.75C17.7614 3.75 20 5.98858 20 8.75Z" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        </button>
      </Link>
    </div>
  );
};

export default Menu;
