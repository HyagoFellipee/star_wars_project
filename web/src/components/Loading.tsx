interface LoadingProps {
  message?: string;
}

export default function Loading({ message = 'Loading...' }: LoadingProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      {/* Star Wars inspired loading animation */}
      <div className="flex space-x-2 mb-4">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="star w-2 h-2 bg-sw-yellow rounded-full"
          />
        ))}
      </div>
      <p className="text-gray-400 text-sm">{message}</p>
    </div>
  );
}
