import { useState, useEffect, useRef } from 'react';

export const useCarousel = (itemsCount) => {
  const [slideIndex, setSlideIndex] = useState(0);
  const carouselRef = useRef(null);
  const touchStartX = useRef(0);
  const isDragging = useRef(false);
  const mouseStartX = useRef(0);

  const goToSlide = (index) => {
    let newIndex = index;
    if (index >= itemsCount) newIndex = 0;
    if (index < 0) newIndex = itemsCount - 1;
    setSlideIndex(newIndex);
  };

  useEffect(() => {
    const carousel = carouselRef.current;
    if (!carousel || itemsCount <= 1) return;

    const onTouchStart = (e) => {
      touchStartX.current = e.touches[0].clientX;
    };

    const onTouchEnd = (e) => {
      const endX = e.changedTouches[0].clientX;
      const deltaX = touchStartX.current - endX;
      if (Math.abs(deltaX) > 50) {
        goToSlide(deltaX > 0 ? slideIndex + 1 : slideIndex - 1);
      }
    };

    const onMouseDown = (e) => {
      isDragging.current = true;
      mouseStartX.current = e.clientX;
    };

    const onMouseMove = (e) => {
      if (!isDragging.current) return;
      const deltaX = mouseStartX.current - e.clientX;
      if (Math.abs(deltaX) > 50) {
        goToSlide(deltaX > 0 ? slideIndex + 1 : slideIndex - 1);
        isDragging.current = false;
      }
    };

    const onMouseUp = () => {
      isDragging.current = false;
    };

    const onMouseLeave = () => {
      isDragging.current = false;
    };

    carousel.addEventListener('touchstart', onTouchStart);
    carousel.addEventListener('touchend', onTouchEnd);
    carousel.addEventListener('mousedown', onMouseDown);
    carousel.addEventListener('mousemove', onMouseMove);
    carousel.addEventListener('mouseup', onMouseUp);
    carousel.addEventListener('mouseleave', onMouseLeave);

    return () => {
      carousel.removeEventListener('touchstart', onTouchStart);
      carousel.removeEventListener('touchend', onTouchEnd);
      carousel.removeEventListener('mousedown', onMouseDown);
      carousel.removeEventListener('mousemove', onMouseMove);
      carousel.removeEventListener('mouseup', onMouseUp);
      carousel.removeEventListener('mouseleave', onMouseLeave);
    };
  }, [slideIndex, itemsCount]);

  return {
    slideIndex,
    carouselRef,
    goToSlide,
  };
};

export default useCarousel;
