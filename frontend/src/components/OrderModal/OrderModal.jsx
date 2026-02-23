import { useState, useEffect } from 'react';
import useCarousel from '../../hooks/useCarousel';
import getTelegramHeaders from '../../utils/telegramHeaders';
import { copyToClipboard } from '../../utils/clipboard';
import { API_BASE_URL } from '../../utils/api';
import './OrderModal.scss';

const OrderModal = ({ order, onClose }) => {
  const [closing, setClosing] = useState(false);
  const [activeReviewItem, setActiveReviewItem] = useState(null);
  const [reviewText, setReviewText] = useState('');
  const [reviewStars, setReviewStars] = useState(5);
  const [reviewStates, setReviewStates] = useState({});
  const [copiedId, setCopiedId] = useState(null);

  const photos = [];
  if (order.product) {
    for (let i = 1; i <= 10; i++) {
      const photoKey = `photo${i}`;
      if (order.product[photoKey]) {
        photos.push(order.product[photoKey]);
      }
    }
  }

  if (photos.length === 0 && order.photo) {
    photos.push(order.photo);
  }

  const { slideIndex, carouselRef, goToSlide } = useCarousel(photos.length);

  const handleClose = () => setClosing(true);
  const onAnimationEnd = () => {
    if (closing) onClose();
  };

useEffect(() => {
  document.body.style.overflow = 'hidden';
  checkReviewsForAllItems();

  const tg = window.Telegram?.WebApp;
  if (tg) {
    tg.BackButton.show();
    const handleBack = () => handleClose();
    tg.BackButton.onClick(handleBack);

    return () => {
      tg.BackButton.offClick(handleBack);
      tg.BackButton.hide();
      document.body.style.overflow = '';
    };
  } else {
    return () => {
      document.body.style.overflow = '';
    };
  }
}, []);

  const checkReviewsForAllItems = () => {
    if (order.order_items && order.order_items.length > 0) {
      const newStates = {};

      Promise.all(
        order.order_items.map((item) =>
          fetch(`${API_BASE_URL}/reviews/check/?order_id=${order.id}&order_item_id=${item.id}`, {
            headers: getTelegramHeaders(),
          })
            .then((res) => res.json())
            .then((data) => {
              newStates[item.id] = {
                hasReview: data.has_review,
                submitting: false
              };
            })
            .catch((err) => {
              console.error(`Ошибка проверки отзыва для товара ${item.id}:`, err);
              newStates[item.id] = {
                hasReview: false,
                submitting: false
              };
            })
        )
      ).then(() => {
        setReviewStates(newStates);
      });
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
  };

  const handleSubmitReview = (orderItemId, productId) => {
    if (reviewText.trim() === '') {
      alert('Пожалуйста, напишите отзыв');
      return;
    }

    setReviewStates(prev => ({
      ...prev,
      [orderItemId]: { ...prev[orderItemId], submitting: true }
    }));

    fetch(`${API_BASE_URL}/reviews/`, {
      method: 'POST',
      headers: getTelegramHeaders(),
      body: JSON.stringify({
        order_id: order.id,
        order_item_id: orderItemId,
        product_id: productId,
        text: reviewText,
        stars: reviewStars,
      }),
    })
      .then((res) => res.json())
      .then(() => {
        setReviewStates(prev => ({
          ...prev,
          [orderItemId]: { hasReview: true, submitting: false }
        }));
        setActiveReviewItem(null);
        setReviewText('');
        setReviewStars(5);
      })
      .catch((err) => {
        console.error('Ошибка отправки отзыва:', err);
        setReviewStates(prev => ({
          ...prev,
          [orderItemId]: { ...prev[orderItemId], submitting: false }
        }));
        alert('Произошла ошибка. Попробуйте еще раз.');
      });
  };

  const handleCopyTrackNumber = async (trackNumber, orderId, e) => {
    e.stopPropagation();
    const success = await copyToClipboard(trackNumber);
    if (success) {
      setCopiedId(orderId);
      setTimeout(() => setCopiedId(null), 2000);
    }
  };

  const isStatusActive = (status) => {
    const statusOrder = ['ASSEMBLING', 'ONTHEWAY', 'ATTHEPOINT', 'DELIVERED'];
    const currentIndex = statusOrder.indexOf(order.status);
    const checkIndex = statusOrder.indexOf(status);
    return checkIndex <= currentIndex;
  };

  return (
    <div className={`order-modal ${closing ? 'order-modal--closing' : ''}`} onClick={handleClose}>
      <div
        className={`order-modal__content ${closing ? 'order-modal__content--closing' : ''}`}
        onClick={(e) => e.stopPropagation()}
        onAnimationEnd={onAnimationEnd}
      >
        <div className="order-modal__scrollable">
          <div className="order-modal__carousel" ref={carouselRef}>
            {photos.map((photo, i) => (
              <div
                key={i}
                className={`order-modal__slide ${i === slideIndex ? 'order-modal__slide--active' : 'order-modal__slide--hidden'}`}
              >
                <img src={photo} alt={`${order.name} ${i + 1}`} className="order-modal__image" />
              </div>
            ))}

            {photos.length > 1 && (
              <div className="order-modal__dots">
                {photos.map((_, i) => (
                  <span
                    key={i}
                    className={`order-modal__dot ${i === slideIndex ? 'order-modal__dot--active' : ''}`}
                    onClick={() => goToSlide(i)}
                  />
                ))}
              </div>
            )}
          </div>

          <h2 className="order-modal__title">{order.name}</h2>
          <p className="order-modal__price">Итоговая сумма: {order.price}₽</p>
          <p className="order-modal__date">Дата заказа: {formatDate(order.order_date)}</p>

          {(order.track_code) && (
            <div className="order-modal__track">
              <strong>Номер заказа:</strong>
              <button
                className={`order-modal__track-btn ${copiedId === order.id ? 'order-modal__track-btn--copied' : ''}`}
                onClick={(e) => handleCopyTrackNumber(order.track_code, order.id, e)}
                title="Нажмите, чтобы скопировать"
              >
                {copiedId === order.id ? (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    fill="currentColor"
                    viewBox="0 0 16 16"
                  >
                    <path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z" />
                  </svg>
                ) : (
                  <span>{order.cdek_number || order.track_code}</span>
                )}
              </button>
            </div>
          )}

          <div className="order-modal__status-section">
            <h3 className="order-modal__section-title">Статус заказа</h3>
            <div className="order-modal__timeline">
              <div className={`order-modal__status ${isStatusActive('ASSEMBLING') ? 'order-modal__status--active' : ''}`}>
                <div className="order-modal__status-dot"></div>
                <span className="order-modal__status-label">Собирается</span>
              </div>

              <div className="order-modal__status-line"></div>

              <div className={`order-modal__status ${isStatusActive('ONTHEWAY') ? 'order-modal__status--active' : ''}`}>
                <div className="order-modal__status-dot"></div>
                <span className="order-modal__status-label">В пути</span>
              </div>

              <div className="order-modal__status-line"></div>

              <div className={`order-modal__status ${isStatusActive('DELIVERED') ? 'order-modal__status--active' : ''}`}>
                <div className="order-modal__status-dot"></div>
                <span className="order-modal__status-label">Доставлено</span>
              </div>
            </div>
          </div>

          <div className="order-modal__delivery-section">
            <h3 className="order-modal__section-title">Информация о доставке</h3>

            <div className="order-modal__info-card">
              <div className="order-modal__info-icon">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M10 2C6.13 2 3 5.13 3 9c0 5.25 7 11 7 11s7-5.75 7-11c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" fill="currentColor"/>
                </svg>
              </div>
              <div className="order-modal__info-content">
                <span className="order-modal__info-label">Пункт сборки заказа</span>
                <span className="order-modal__info-value">Москва, Тестовый адрес</span>
              </div>
            </div>

            {order.delivery_address && (
              <div className="order-modal__info-card">
                <div className="order-modal__info-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                    <path fillRule="evenodd" d="M4 4a4 4 0 1 1 4.5 3.969V13.5a.5.5 0 0 1-1 0V7.97A4 4 0 0 1 4 3.999zm2.493 8.574a.5.5 0 0 1-.411.575c-.712.118-1.28.295-1.655.493a1.3 1.3 0 0 0-.37.265.3.3 0 0 0-.057.09V14l.002.008.016.033a.6.6 0 0 0 .145.15c.165.13.435.27.813.395.751.25 1.82.414 3.024.414s2.273-.163 3.024-.414c.378-.126.648-.265.813-.395a.6.6 0 0 0 .146-.15l.015-.033L12 14v-.004a.3.3 0 0 0-.057-.09 1.3 1.3 0 0 0-.37-.264c-.376-.198-.943-.375-1.655-.493a.5.5 0 1 1 .164-.986c.77.127 1.452.328 1.957.594C12.5 13 13 13.4 13 14c0 .426-.26.752-.544.977-.29.228-.68.413-1.116.558-.878.293-2.059.465-3.34.465s-2.462-.172-3.34-.465c-.436-.145-.826-.33-1.116-.558C3.26 14.752 3 14.426 3 14c0-.599.5-1 .961-1.243.505-.266 1.187-.467 1.957-.594a.5.5 0 0 1 .575.411"/>
                  </svg>
                </div>
                <div className="order-modal__info-content">
                  <span className="order-modal__info-label">Пункт назначения</span>
                  <span className="order-modal__info-value">Москва, Тестовый адрес</span>
                </div>
              </div>
            )}
          </div>

          {order.order_items && order.order_items.length > 0 && (
            <div className="order-modal__reviews-section">
              <h3 className="order-modal__section-title">Товары в заказе</h3>

              {order.order_items.map((item) => {
                const itemState = reviewStates[item.id] || { hasReview: false, submitting: false };
                const isActiveForm = activeReviewItem === item.id;

                return (
                  <div key={item.id} className="order-modal__item-card">
                    <div className="order-modal__item-header">
                      {item.product_info?.photo1 && (
                        <img
                          src={item.product_info.photo1}
                          alt={item.product_info.name}
                          className="order-modal__item-image"
                        />
                      )}
                      <div className="order-modal__item-info">
                        <h4 className="order-modal__item-name">{item.product_info?.name || 'Товар'}</h4>
                        <p className="order-modal__item-details">
                          {item.quantity} шт. × {item.price}₽
                        </p>
                      </div>
                    </div>

                    {!itemState.hasReview ? (
                      isActiveForm ? (
                        <div className="order-modal__review-form">
                          <div className="order-modal__stars">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <button
                                key={star}
                                className={`order-modal__star ${reviewStars >= star ? 'order-modal__star--active' : ''}`}
                                onClick={() => setReviewStars(star)}
                              >
                                ★
                              </button>
                            ))}
                          </div>

                          <textarea
                            className="order-modal__textarea"
                            placeholder="Расскажите о своих впечатлениях..."
                            value={reviewText}
                            onChange={(e) => setReviewText(e.target.value)}
                            rows={4}
                            maxLength={500}
                          />
                          <div className="order-modal__char-count">{reviewText.length}/500</div>

                          <div className="order-modal__review-actions">
                            <button
                              className="order-modal__review-btn order-modal__review-btn--cancel"
                              onClick={() => {
                                setActiveReviewItem(null);
                                setReviewText('');
                                setReviewStars(5);
                              }}
                            >
                              Отмена
                            </button>
                            <button
                              className="order-modal__review-btn order-modal__review-btn--submit"
                              onClick={() => handleSubmitReview(item.id, item.product)}
                              disabled={itemState.submitting}
                            >
                              {itemState.submitting ? 'Отправка...' : 'Отправить'}
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button
                          className="order-modal__write-review-btn"
                          onClick={() => setActiveReviewItem(item.id)}
                        >
                          Написать отзыв
                        </button>
                      )
                    ) : (
                      <div className="order-modal__review-submitted">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                          <path d="M13 4L6 11L3 8" stroke="var(--primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        <span>Отзыв оставлен</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="order-modal__actions">
          <button className="order-modal__action-btn order-modal__action-btn--return" onClick={handleClose}>
            Вернуть заказ
          </button>
          <button className="order-modal__action-btn order-modal__action-btn--confirm" onClick={handleClose}>
            Хорошо
          </button>
        </div>
      </div>
    </div>
  );
};

export default OrderModal;
