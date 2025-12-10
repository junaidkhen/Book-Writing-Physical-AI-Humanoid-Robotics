import React, {useState} from 'react';
import clsx from 'clsx';
import styles from './InteractiveModuleSelector.module.css';

const ModuleData = [
  {
    id: 1,
    title: 'Module 1: Foundations',
    description: 'Introduction to Physical AI and basic concepts of digital brain to physical body',
    weeks: 'Weeks 1-5',
    topics: ['Digital vs Physical Intelligence', 'Sensing the World', 'Motor Control', 'Perception Pipeline', 'Digital Twin Concepts'],
    color: 'var(--textbook-accent-1)',
  },
  {
    id: 2,
    title: 'Module 2: Physics & Interaction',
    description: 'Understanding how robots interact with the physical world',
    weeks: 'Weeks 6-7',
    topics: ['Physics & Interaction Basics', 'Human-Robot Interaction', 'Contact & Friction'],
    color: 'var(--textbook-accent-2)',
  },
  {
    id: 3,
    title: 'Module 3: Vision & Navigation',
    description: 'Vision systems and navigation techniques for robots',
    weeks: 'Weeks 8-10',
    topics: ['Vision Systems', 'Mapping & Understanding Environments', 'Navigation & Path Planning'],
    color: 'var(--textbook-accent-3)',
  },
  {
    id: 4,
    title: 'Module 4: Kinematics & Decision-Making',
    description: 'Advanced concepts in movement and decision systems',
    weeks: 'Weeks 11-13',
    topics: ['Kinematics & Movement', 'Decision-Making for Robots', 'Full System Overview'],
    color: 'var(--textbook-accent-4)',
  },
];

function ModuleCard({module, isActive, onClick}) {
  return (
    <div
      className={clsx(
        styles.moduleCard,
        {[styles.active]: isActive}
      )}
      style={{borderLeft: `4px solid ${module.color}`}}
      onClick={() => onClick(module.id)}
    >
      <div className={styles.moduleHeader}>
        <h3 className={styles.moduleTitle} style={{color: module.color}}>
          {module.title}
        </h3>
        <span className={styles.weeks}>{module.weeks}</span>
      </div>
      <p className={styles.moduleDescription}>{module.description}</p>
      <div className={styles.topics}>
        <h4>Key Topics:</h4>
        <ul>
          {module.topics.map((topic, index) => (
            <li key={index}>{topic}</li>
          ))}
        </ul>
      </div>
      <button className={clsx('button button--primary button--block', styles.moduleButton)}>
        Start Learning
      </button>
    </div>
  );
}

export default function InteractiveModuleSelector() {
  const [activeModule, setActiveModule] = useState(1);

  return (
    <div className={styles.moduleSelector}>
      <div className={styles.header}>
        <h2 className="module-header">Explore the Learning Modules</h2>
        <p>Choose a module to begin your journey in Physical AI and Humanoid Robotics</p>
      </div>
      <div className={styles.modulesGrid}>
        {ModuleData.map((module) => (
          <ModuleCard
            key={module.id}
            module={module}
            isActive={activeModule === module.id}
            onClick={setActiveModule}
          />
        ))}
      </div>
    </div>
  );
}