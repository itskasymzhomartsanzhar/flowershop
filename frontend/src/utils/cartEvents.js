export const CART_UPDATED_EVENT = 'cart:updated';

export const emitCartUpdated = () => {
  window.dispatchEvent(new Event(CART_UPDATED_EVENT));
};
