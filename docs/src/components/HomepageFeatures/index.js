import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Comprehensive Learning Path',
    image: require('@site/static/diagrams/Robotics/comprehensive-learning-path.png').default,
    description: (
      <>
        A structured 13-week journey through Physical AI and Humanoid Robotics,
        from foundational concepts to advanced decision-making systems.
      </>
    ),
  },
  {
    title: 'Practical Code Examples',
    image: require('@site/static/diagrams/Robotics/practical-code-examples.jpg').default,
    description: (
      <>
        20 runnable code examples with environment specifications and test scripts
        to reinforce theoretical concepts with hands-on practice.
      </>
    ),
  },
  {
    title: 'Cutting-Edge Topics',
    image: require('@site/static/diagrams/Robotics/cutting-edge-topics.PNG').default,
    description: (
      <>
        Explore the latest in embodied artificial intelligence, sensor fusion,
        navigation systems, and human-robot interaction paradigms.
      </>
    ),
  },
];

function Feature({image, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <img src={image} className={styles.featureSvg} alt={title} />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
