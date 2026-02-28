import { useEffect, useState, useCallback } from 'react';
import ProductModalCarousel from '../ProductModal/ProductModal';
import { API_ENDPOINTS } from '../../utils/api';
import { getTelegramHeaders } from '../../utils/telegramHeaders';
import './Favorite.scss';
import formatPrice from '../../utils/formatPrice';
import { emitCartUpdated } from '../../utils/cartEvents';
import { Link, useLocation } from 'react-router-dom';

const Favorite = () => {
  const [favorites, setFavorites] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [notificationEnabled, setNotificationEnabled] = useState(true);
  const location = useLocation();

  const fetchFavorites = useCallback(() => {
    fetch(API_ENDPOINTS.FAVORITES.LIST, {
      headers: getTelegramHeaders(),
    })
      .then(res => res.json())
      .then(data => {
        setFavorites(data);
      })
      .catch(err => {
        console.error('❌ [Favorite] Ошибка загрузки избранного:', err);
      });
  }, []);

  useEffect(() => {
    fetchFavorites();
  }, [fetchFavorites]);

  useEffect(() => {
    fetchFavorites();
  }, [location.pathname, fetchFavorites]);


  const removeFavorite = (productId) => {
    fetch(`${API_ENDPOINTS.FAVORITES.REMOVE}?product_id=${productId}`, {
      method: 'DELETE',
      headers: getTelegramHeaders(),
    })
      .then(() => {
        setFavorites(prev => prev.filter(fav => fav.product !== productId));
      })
      .catch(err => {});
  };

  const handleAddToCart = (product, quantity = 1) => {
    fetch(API_ENDPOINTS.CART.ADD, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getTelegramHeaders(),
      },
      body: JSON.stringify({
        product_id: product.id,
        quantity,
      }),
    })
      .then(res => res.json())
      .then(data => {
        setSelectedProduct(null);
        emitCartUpdated();
      })
      .catch(err => {});
  };

  return (
    <>

      {favorites.length === 0 ? (
        <div className="favorite__empty">
          <div className='favorite__empty-content'>
          <p className='favorite__empty-text'>У вас пока нет избранных товаров</p>
          <Link to="/">
            <button className='favorite__button'>Перейти в каталог</button>
          </Link>
          </div>
        </div>
      ) : (
        <div className="catalog">
          {favorites.map((favorite) => {
            const product = favorite.product_info;
            const isOutOfStock = product.in_stock === 0;

            return (
              <div
                className="catalog__card"
                key={product.id}
                onClick={() => setSelectedProduct(product)}
              >
                <div className="catalog__image-wrapper">
                  <img src={product.photo1} alt={product.name} className="catalog__image" />


                <div className="tags">
                  {isOutOfStock && <span className="tag tag--out-of-stock">Нет в наличии</span>}
                  {product.flug_new && <span className="tag tag--new">Новинка</span>}
                  {product.flug_popular && <span className="tag tag--popular">Популярное</span>}
                </div>

                  <button
                    className="favorite__btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFavorite(product.id);
                    }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="#e63946" viewBox="-1 -2 17 18">
                      <path fillRule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314" />
                    </svg>
                  </button>
                </div>

                <div className="catalog__info">
                  <span className="catalog__price">{formatPrice(product.price)}₽</span>
                  {product.oldprice && product.oldprice > 0 && (
                    <span className="catalog__price catalog__price--old">{formatPrice(product.oldprice)}₽</span>
                  )}
                  <h3 className="catalog__title">{product.name}</h3>
                  <div className="catalog__rating">
                    <span className="catalog__stars">&#9733;</span>
                    <span> {product.average_rating.toFixed(1)}</span>
                    {product.reviews_count > 0 && <span className="catalog__reviews-count"> ({product.reviews_count})</span>}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {selectedProduct && (
        <ProductModalCarousel
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
          onAddToCart={handleAddToCart}
        />
      )}
    </>
  );
};

export default Favorite;
