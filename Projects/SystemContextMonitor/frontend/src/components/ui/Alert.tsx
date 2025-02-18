import React, { useEffect, useState } from 'react';
import styles from './Alert.module.css';

type AlertType = 'info' | 'success' | 'warning' | 'error';

interface AlertProps {
  type?: AlertType;
  message?: string;
  children?: React.ReactNode;
  title?: string;
  onClose?: () => void;
  autoClose?: boolean;
  autoCloseDelay?: number;
  className?: string;
  showIcon?: boolean;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  message,
  children,
  title,
  onClose,
  autoClose = false,
  autoCloseDelay = 5000,
  className = '',
  showIcon = true
}) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    if (autoClose && isVisible) {
      timeoutId = setTimeout(() => {
        setIsVisible(false);
        onClose?.();
      }, autoCloseDelay);
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [autoClose, autoCloseDelay, isVisible, onClose]);

  if (!isVisible) {
    return null;
  }

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return '✓';
      case 'warning':
        return '⚠';
      case 'error':
        return '✕';
      default:
        return 'ℹ';
    }
  };

  const alertClasses = [
    styles.alert,
    styles[`alert-${type}`],
    className
  ].filter(Boolean).join(' ');

  return (
    <div
      role="alert"
      className={alertClasses}
      aria-live={type === 'error' ? 'assertive' : 'polite'}
    >
      {showIcon && <span className={styles.icon} aria-hidden="true">{getIcon()}</span>}
      <div className={styles.content}>
        {title && <h4 className={styles.title}>{title}</h4>}
        <p className={styles.message}>{message || children}</p>
      </div>
      {onClose && (
        <button
          type="button"
          className={styles.close}
          onClick={handleClose}
          aria-label="Close alert"
        >
          ×
        </button>
      )}
    </div>
  );
};

export default Alert; 