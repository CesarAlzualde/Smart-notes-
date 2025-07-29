import React from 'react';

interface SimpleComponentProps {
  text: string;
}

const SimpleComponent: React.FC<SimpleComponentProps> = ({ text }) => {
  return (
    <div className="simple-component">
      <h1>Simple Test Component</h1>
      <p data-testid="text-content">{text}</p>
      <button data-testid="test-button">Click me</button>
    </div>
  );
};

export default SimpleComponent;
