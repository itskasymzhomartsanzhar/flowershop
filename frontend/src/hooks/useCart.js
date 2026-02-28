import { useState, useEffect } from 'react';
import API_ENDPOINTS from '../utils/api';
import getTelegramHeaders from '../utils/telegramHeaders';
import { CART_UPDATED_EVENT, emitCartUpdated } from '../utils/cartEvents';

export const useCart = () => {
  const [products, setProducts] = useState([]);
  const [counts, setCounts] = useState({});
  const [summary, setSummary] = useState({
    items_count: 0,
    subtotal: 0,
    service_fee_percent: 0,
    service_fee_amount: 0,
    discount_percent: 0,
    discount_amount: 0,
    total: 0,
  });

  useEffect(() => {
    fetchCart();
  }, []);

  useEffect(() => {
    const handleCartUpdated = () => {
      fetchCart();
    };
    window.addEventListener(CART_UPDATED_EVENT, handleCartUpdated);
    return () => window.removeEventListener(CART_UPDATED_EVENT, handleCartUpdated);
  }, []);

  const fetchCart = () => {
    fetch(API_ENDPOINTS.CART.GET, {
      method: 'GET',
      headers: getTelegramHeaders(),
    })
      .then((res) => res.json())
      .then((data) => {
        const cartItems = data.cart || [];
        const cartSummary = data.summary || {
          items_count: 0,
          subtotal: 0,
          service_fee_percent: 0,
          service_fee_amount: 0,
          discount_percent: 0,
          discount_amount: 0,
          total: 0,
        };
        const initialCounts = {};

        cartItems.forEach((item) => {
          initialCounts[item.id] = item.quantity;
        });

        setProducts(cartItems);
        setCounts(initialCounts);
        setSummary(cartSummary);
      })
      .catch((err) => console.error('Ошибка при получении корзины:', err));
  };

  const updateCartQuantity = (productId, quantity) => {
    fetch(API_ENDPOINTS.CART.UPDATE, {
      method: 'POST',
      headers: getTelegramHeaders(),
      body: JSON.stringify({
        product_id: productId,
        quantity: quantity,
      }),
    })
      .then(() => fetchCart())
      .then(() => emitCartUpdated())
      .catch((err) => console.error('Ошибка при обновлении корзины:', err));
  };

  const removeFromCart = (productId) => {
    fetch(API_ENDPOINTS.CART.REMOVE, {
      method: 'POST',
      headers: getTelegramHeaders(),
      body: JSON.stringify({ product_id: productId }),
    })
      .then(() => fetchCart())
      .then(() => emitCartUpdated())
      .catch((err) => console.error('Ошибка при удалении из корзины:', err));
  };

  const increment = (id) => {
    setCounts((prev) => {
      const product = products.find((item) => item.id === id);
      const step = Math.max(1, Number(product?.quantity_step || 1));
      const newCount = (prev[id] || 0) + step;
      updateCartQuantity(id, newCount);
      return { ...prev, [id]: newCount };
    });
  };

  const decrement = (id) => {
    setCounts((prev) => {
      const product = products.find((item) => item.id === id);
      const step = Math.max(1, Number(product?.quantity_step || 1));
      const current = prev[id] || 1;
      const newCount = current - step;

      if (newCount <= 0) {
        const updatedCounts = { ...prev };
        delete updatedCounts[id];
        removeFromCart(id);
        return updatedCounts;
      } else {
        updateCartQuantity(id, newCount);
        return { ...prev, [id]: newCount };
      }
    });
  };

  const calculateTotalPrice = () => {
    return summary.total;
  };

  const clearCart = () => {
    setCounts({});
    setProducts([]);
    setSummary({
      items_count: 0,
      subtotal: 0,
      service_fee_percent: 0,
      service_fee_amount: 0,
      discount_percent: 0,
      discount_amount: 0,
      total: 0,
    });
    fetch(API_ENDPOINTS.CART.CLEAR, {
      method: 'POST',
      headers: getTelegramHeaders(),
    })
      .then(() => fetchCart())
      .then(() => emitCartUpdated())
      .catch((err) => console.error('Ошибка при очистке корзины:', err));
  };

  return {
    products,
    counts,
    increment,
    decrement,
    calculateTotalPrice,
    clearCart,
    summary,
    refreshCart: fetchCart,
  };
};

export default useCart;
