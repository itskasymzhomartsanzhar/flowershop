const formatPrice = (value) => {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return '0';
  }
  return new Intl.NumberFormat('ru-RU').format(number);
};

export default formatPrice;
