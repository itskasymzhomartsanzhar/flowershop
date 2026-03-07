import profileimg from '../../assets/profile.png';
import './ProfileNavbar.scss';

const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;

const name = `${tgUser?.first_name || ''} ${tgUser?.last_name || ''}`.trim();
const username = tgUser?.username ? `@${tgUser.username}` : '@username';
const photoUrl = tgUser?.photo_url || profileimg;

const ProfileNavbar = () => {
  const handleDeliveryTerms = (event) => {
    event.preventDefault();
    const tg = window.Telegram?.WebApp;
    if (tg && typeof tg.sendData === 'function') {
      tg.sendData('delivery_terms');
    }
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
