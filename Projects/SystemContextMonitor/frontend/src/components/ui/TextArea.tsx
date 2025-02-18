import React, { ChangeEvent } from 'react';
import styles from './TextArea.module.css';

interface TextAreaProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  rows?: number;
  disabled?: boolean;
  className?: string;
  maxLength?: number;
  minLength?: number;
  required?: boolean;
  autoFocus?: boolean;
  name?: string;
  id?: string;
  'aria-label'?: string;
  'aria-describedby'?: string;
}

export const TextArea: React.FC<TextAreaProps> = ({
  value,
  onChange,
  placeholder = '',
  rows = 4,
  disabled = false,
  className = '',
  maxLength,
  minLength,
  required = false,
  autoFocus = false,
  name,
  id,
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedby
}) => {
  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
  };

  const wrapperClasses = [
    styles['textarea-wrapper'],
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={wrapperClasses}>
      <textarea
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        rows={rows}
        disabled={disabled}
        maxLength={maxLength}
        minLength={minLength}
        required={required}
        autoFocus={autoFocus}
        name={name}
        id={id}
        aria-label={ariaLabel}
        aria-describedby={ariaDescribedby}
        className={styles.textarea}
      />
      {maxLength && (
        <div className={styles['character-count']} aria-live="polite">
          {value.length}/{maxLength}
        </div>
      )}
    </div>
  );
};

export default TextArea; 