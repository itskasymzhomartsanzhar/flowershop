import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import useCart from '../../hooks/useCart';
import './PaymentSuccess.scss';

const PaymentSuccess = ({ onClose, orderNumber: propsOrderNumber }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [showCheckmark, setShowCheckmark] = useState(false);
  const [orderNumber, setOrderNumber] = useState('');
  const { clearCart } = useCart();

  useEffect(() => {
    if (propsOrderNumber) {
      setOrderNumber(propsOrderNumber);
    } else {
      const orderNum = searchParams.get('order');
      const paymentId = searchParams.get('payment_id');

      if (orderNum) {
        setOrderNumber(orderNum);
      } else if (paymentId) {
        setOrderNumber(paymentId.slice(0, 8).toUpperCase());
      }
    }

    clearCart();

    setTimeout(() => {
      setShowCheckmark(true);
    }, 300);

    const closeTimer = setTimeout(() => {
      if (onClose) {
        onClose();
      } else {
        navigate('/profile');
      }
    }, 25000);

    return () => clearTimeout(closeTimer);
  }, [searchParams, navigate, onClose, propsOrderNumber]);

  return (
    <div className="payment-success">
      <div className="payment-success__container">
        <div className={`checkmark-wrapper ${showCheckmark ? 'show' : ''}`}>
          <div className="checkmark-circle">
            <svg
              className="checkmark"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 52 52"
            >
              <circle
                className="checkmark-circle-path"
                cx="26"
                cy="26"
                r="25"
                fill="none"
              />
              <path
                className="checkmark-check"
                fill="none"
                d="M14.1 27.2l7.1 7.2 16.7-16.8"
              />
            </svg>
          </div>
        </div>

        <h1 className="payment-success__title">Оплата успешно прошла!</h1>

        <p className="payment-success__message">
          Ваш заказ #{orderNumber || 'XXXXXX'} уже передан в обработку.
        </p>

        <div className="payment-success__info">
          <div className="info-item">
            <svg
              className="info-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>Заказ принят в обработку</span>
          </div>

          <div className="info-item">
            <svg
              className="info-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
              />
            </svg>
            <span>Скоро начнем подготовку к отправке</span>
          </div>

          <div className="info-item">
            <svg
              className="info-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>
            <span>Вы получите уведомление о статусе</span>
          </div>
        </div>

        <div className="payment-success__actions">

          <button
            className="btn btn-primary"
            onClick={() => {
              if (onClose) onClose();
              navigate('/');
            }}
          >
            На главную
          </button>
        </div>

        <p className="payment-success__redirect">
          Автоматический переход через 25 секунд...
        </p>
      </div>
    </div>
  );
};

export default PaymentSuccess;
