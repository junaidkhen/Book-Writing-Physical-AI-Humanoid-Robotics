import React from 'react';
import clsx from 'clsx';
import styles from './LoadingIndicator.module.css';

interface LoadingIndicatorProps {
  message?: string;
  size?: 'small' | 'medium' | 'large';
  inline?: boolean;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  message = 'AI is thinking...',
  size = 'medium',
  inline = false
}) => {
  return (
    <div className={clsx(
      styles.loadingContainer,
      inline ? styles.inline : styles.block,
      styles[size]
    )}>
      <div className={styles.spinner}>
        <div className={styles.spinnerDot}></div>
        <div className={styles.spinnerDot}></div>
        <div className={styles.spinnerDot}></div>
      </div>
      <div className={styles.loadingMessage}>{message}</div>
    </div>
  );
};

export default LoadingIndicator;