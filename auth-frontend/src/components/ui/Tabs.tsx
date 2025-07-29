import React, { useState } from 'react';
import './Tabs.css';

interface TabProps {
  label: string;
  children: React.ReactNode;
  icon?: string;
}

export const Tab: React.FC<TabProps> = ({ children }) => {
  return <div className="tab-content">{children}</div>;
};

interface TabsProps {
  children: React.ReactElement<TabProps>[];
}

export const Tabs: React.FC<TabsProps> = ({ children }) => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabClick = (index: number) => {
    setActiveTab(index);
  };

  return (
    <div className="tabs-container">
      <div className="tabs-list" role="tablist">
        {children.map((tab, index) => (
          <button
            key={index}
            className={`tab-item ${index === activeTab ? 'active' : ''}`}
            onClick={() => handleTabClick(index)}
            role="tab"
            aria-selected={index === activeTab}
            aria-controls={`tab-panel-${index}`}
          >
            {tab.props.icon && <i className={`fas ${tab.props.icon}`}></i>}
            <span>{tab.props.label}</span>
          </button>
        ))}
      </div>
      <div 
        className="tabs-content-container"
        id={`tab-panel-${activeTab}`}
        role="tabpanel"
      >
        {children[activeTab]}
      </div>
    </div>
  );
};
