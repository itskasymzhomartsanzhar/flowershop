const API_BASE_URL = "https://flowershop.swifttest.ru/api";

export const API_ENDPOINTS = {
  CART: {
    GET: `${API_BASE_URL}/users/get_cart/`,
    UPDATE: `${API_BASE_URL}/users/update_cart/`,
    REMOVE: `${API_BASE_URL}/users/remove_from_cart/`,
    CLEAR: `${API_BASE_URL}/users/clear_cart/`,
    ADD: `${API_BASE_URL}/users/add_to_cart/`,
  },
  PRODUCTS: {
    LIST: `${API_BASE_URL}/products/`,
    DETAIL: (id) => `${API_BASE_URL}/products/${id}/`,
  },
  FAVORITES: {
    LIST: `${API_BASE_URL}/favorites/`,
    GET: `${API_BASE_URL}/favorites/`,
    ADD: `${API_BASE_URL}/favorites/`,
    REMOVE: `${API_BASE_URL}/favorites/remove/`,
  },
  ORDERS: {
    CREATE: `${API_BASE_URL}/users/create_order/`,
    LIST: `${API_BASE_URL}/users/orders/`,
    DETAIL: (id) => `${API_BASE_URL}/users/orders/${id}/`,
    RECENT: `${API_BASE_URL}/orders/recent_orders/`,
  },
  NOTIFICATIONS: {
    LIST: `${API_BASE_URL}/users/notifications/`,
    READ: (id) => `${API_BASE_URL}/users/notifications/${id}/read/`,
  },
  CATEGORIES: {
    LIST: `${API_BASE_URL}/categories/`,
  },
  BANNERS: {
    LIST: `${API_BASE_URL}/banners/`,
  },
  DELIVERY: {
    CHECK_ADDRESS: `${API_BASE_URL}/users/check_delivery_address/`,
    OPTIONS: `${API_BASE_URL}/users/delivery-options/`,
    SUGGEST: `${API_BASE_URL}/users/address-suggestions/`,
  },
  USERS: {
    PROFILE: `${API_BASE_URL}/users/profile/`,
    UPDATE_NOTIFICATIONS: `${API_BASE_URL}/users/update-notifications/`,
  },
  PAYMENT: {
    CREATE: `${API_BASE_URL}/users/create_payment/`,
    CHECK_STATUS: (id) => `${API_BASE_URL}/users/check_payment_status/${id}`,
  },
  PROMOCODE: {
    VALIDATE: `${API_BASE_URL}/users/validate-promocode/`,
    APPLY: `${API_BASE_URL}/users/apply-promocode/`,
  },
  REVIEWS: {
    CHECK: `${API_BASE_URL}/reviews/check/`,
    CREATE: `${API_BASE_URL}/reviews/create_review/`,
  },
  POSTER: {
    LIST: `${API_BASE_URL}/poster/`,
  },
  PRODUCT_API: {
    LIST: `${API_BASE_URL}/product/`,
  },
  CATEGORY: {
    LIST: `${API_BASE_URL}/category/`,
  },
  SERVICE: {
    PATH: `${API_BASE_URL}/service/`,
  },
};

export { API_BASE_URL };
export default API_ENDPOINTS;
