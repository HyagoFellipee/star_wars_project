interface SectionLoaderProps {
  itemCount?: number;
  columns?: string;
}

export default function SectionLoader({
  itemCount = 4,
  columns = "grid-cols-2 sm:grid-cols-3 lg:grid-cols-4"
}: SectionLoaderProps) {
  return (
    <div className={`grid ${columns} gap-4`}>
      {[...Array(itemCount)].map((_, i) => (
        <div
          key={i}
          className="p-4 bg-sw-darker rounded-lg border border-transparent animate-pulse"
        >
          <div className="h-4 bg-sw-gray/30 rounded w-3/4 mb-2" />
          <div className="h-3 bg-sw-gray/30 rounded w-1/2" />
        </div>
      ))}
    </div>
  );
}
