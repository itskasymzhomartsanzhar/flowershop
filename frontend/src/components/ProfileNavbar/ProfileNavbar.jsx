import profileimg from '../../assets/profile.png';
import './ProfileNavbar.scss';
import API_ENDPOINTS from '../../utils/api';
import getTelegramHeaders from '../../utils/telegramHeaders';

const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;

const name = `${tgUser?.first_name || ''} ${tgUser?.last_name || ''}`.trim();
const username = tgUser?.username ? `@${tgUser.username}` : '@username';
const photoUrl = tgUser?.photo_url || profileimg;

const ProfileNavbar = () => {
  const handleDeliveryTerms = (event) => {
    event.preventDefault();
    fetch(API_ENDPOINTS.USERS.DELIVERY_TERMS, {
      method: 'POST',
      headers: getTelegramHeaders(),
    }).catch(() => {});
  };

  return (
    <>
      <div className="profile-navbar">
        <img src={photoUrl} alt="Photo" className="profileimg" />
        <h2 className="profiletext">{name} ({username})</h2>
      </div>
      <div className="link-wrapper">
        <div className="link">
          <a href="https://t.me/srez_zabota"><button className="link-btn">Поддержка</button></a>
          <button className="link-btn" onClick={handleDeliveryTerms}>Условия доставки</button>
          <a href=""><button className="link-btn">Политика конфиденциальности</button></a>
        </div>
      </div>
    </>
  );
};

export default ProfileNavbar;
