import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import getTelegramHeaders from '../../utils/telegramHeaders';
import API_ENDPOINTS from '../../utils/api';
import formatPrice from '../../utils/formatPrice';
import './Confirm.scss';

const PICKUP_ADDRESS = 'ул. Пушкина, дом 1';

const Confirm = () => {
  const location = useLocation();
  const initialTotal = location.state?.total || 0;
  const [baseTotal, setBaseTotal] = useState(initialTotal);
  const [finalTotal, setFinalTotal] = useState(initialTotal);

  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [isPickup, setIsPickup] = useState(false);
  const [isRecipientSelf, setIsRecipientSelf] = useState(true);
  const [recipientName, setRecipientName] = useState('');
  const [recipientPhone, setRecipientPhone] = useState('');
  const [comment, setComment] = useState('');
  const [promocode, setPromocode] = useState('');
  const [toast, setToast] = useState('');
  const [discount, setDiscount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [paymentRequested, setPaymentRequested] = useState(false);
  const [deliveryOptions, setDeliveryOptions] = useState({
    min_date: '',
    max_date: '',
    time_slots: [],
    default_time_slot: '',
  });
  const [deliveryDate, setDeliveryDate] = useState('');
  const [deliveryTimeSlot, setDeliveryTimeSlot] = useState('');
  const [addressSuggestions, setAddressSuggestions] = useState([]);
  const [isAddressSuggestionsLoading, setIsAddressSuggestionsLoading] = useState(false);
  const [isAddressInputFocused, setIsAddressInputFocused] = useState(false);
  const addressSuggestRef = useRef(null);

  const formatIsoDate = (iso) => {
    if (!iso) return '';
    const [year, month, day] = iso.split('-');
    if (!year || !month || !day) return iso;
    return `${day}.${month}.${year}`;
  };

  const isDeliveryDateOutOfRange = () => {
    if (!deliveryDate || !deliveryOptions.min_date || !deliveryOptions.max_date) return false;
    return deliveryDate < deliveryOptions.min_date || deliveryDate > deliveryOptions.max_date;
  };

  const deliveryRangeHint = deliveryOptions.min_date && deliveryOptions.max_date
    ? `Срок доставки: от ${formatIsoDate(deliveryOptions.min_date)} до ${formatIsoDate(deliveryOptions.max_date)}`
    : '';

  const deliveryValidationError = !isPickup && isDeliveryDateOutOfRange()
    ? `Выберите дату в диапазоне ${formatIsoDate(deliveryOptions.min_date)} - ${formatIsoDate(deliveryOptions.max_date)}`
    : '';

  const canSubmit = phone && (
    isPickup || (
      !!address &&
      !!deliveryDate &&
      !!deliveryTimeSlot &&
      !isDeliveryDateOutOfRange()
    )
  ) && (
    isRecipientSelf || (!!recipientName.trim() && !!recipientPhone.trim())
  );

  const showToast = (message) => {
    setToast(message);
    setTimeout(() => setToast(''), 3000);
  };

  const handlePhoneChange = (value) => setPhone(value);

  useEffect(() => {
    fetch(API_ENDPOINTS.CART.GET, {
      method: 'GET',
      headers: getTelegramHeaders(),
    })
      .then((res) => res.json())
      .then((data) => {
        const cartTotal = data?.summary?.total || 0;
        setBaseTotal(cartTotal);
        setFinalTotal(cartTotal);
      })
      .catch(() => {
        setBaseTotal(initialTotal);
        setFinalTotal(initialTotal);
      });
  }, [initialTotal]);

  useEffect(() => {
    fetch(API_ENDPOINTS.DELIVERY.OPTIONS, {
      method: 'GET',
      headers: getTelegramHeaders(),
    })
      .then((res) => res.json())
      .then((data) => {
        const minDate = data?.min_date || '';
        const maxDate = data?.max_date || '';
        const slots = Array.isArray(data?.time_slots) ? data.time_slots : [];
        const defaultSlot = data?.default_time_slot || slots[0] || '';
        setDeliveryOptions({
          min_date: minDate,
          max_date: maxDate,
          time_slots: slots,
          default_time_slot: defaultSlot,
        });
        if (!deliveryDate && minDate) {
          setDeliveryDate(minDate);
        }
        if (!deliveryTimeSlot && defaultSlot) {
          setDeliveryTimeSlot(defaultSlot);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (isPickup) {
      setAddressSuggestions([]);
      setIsAddressSuggestionsLoading(false);
      return;
    }

    const query = address.trim();
    if (query.length < 3) {
      setAddressSuggestions([]);
      setIsAddressSuggestionsLoading(false);
      return;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(async () => {
      try {
        setIsAddressSuggestionsLoading(true);
        const url = `${API_ENDPOINTS.DELIVERY.SUGGEST}?q=${encodeURIComponent(query)}&count=8`;
        const response = await fetch(url, {
          method: 'GET',
          headers: getTelegramHeaders(),
          signal: controller.signal,
        });
        if (!response.ok) {
          setAddressSuggestions([]);
          return;
        }
        const data = await response.json();
        const suggestions = Array.isArray(data?.suggestions) ? data.suggestions : [];
        setAddressSuggestions(suggestions);
      } catch (error) {
        if (error?.name !== 'AbortError') {
          setAddressSuggestions([]);
        }
      } finally {
        setIsAddressSuggestionsLoading(false);
      }
    }, 350);

    return () => {
      controller.abort();
      clearTimeout(timeoutId);
    };
  }, [address, isPickup]);

  useEffect(() => {
    const handleOutsideClick = (event) => {
      if (!addressSuggestRef.current?.contains(event.target)) {
        setIsAddressInputFocused(false);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  // Валидация промокода
  useEffect(() => {
    const validatePromocode = async () => {
      const trimmedPromo = promocode.trim();
      if (trimmedPromo === '') {
        setDiscount(0);
        setFinalTotal(baseTotal);
        return;
      }
      try {
        const res = await fetch(API_ENDPOINTS.PROMOCODE.APPLY, {
          method: 'POST',
          headers: getTelegramHeaders(),
          body: JSON.stringify({ promocode: trimmedPromo }),
        });
        const data = await res.json();
        if (res.ok && data.success) {
          setDiscount(data.discount / 100);
          setFinalTotal(data?.summary?.total ?? baseTotal);
        } else {
          setDiscount(0);
          setFinalTotal(baseTotal);
        }
      } catch {
        setDiscount(0);
        setFinalTotal(baseTotal);
      }
    };
    const timeoutId = setTimeout(validatePromocode, 500);
    return () => clearTimeout(timeoutId);
  }, [promocode, baseTotal]);

  const handlePayment = async () => {
    if (paymentRequested) {
      return;
    }

    if (!phone || (!isPickup && !address)) {
      showToast('Пожалуйста, заполните номер и адрес');
      return;
    }
    if (!isRecipientSelf && (!recipientName.trim() || !recipientPhone.trim())) {
      showToast('Укажите имя и телефон получателя');
      return;
    }
    if (!isPickup && (!deliveryDate || !deliveryTimeSlot)) {
      showToast('Выберите дату и время доставки');
      return;
    }
    if (!isPickup && isDeliveryDateOutOfRange()) {
      showToast('Дата доставки вне допустимого диапазона');
      return;
    }


    try {
      setLoading(true);

      const res = await fetch(API_ENDPOINTS.PAYMENT.CREATE, {
        method: 'POST',
        headers: getTelegramHeaders(),
        body: JSON.stringify({
          phone,
          address: isPickup ? PICKUP_ADDRESS : address,
          is_pickup: isPickup,
          is_recipient_self: isRecipientSelf,
          recipient_name: isRecipientSelf ? '' : recipientName.trim(),
          recipient_phone: isRecipientSelf ? phone : recipientPhone.trim(),
          comment,
          promocode: promocode.trim(),
          delivery_date: isPickup ? null : deliveryDate,
          delivery_time_slot: isPickup ? '' : deliveryTimeSlot,
        }),
      });


      if (!res.ok) {
        const errorText = await res.text();
        console.error('❌ Ошибка HTTP:', res.status, errorText);
        throw new Error(`Ошибка сервера: ${res.status}`);
      }

      const data = await res.json();
      console.log('📝 Ответ от сервера:', data);

      if (!data.payment_id || !data.payment_url_sent) {
        console.error('❌ Нет payment_id или отправки ссылки:', data);
        showToast('Не удалось отправить ссылку на оплату');
        setLoading(false);
        return;
      }

      setPaymentRequested(true);
      showToast('Ссылка на оплату отправлена в Telegram-бот');
      setLoading(false);
    } catch (err) {
      console.error('❌ Критическая ошибка при оплате:', err);

      if (err.name === 'AbortError') {
        showToast('Превышено время ожидания. Попробуйте еще раз.');
      } else if (err.message.includes('NetworkError') || err.message.includes('Failed to fetch')) {
        showToast('Ошибка сети. Проверьте подключение к интернету.');
      } else {
        showToast('Ошибка при инициализации платежа: ' + err.message);
      }
      setLoading(false);
    }
  };

  return (
    <>
      {toast && <div className="toast">{toast}</div>}

      <div className="progress">
        <div className="progress__bar progress__bar--full"></div>
      </div>

      <div className="form">
        <h2 className="form__title">Заказ почти оформлен</h2>

        <input
          type="tel"
          placeholder="Номер телефона (+7 или 8)"
          className="form__input"
          maxLength={20}
          minLength={7}
          required
          value={phone}
          onChange={(e) => handlePhoneChange(e.target.value)}
        />


        <label className={`pickup recipient ${isRecipientSelf ? 'pickup--active' : ''}`}>
          <input
            className="pickup__input"
            type="checkbox"
            checked={isRecipientSelf}
            onChange={(e) => {
              const checked = e.target.checked;
              setIsRecipientSelf(checked);
              if (checked) {
                setRecipientName('');
                setRecipientPhone('');
              } else {
                setRecipientPhone(phone);
              }
            }}
          />
          <div className="pickup__content">
            <div className="pickup__title-row">
              <div className="pickup__title-wrap">
                <span className="pickup__title">Я являюсь получателем</span>
              </div>
              <span className="pickup__switch" aria-hidden="true">
                <span className="pickup__switch-knob"></span>
              </span>
            </div>
            <p className="pickup__hint">Снимите галочку, если заказ получает другой человек</p>
          </div>
        </label>

        {!isRecipientSelf && (
          <div className="recipient__fields">
            <input
              type="text"
              placeholder="Имя получателя"
              className="form__input"
              maxLength={255}
              value={recipientName}
              onChange={(e) => setRecipientName(e.target.value)}
            />
            <input
              type="tel"
              placeholder="Телефон получателя (+7 или 8)"
              className="form__input"
              maxLength={20}
              value={recipientPhone}
              onChange={(e) => setRecipientPhone(e.target.value)}
            />
          </div>
        )}
        <label className={`pickup ${isPickup ? 'pickup--active' : ''}`}>
          <input
            className="pickup__input"
            type="checkbox"
            checked={isPickup}
            onChange={(e) => setIsPickup(e.target.checked)}
          />
          <div className="pickup__content">
            <div className="pickup__title-row">
              <div className="pickup__title-wrap">
                <span className="pickup__title">Самовывоз</span>
              </div>
              <span className="pickup__switch" aria-hidden="true">
                <span className="pickup__switch-knob"></span>
              </span>
            </div>
            <p className="pickup__hint">Забрать заказ самостоятельно из пункта выдачи</p>
          </div>
        </label>
        {isPickup ? (
          <div className="pickup__address">
            <span className="pickup__address-label">Пункт самовывоза</span>
            <span className="pickup__address-value">{PICKUP_ADDRESS}</span>
          </div>
        ) : (
          <div className="address-suggest" ref={addressSuggestRef}>
            <input
              type="text"
              placeholder="Адрес доставки"
              className="form__input"
              maxLength={250}
              minLength={3}
              required
              autoComplete="off"
              value={address}
              onFocus={() => setIsAddressInputFocused(true)}
              onChange={(e) => {
                setAddress(e.target.value);
                setIsAddressInputFocused(true);
              }}
            />
            {isAddressInputFocused && (addressSuggestions.length > 0 || isAddressSuggestionsLoading) && (
              <div className="address-suggest__dropdown">
                {isAddressSuggestionsLoading && (
                  <div className="address-suggest__loading">Ищем улицы и дома...</div>
                )}
                {!isAddressSuggestionsLoading && addressSuggestions.map((item, index) => (
                  <button
                    key={`${item.unrestricted_value || item.value || 'suggestion'}-${index}`}
                    type="button"
                    className="address-suggest__item"
                    onClick={() => {
                      setAddress(item.value || item.unrestricted_value || '');
                      setAddressSuggestions([]);
                      setIsAddressInputFocused(false);
                    }}
                  >
                    <span className="address-suggest__main">{item.value}</span>
                    {(item.city || item.region) && (
                      <span className="address-suggest__meta">
                        {[item.city, item.region].filter(Boolean).join(', ')}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {!isPickup && (
          <div className="delivery">
            <div className="delivery__title">Отложенная доставка</div>
            {deliveryRangeHint && (
              <div className="delivery__hint">{deliveryRangeHint}</div>
            )}
            <div className="delivery__grid">
              <div className="delivery__field">
                <label className="delivery__label">Дата</label>
                <input
                  type="date"
                  className="form__input delivery__input"
                  value={deliveryDate}
                  min={deliveryOptions.min_date || undefined}
                  max={deliveryOptions.max_date || undefined}
                  onChange={(e) => setDeliveryDate(e.target.value)}
                  required
                />
              </div>
              <div className="delivery__field">
                <label className="delivery__label">Время</label>
                <select
                  className="form__input delivery__input"
                  value={deliveryTimeSlot}
                  onChange={(e) => setDeliveryTimeSlot(e.target.value)}
                  required
                >
                  {deliveryOptions.time_slots.map((slot) => (
                    <option key={slot} value={slot}>{slot}</option>
                  ))}
                </select>
              </div>
            </div>
            {deliveryValidationError && (
              <div className="delivery__error">{deliveryValidationError}</div>
            )}
          </div>
        )}

        <textarea
          placeholder="Комментарий (необязательно)"
          className="form__input"
          rows="2"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        ></textarea>

        <div className="promocode__wrapper">
          <input
            type="text"
            placeholder="Есть промокод?"
            className="form__input"
            maxLength={20}
            value={promocode}
            onChange={(e) => setPromocode(e.target.value)}
          />
          {discount > 0 && (
            <span className="promocode__badge">−{Math.round(discount * 100)}%</span>
          )}
        </div>

      </div>

      <div className="checkout">
        <button
          className="checkout__btn"
          onClick={handlePayment}
          disabled={loading || paymentRequested || !canSubmit}
        >
          {loading ? 'Обработка...' : paymentRequested ? 'Проверьте сообщения в боте' : `Оплатить через ЮKassa (${formatPrice(finalTotal)}₽)`}
        </button>
      </div>
    </>
  );
};

export default Confirm;
