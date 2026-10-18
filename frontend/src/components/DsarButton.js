import React from 'react';
import './DsarButton.css';

const DsarButton = ({ 
  children, 
  variant = 'primary', 
  size = 'medium', 
  disabled = false, 
  onClick,
  className = '',
  ...props 
}) => {
  const baseClass = 'dsar-button';
  const variantClass = `dsar-button--${variant}`;
  const sizeClass = `dsar-button--${size}`;
  const classes = `${baseClass} ${variantClass} ${sizeClass} ${className}`.trim();

  return (
    <button
      className={classes}
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
};

export default DsarButton;
