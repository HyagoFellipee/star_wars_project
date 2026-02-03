interface FilterSelectProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
  placeholder?: string;
}

export default function FilterSelect({
  label,
  value,
  onChange,
  options,
  placeholder,
}: FilterSelectProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      aria-label={label}
      className="bg-sw-dark border border-sw-gray rounded-lg px-3 py-2 text-sm text-white
                 focus:border-sw-yellow focus:outline-none focus:ring-1 focus:ring-sw-yellow
                 hover:border-sw-gray/70 transition-colors cursor-pointer"
    >
      <option value="">{placeholder || `All ${label}`}</option>
      {options.map((opt) => (
        <option key={opt} value={opt} className="capitalize">
          {opt}
        </option>
      ))}
    </select>
  );
}
