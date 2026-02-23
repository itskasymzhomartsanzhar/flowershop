import './CartItems.scss';
import { Link } from 'react-router-dom';
import useCart from '../../hooks/useCart';

const CartItems = () => {
  const { products, counts, increment, decrement, calculateTotalPrice, clearCart, summary } = useCart();

  const itemsCount = Object.keys(counts).length;
  const totalPrice = calculateTotalPrice();
  const serviceFee = summary.service_fee_amount || 0;
  const serviceFeePercent = summary.service_fee_percent || 0;

  const goods = products
    .filter((product) => counts[product.id])
    .map((product) => ({
      id: product.id,
      name: product.name,
      price: product.price,
      quantity: counts[product.id]
    }));

  return (
    <>
      <div className="progress">
        <div className="progress__bar progress__bar--half"></div>
      </div>

      <div className="cart__header">
        <h3>Корзина: {itemsCount} товара</h3>
        <button className="cart__clear-btn" onClick={clearCart}>Очистить</button>
      </div>

      <div className="cart__items">
        {products
          .filter((product) => counts[product.id])
          .map((product) => (
            <div className="cart__card" key={product.id}>
              <img src={product.photo} alt={product.name} className="cart__image" />
              <div className="cart__info">
                <h3 className="cart__title">{product.name}</h3>
                <p className="cart__price">{product.price}₽</p>
              </div>

              <div className="cart__counter">
                <button onClick={() => decrement(product.id)} className="cart__counter-btn">−</button>
                <span className="cart__counter-value">{counts[product.id]}</span>
                <button onClick={() => increment(product.id)} className="cart__counter-btn">+</button>
              </div>
            </div>
          ))}
      </div>

      {itemsCount > 0 && (
        <Link to="/confirm" state={{ total: totalPrice, goods }}>
          <div className="cart__footer">
            {serviceFee > 0 && (
              <div className="cart__fee-row">
                <span>Сервисный сбор ({serviceFeePercent}%)</span>
                <span>{serviceFee}₽</span>
              </div>
            )}
            <button className="cart__checkout-btn">
              Оформить заказ ({totalPrice}₽)
            </button>
          </div>
        </Link>
      )}
    </>
  );
};

export default CartItems;
