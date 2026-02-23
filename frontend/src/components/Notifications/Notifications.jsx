import { useEffect, useState } from 'react';
import { API_ENDPOINTS } from '../../utils/api';
import { getTelegramHeaders } from '../../utils/telegramHeaders';
import './Notifications.scss';

const Notifications = () => {
  const [orderStatus, setOrderStatus] = useState(true);
  const [promotion, setPromotion] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserSettings();
  }, []);

  const fetchUserSettings = () => {
    fetch(API_ENDPOINTS.USERS.PROFILE, {
      headers: getTelegramHeaders(),
    })
      .then(res => res.json())
      .then(data => {
        setOrderStatus(data.notification_order_status);
        setPromotion(data.notification_promotion);
        setLoading(false);
      })
      .catch(err => {
        setLoading(false);
      });
  };

  const updateNotification = (notificationType, enabled) => {
    fetch(API_ENDPOINTS.USERS.UPDATE_NOTIFICATIONS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getTelegramHeaders(),
      },
      body: JSON.stringify({
        notification_type: notificationType,
        enabled: enabled,
      }),
    })
      .then(res => res.json())
      .then(data => {})
      .catch(err => {});
  };

  const toggleOrderStatus = () => {
    const newValue = !orderStatus;
    setOrderStatus(newValue);
    updateNotification('order_status', newValue);
  };

  const togglePromotion = () => {
    const newValue = !promotion;
    setPromotion(newValue);
    updateNotification('promotion', newValue);
  };

  if (loading) {
    return <div>Загрузка...</div>;
  }

  return (
    <div className="notifications">
      <h3 className="notifications__title">Уведомления</h3>

      <div className="notifications__card">
        <div className="notifications__content">
          <h4 className="notifications__label">Статус заказа</h4>
          <p className="notifications__description">
            Получайте уведомления об изменении статуса вашего заказа: подтверждение, отправка и доставка
          </p>
        </div>
        <label className="notifications__switch">
          <input
            type="checkbox"
            checked={orderStatus}
            onChange={toggleOrderStatus}
            className="notifications__input"
          />
          <span className="notifications__slider"></span>
        </label>
      </div>

      <div className="notifications__card">
        <div className="notifications__content">
          <h4 className="notifications__label">Акции и новинки</h4>
          <p className="notifications__description">
            Узнавайте первыми о специальных предложениях, скидках и новых товарах в каталоге
          </p>
        </div>
        <label className="notifications__switch">
          <input
            type="checkbox"
            checked={promotion}
            onChange={togglePromotion}
            className="notifications__input"
          />
          <span className="notifications__slider"></span>
        </label>
      </div>
    </div>
  );
};

export default Notifications;
