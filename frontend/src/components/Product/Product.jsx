import { useEffect, useMemo, useState } from 'react';
import ProductModalCarousel from '../ProductModal/ProductModal';
import getTelegramHeaders from '../../utils/telegramHeaders';
import API_ENDPOINTS, { API_BASE_URL } from '../../utils/api';
import './Product.scss';

const getQuantityStep = (product) => Math.max(1, Number(product?.quantity_step || 1));

const normalizeQuantityByStep = (quantity, step) => {
  const parsed = Number(quantity);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return step;
  }
  const normalized = Math.floor(parsed / step) * step;
  return Math.max(step, normalized);
};

function similarity(a, b) {
  if (!a || !b) return 0;

  const first = a.toLowerCase();
  const second = b.toLowerCase();
  const matrix = [];

  for (let i = 0; i <= second.length; i += 1) {
    matrix[i] = [i];
  }
  for (let j = 0; j <= first.length; j += 1) {
    matrix[0][j] = j;
  }

  for (let i = 1; i <= second.length; i += 1) {
    for (let j = 1; j <= first.length; j += 1) {
      if (second.charAt(i - 1) === first.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }

  const distance = matrix[second.length][first.length];
  const maxLen = Math.max(first.length, second.length);
  return (1 - distance / maxLen) * 100;
}

const Product = ({ activeTab, searchQuery, filterState = 0 }) => {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [favorites, setFavorites] = useState([]);
  const [catalogQuantities, setCatalogQuantities] = useState({});
  const [addingIds, setAddingIds] = useState({});

  useEffect(() => {
    fetchFavorites();
  }, []);

  useEffect(() => {
    let url = `${API_BASE_URL}/product/`;
    if (filterState === 0) {
      url = `${API_BASE_URL}/product/recommended/`;
    } else if (filterState === 1) {
      url = `${API_BASE_URL}/product/price-ascending/`;
    } else if (filterState === 2) {
      url = `${API_BASE_URL}/product/price-descending/`;
    }

    fetch(url)
      .then((res) => res.json())
      .then((data) => setProducts(Array.isArray(data) ? data : []))
      .catch((err) => console.error('Ошибка при загрузке продуктов:', err));
  }, [filterState]);

  useEffect(() => {
    setCatalogQuantities((prev) => {
      const next = {};
      products.forEach((product) => {
        const step = getQuantityStep(product);
        next[product.id] = normalizeQuantityByStep(prev[product.id], step);
      });
      return next;
    });
  }, [products]);

  const fetchFavorites = () => {
    fetch(API_ENDPOINTS.FAVORITES.GET, {
      headers: getTelegramHeaders(),
    })
      .then((res) => res.json())
      .then((data) => {
        const favoriteIds = Array.isArray(data) ? data.map((fav) => fav.product) : [];
        setFavorites(favoriteIds);
      })
      .catch((err) => console.error('Ошибка при загрузке избранного:', err));
  };

  const toggleFavorite = (productId) => {
    const isFavorite = favorites.includes(productId);
    if (isFavorite) {
      fetch(`${API_ENDPOINTS.FAVORITES.REMOVE}?product_id=${productId}`, {
        method: 'DELETE',
        headers: getTelegramHeaders(),
      })
        .then((res) => res.json())
        .then(() => setFavorites((prev) => prev.filter((id) => id !== productId)))
        .catch((err) => console.error('Ошибка при удалении из избранного:', err));
      return;
    }

    fetch(API_ENDPOINTS.FAVORITES.ADD, {
      method: 'POST',
      headers: getTelegramHeaders(),
      body: JSON.stringify({ product_id: productId }),
    })
      .then((res) => res.json())
      .then(() => setFavorites((prev) => [...prev, productId]))
      .catch((err) => console.error('Ошибка при добавлении в избранное:', err));
  };

  const filteredProducts = useMemo(
    () =>
      products.filter((product) => {
        let inCategory = false;
        if (activeTab === 'Все') {
          inCategory = true;
        } else if (activeTab === 'Новинки') {
          inCategory = product.flug_new === true;
        } else if (activeTab === 'Популярные') {
          inCategory = product.flug_popular === true;
        } else {
          inCategory = product.category_name === activeTab;
        }

        const matchesSearch =
          searchQuery.trim() === '' ||
          similarity(product.name, searchQuery) >= 60 ||
          similarity(product.description || '', searchQuery) >= 60;
        return inCategory && matchesSearch;
      }),
    [products, activeTab, searchQuery]
  );

  const handleAddToCart = async (product, quantity = 1, closeModal = true) => {
    const step = getQuantityStep(product);
    const safeQuantity = normalizeQuantityByStep(quantity, step);
    if (safeQuantity <= 0) {
      return false;
    }

    try {
      const response = await fetch(API_ENDPOINTS.CART.ADD, {
        method: 'POST',
        headers: getTelegramHeaders(),
        body: JSON.stringify({
          product_id: product.id,
          quantity: safeQuantity,
        }),
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      if (closeModal) {
        setSelectedProduct(null);
      }
      return true;
    } catch (err) {
      console.error('Ошибка при добавлении в корзину:', err);
      return false;
    }
  };

  const changeCatalogQuantity = (product, direction, event) => {
    event.stopPropagation();
    const step = getQuantityStep(product);
    setCatalogQuantities((prev) => {
      const current = normalizeQuantityByStep(prev[product.id], step);
      const nextValue = direction === 'inc' ? current + step : Math.max(step, current - step);
      return { ...prev, [product.id]: nextValue };
    });
  };

  const quickAddToCart = async (product, event) => {
    event.stopPropagation();
    const step = getQuantityStep(product);
    const quantity = normalizeQuantityByStep(catalogQuantities[product.id], step);
    setAddingIds((prev) => ({ ...prev, [product.id]: true }));
    await handleAddToCart(product, quantity, false);
    setAddingIds((prev) => ({ ...prev, [product.id]: false }));
  };

  return (
    <>
      <div className="catalog">
        {filteredProducts.map((product) => {
          const isFavorite = favorites.includes(product.id);
          const isOutOfStock = product.in_stock === 0;
          const selectedQuantity = normalizeQuantityByStep(catalogQuantities[product.id], getQuantityStep(product));
          const isAdding = Boolean(addingIds[product.id]);
          const totalPrice = product.price * selectedQuantity;

          return (
            <div className="catalog__card" key={`${product.id}-${product.name}`} onClick={() => setSelectedProduct(product)}>
              <div className="catalog__image-wrapper">
                <img src={product.photo1} alt={product.name} className="catalog__image" />

                <div className="tags">
                  {isOutOfStock && <span className="tag tag--out-of-stock">Нет в наличии</span>}
                  {product.flug_new && <span className="tag tag--new">Новинка</span>}
                  {product.flug_popular && <span className="tag tag--popular">Популярное</span>}
                </div>

                <button
                  className="favorite__btn"
                  onClick={(event) => {
                    event.stopPropagation();
                    toggleFavorite(product.id);
                  }}
                >
                  {isFavorite ? (
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="#e63946" viewBox="-1 -2 17 18">
                      <path fillRule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314" />
                    </svg>
                  ) : (
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      fill="#fff"
                      stroke="#e63946"
                      strokeWidth="1"
                      viewBox="-1 -2 17 18"
                    >
                      <path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143q.09.083.176.171a3 3 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15" />
                    </svg>
                  )}
                </button>
              </div>

              <div className="catalog__info">
                <div className="catalog__price-row">
                  <span className="catalog__price">{product.price}₽</span>
                  {product.oldprice && product.oldprice > 0 && (
                    <span className="catalog__price catalog__price--old">{product.oldprice}₽</span>
                  )}
                </div>
                <h3 className="catalog__title">{product.name}</h3>
                <div className="catalog__rating">
                  <span className="catalog__stars">&#9733;</span>
                  <span> {product.average_rating.toFixed(1)}</span>
                  {product.reviews_count > 0 && <span className="catalog__reviews-count"> ({product.reviews_count})</span>}
                </div>

                <div className="catalog__quick" onClick={(event) => event.stopPropagation()}>
                  <div className="catalog__counter">
                    <button
                      type="button"
                      className="catalog__counter-btn"
                      disabled={isOutOfStock}
                      onClick={(event) => changeCatalogQuantity(product, 'dec', event)}
                    >
                      -
                    </button>
                    <input type="text" readOnly className="catalog__counter-value" value={selectedQuantity} />
                    <button
                      type="button"
                      className="catalog__counter-btn"
                      disabled={isOutOfStock}
                      onClick={(event) => changeCatalogQuantity(product, 'inc', event)}
                    >
                      +
                    </button>
                  </div>
                  <button
                    type="button"
                    className="catalog__add-btn"
                    disabled={isOutOfStock || isAdding}
                    onClick={(event) => quickAddToCart(product, event)}
                  >
                    {isOutOfStock ? 'Нет в наличии' : isAdding ? 'Добавляем...' : `Добавить ${totalPrice}₽`}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {selectedProduct && (
        <ProductModalCarousel product={selectedProduct} onClose={() => setSelectedProduct(null)} onAddToCart={handleAddToCart} />
      )}
    </>
  );
};

export default Product;
