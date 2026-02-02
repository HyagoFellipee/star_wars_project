type Category = 'character' | 'film' | 'starship' | 'planet';

interface PlaceholderImageProps {
  category: Category;
  aspectRatio?: string;
}

const icons: Record<Category, JSX.Element> = {
  character: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="w-16 h-16">
      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
    </svg>
  ),
  film: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="w-16 h-16">
      <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z" />
    </svg>
  ),
  starship: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="w-16 h-16">
      <path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z" />
    </svg>
  ),
  planet: (
    <svg viewBox="0 0 24 24" fill="currentColor" className="w-16 h-16">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
    </svg>
  ),
};

export default function PlaceholderImage({ category, aspectRatio }: PlaceholderImageProps) {
  return (
    <div
      className="w-full bg-gradient-to-b from-sw-darker to-sw-dark flex items-center justify-center text-sw-gray/40"
      style={aspectRatio ? { aspectRatio } : { height: '12rem' }}
    >
      {icons[category]}
    </div>
  );
}
