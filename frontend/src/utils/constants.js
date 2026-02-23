export const WAREHOUSE_COORDS = {
  lat: 51.1605,
  lng: 71.4704,
  city: 'Сызрань',
  country: 'Россия',
};

export const PROMO_CODES = {
  START: {
    code: 'START',
    discount: 0.25,
  },
};

export const ORDER_STATUSES = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  SHIPPED: 'shipped',
  DELIVERED: 'delivered',
  CANCELLED: 'cancelled',
};

export const PRODUCT_TAGS = {
  NEW: 'new',
  POPULAR: 'popular',
  OUT_OF_STOCK: 'out_of_stock',
};

export const IMAGE_DIMENSIONS = {
  PRODUCT_CARD: {
    width: 110,
    height: 110,
  },
  PRODUCT_MODAL: {
    width: '100%',
    height: 'auto',
  },
};

export default {
  WAREHOUSE_COORDS,
  PROMO_CODES,
  ORDER_STATUSES,
  PRODUCT_TAGS,
  IMAGE_DIMENSIONS,
};
