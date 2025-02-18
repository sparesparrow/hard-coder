import React, { ChangeEvent } from 'react';
import styles from './Select.module.css';

interface SelectProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  className?: string;
  error?: string;
  children: React.ReactNode;
}

export const Select: React.FC<SelectProps> = ({
  value,
  onChange,
  disabled = false,
  className = '',
  error,
  children
}) => {
  const handleChange = (e: ChangeEvent<HTMLSelectElement>) => {
    onChange(e.target.value);
  };

  return (
    <div className={styles.container}>
      <select
        value={value}
        onChange={handleChange}
        disabled={disabled}
        className={`${styles.select} ${error ? styles.error : ''} ${className}`}
      >
        {children}
      </select>
      {error && <div className={styles.errorMessage}>{error}</div>}
    </div>
  );
}; 