export const getQuantityStep = (product) => Math.max(1, Number(product?.quantity_step || 1));

export const getAvailableStock = (product) => {
  const raw = product?.in_stock;
  if (raw === null || raw === undefined) {
    return null;
  }
  const value = Number(raw);
  if (!Number.isFinite(value)) {
    return null;
  }
  return value;
};

export const getMaxOrderableQuantity = (product) => {
  const step = getQuantityStep(product);
  const available = getAvailableStock(product);
  if (available === null) {
    return Number.POSITIVE_INFINITY;
  }
  if (available < step || available <= 0) {
    return 0;
  }
  return Math.floor(available / step) * step;
};

export const isOutOfStock = (product) => {
  const step = getQuantityStep(product);
  const available = getAvailableStock(product);
  if (available === null) {
    return false;
  }
  return available <= 0 || available < step;
};

export const clampQuantityToStock = (product, quantity) => {
  const step = getQuantityStep(product);
  const parsed = Number(quantity);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return step;
  }
  const normalized = Math.floor(parsed / step) * step;
  const maxQty = getMaxOrderableQuantity(product);
  if (!Number.isFinite(maxQty)) {
    return Math.max(step, normalized);
  }
  if (maxQty <= 0) {
    return 0;
  }
  return Math.min(maxQty, Math.max(step, normalized));
};
