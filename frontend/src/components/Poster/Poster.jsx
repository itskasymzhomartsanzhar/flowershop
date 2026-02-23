import './Poster.scss';
import poster from '@/assets/poster.webp';

const Poster = () => {
  return (
    <div className="poster-block">
      <img className="poster-img" src={poster} alt="Poster" />
    </div>
  );
};

export default Poster;