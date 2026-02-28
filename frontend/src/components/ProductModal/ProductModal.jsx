import { useState, useEffect } from 'react';
import useCarousel from '../../hooks/useCarousel';
import './ProductModal.scss';
import formatPrice from '../../utils/formatPrice';

const ProductModalCarousel = ({ product, onClose, onAddToCart, source = 'catalog' }) => {
  const photos = [];
  for (let i = 1; i <= 10; i++) {
    const photoKey = `photo${i}`;
    if (product[photoKey]) photos.push(product[photoKey]);
  }

  const [closing, setClosing] = useState(false);
  const quantityStep = Math.max(1, Number(product.quantity_step || 1));
  const [quantity, setQuantity] = useState(quantityStep);
  const { slideIndex, carouselRef, goToSlide } = useCarousel(photos.length);
  const isOutOfStock = product.in_stock === 0;

  const handleClose = () => setClosing(true);
  const onAnimationEnd = () => {
    if (closing) onClose();
  };

useEffect(() => {
  document.body.style.overflow = 'hidden';

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
  }

  return () => {
    document.body.style.overflow = '';
  };
}, []);


const handleAddToCart = () => {
    if (isOutOfStock) return;
    if (onAddToCart) onAddToCart(product, quantity);
    handleClose();
  };

  const incrementQuantity = () => {
    setQuantity((prev) => prev + quantityStep);
  };

  const decrementQuantity = () => {
    setQuantity((prev) => Math.max(quantityStep, prev - quantityStep));
  };

  const renderStars = (count) => '★'.repeat(count) + '☆'.repeat(5 - count);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const months = [
      'января','февраля','марта','апреля','мая','июня',
      'июля','августа','сентября','октября','ноября','декабря',
    ];
    return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
  };

  return (
    <div className={`modal__overlay ${closing ? 'modal__overlay--closing' : ''}`} onClick={handleClose}>
      <div
        style={{ position: 'relative', userSelect: 'none' }}
        className={`carousel modal__container ${closing ? 'modal__container--slide-down' : 'modal__container--slide-up'}`}
        onClick={(e) => e.stopPropagation()}
        ref={carouselRef}
        onAnimationEnd={onAnimationEnd}
      >
        <div className="modal__scrollable">
          <div className="carousel" ref={carouselRef}>
            {photos.map((photo, i) => (
              <div
                key={i}
                className="carousel__slide"
                style={{ display: i === slideIndex ? 'block' : 'none', transition: 'transform 0.3s ease' }}
              >
                <img src={photo} alt={`${product.name} ${i + 1}`} className="modal__image" style={{ width: '100%', pointerEvents: 'none', userSelect: 'none' }} />
              </div>
            ))}

            {photos.length > 1 && (
              <div className="carousel__dots">
                {photos.map((_, i) => (
                  <span
                    key={i}
                    className={`carousel__dot${i === slideIndex ? ' carousel__dot--active' : ''}`}
                    onClick={() => goToSlide(i)}
                  />
                ))}
              </div>
            )}

            {(product.flug_new || product.flug_popular || isOutOfStock) && (
              <div className="tags__container">
                {product.flug_new && <span className="tag tag--new">Новинка</span>}
                {product.flug_popular && <span className="tag tag--popular">Популярное</span>}
                {isOutOfStock && <span className="tag tag--out-of-stock">Нет в наличии</span>}
              </div>
            )}
          </div>

          <h2 className="modal__title">{product.name}</h2>
          <p className="modal__description">{product.description}</p>

          {product.reviews && product.reviews.length > 0 && (
            <div className="reviews__wrapper">
              <div className="reviews__header">
                <h1>Отзывы о товаре</h1>
                <span className="reviews__rating">
                  <span className="reviews__stars">★</span> {product.average_rating.toFixed(1)} ({product.reviews_count})
                </span>
              </div>
              <div className="reviews__list">
                {product.reviews.map((review) => (
                  <div className="review" key={review.id}>
                    <div className="review__content">
                      <h3>{review.name}</h3>
                      <p>{review.text}</p>
                    </div>
                    <div className="review__info">
                      <span className="review__stars">{renderStars(review.stars)}</span>
                      <span className="review__date">{formatDate(review.time)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {!isOutOfStock && (
          <div className="modal__qty">
            <button className="modal__qty-btn" onClick={decrementQuantity}>−</button>
            <span className="modal__qty-value">{quantity}</span>
            <button className="modal__qty-btn" onClick={incrementQuantity}>+</button>
          </div>
        )}

        <button className={`modal__add-btn ${isOutOfStock ? 'modal__add-btn--disabled' : ''}`} onClick={handleAddToCart} disabled={isOutOfStock}>
          {isOutOfStock ? 'Нет в наличии' : `Добавить в корзину (${formatPrice(product.price * quantity)}₽)`}
        </button>
      </div>
    </div>
  );
};

export default ProductModalCarousel;
