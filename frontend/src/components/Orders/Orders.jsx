import { useEffect, useState } from 'react';
import productimg from '../../assets/product.png';
import OrderModal from '../OrderModal/OrderModal';
import { API_ENDPOINTS } from '../../utils/api';
import { getTelegramHeaders } from '../../utils/telegramHeaders';
import { copyToClipboard } from '../../utils/clipboard';
import './Orders.scss';

const Orders = ({ onInitData }) => {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    fetch(API_ENDPOINTS.ORDERS.RECENT, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getTelegramHeaders(),
      },
    })
      .then(res => res.json())
      .then(data => {
        setProducts(data);
        if (typeof onInitData === 'function') {
          onInitData(data);
        }
      })
      .catch(error => {});
  }, [onInitData]);

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
  };

  const copyTrackNumber = (trackNumber, orderId, e) => {
    e.stopPropagation();

    copyToClipboard(trackNumber)
      .then(() => {
        setCopiedId(orderId);
        setTimeout(() => setCopiedId(null), 4000);
      })
      .catch(err => {});
  };

  const getStatusStages = (currentStatus) => {
    const stages = [
      { key: 'ASSEMBLING', label: 'Собирается' },
      { key: 'ONTHEWAY', label: 'В пути' },
      { key: 'ATTHEPOINT', label: 'В пути' },
      { key: 'DELIVERED', label: 'Доставлено' }
    ];

    const statusOrder = ['ASSEMBLING', 'ONTHEWAY', 'ATTHEPOINT', 'DELIVERED'];
    const currentIndex = statusOrder.indexOf(currentStatus);

    // Если доставлено - показываем предыдущий и текущий
    if (currentIndex === stages.length - 1) {
      return [
        { ...stages[currentIndex - 1], isActive: true, isCurrent: false },
        { ...stages[currentIndex], isActive: true, isCurrent: true }
      ];
    }

    // Иначе показываем текущий и следующий
    return [
      { ...stages[currentIndex], isActive: true, isCurrent: true },
      { ...stages[currentIndex + 1], isActive: false, isCurrent: false }
    ];
  };

  return (
    <div className="orders">
      <h3 className="orders__title">Мои заказы:</h3>
      <div className="orders__list">
        {products.map(order => (
          <div
            className="orders__card"
            key={order.id}
            onClick={() => setSelectedProduct(order)}
          >
            <div className="orders__info">
              <h3 className="orders__name">{order.name}</h3>
              <p className="orders__price">{order.price}₽</p>
              <p className="orders__date">{formatDate(order.order_date)}</p>
            </div>

            <div className="orders__timeline">
              {getStatusStages(order.status).map((stage, index, array) => (
                <div key={stage.key} className="orders__stage">
                  <div className={`orders__stage-item ${stage.isActive ? 'orders__stage-item--active' : ''} ${stage.isCurrent ? 'orders__stage-item--current' : ''}`}>
                    <div className="orders__stage-dot"></div>
                    <span className="orders__stage-label">{stage.label}</span>
                  </div>
                  {index < array.length - 1 && (
                    <div className={`orders__stage-line ${stage.isActive ? 'orders__stage-line--active' : ''}`}></div>
                  )}
                </div>
              ))}
            </div>

            {(order.track_code) && (
              <button
                className={`orders__track-btn ${copiedId === order.id ? 'orders__track-btn--copied' : ''}`}
                onClick={(e) => copyTrackNumber(order.track_code, order.id, e)}
                title="Нажмите, чтобы скопировать"
              >
                {copiedId === order.id ? (
                  <>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/>
                    </svg>
                  </>
                ) : (
                  <>
                    <span>{order.track_code}</span>
                  </>
                )}
              </button>
            )}
          </div>
        ))}
      </div>

      {selectedProduct && (
        <OrderModal
          order={selectedProduct}
          onClose={() => setSelectedProduct(null)}
        />
      )}
    </div>
  );
};

export default Orders;
