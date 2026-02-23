import React, { useEffect, useState } from 'react';
import { Routes, Route, useLocation, useSearchParams, useNavigate } from 'react-router-dom';
import Home from './pages/Home';
import Cart from './pages/Cart';
import Profile from './pages/Profile';
import ConfirmPage from './pages/ConfirmPage';
import FavoritePage from './pages/FavoritePage';
import Search from './pages/Search';
import PaymentSuccess from './components/PaymentSuccess/PaymentSuccess';
import getTelegramHeaders from './utils/telegramHeaders';
import { API_BASE_URL } from './utils/api';

import Menu from './components/Menu/Menu';
import Preloader from './components/Preloader/Preloader';

const App = () => {
  const [loading, setLoading] = useState(false);
  const [showPaymentSuccess, setShowPaymentSuccess] = useState(false);
  const [orderNumber, setOrderNumber] = useState('');
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
useEffect(() => {
  if (showPaymentSuccess) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }

  return () => {
    document.body.style.overflow = '';
  };
}, [showPaymentSuccess]);

  useEffect(() => {
    const paymentId = searchParams.get('payment_id');
    if (paymentId) {
      console.log('🔄 Обнаружен payment_id, проверяем статус:', paymentId);

      const checkPaymentStatus = async () => {
        try {
          const res = await fetch(`${API_BASE_URL}/users/check_payment_status/`, {
            method: 'POST',
            headers: getTelegramHeaders(),
            body: JSON.stringify({ payment_id: paymentId }),
          });

          if (!res.ok) {
            console.error('❌ Ошибка HTTP при проверке статуса:', res.status);
            return;
          }

          const data = await res.json();
          console.log('📊 Статус платежа:', data);

          if (data.status === 'succeeded') {
            const order = data.track_number || data.order_id || paymentId.slice(0, 8).toUpperCase();
            setOrderNumber(order);
            setShowPaymentSuccess(true);

            // Убираем payment_id из URL
            navigate(location.pathname, { replace: true });
          }
        } catch (err) {
          console.error('Ошибка проверки статуса:', err);
        }
      };

      checkPaymentStatus();
    }
  }, [searchParams, navigate, location.pathname]);

  useEffect(() => {
    const images = Array.from(document.images);
    const unloaded = images.filter(img => !img.complete);

    if (unloaded.length === 0) {
      setLoading(false);
      return;
    }

    setLoading(true);
    let loaded = 0;

    unloaded.forEach(img => {
      const onLoadOrError = () => {
        loaded++;
        if (loaded === unloaded.length) {
          setLoading(false);
        }
      };
      img.onload = onLoadOrError;
      img.onerror = onLoadOrError;
    });
  }, [location]); 

  return (
    <>
      {loading && <Preloader />}
      {showPaymentSuccess && (
        <PaymentSuccess
          onClose={() => setShowPaymentSuccess(false)}
          orderNumber={orderNumber}
        />
      )}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/confirm" element={<ConfirmPage />} />
        <Route path="/favorite" element={<FavoritePage />} />
        <Route path="/search" element={<Search />} />
        <Route path="/payment-success" element={<PaymentSuccess />} />

      </Routes>
      <Menu />
    </>
  );
};

export default App;
