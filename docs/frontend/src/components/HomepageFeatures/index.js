import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="text--center">
          <Heading as="h1">Robotics Learning Modules</Heading>
          <p>Explore the fascinating world of Physical AI and Humanoid Robotics</p>
        </div>

        <div className="row padding-vert--lg">
          <div className="col col--4">
            <div className="text--center">
              <img
                src="diagrams/module-1/perception-stages.svg"
                alt="Perception Systems"
                className={styles.featureImage}
                style={{maxWidth: '100%', height: 'auto'}}
              />
              <Heading as="h3">Perception Systems</Heading>
              <p>Learn about sensors, computer vision, and environment understanding</p>
            </div>
          </div>

          <div className="col col--4">
            <div className="text--center">
              <img
                src="diagrams/module-2/balance-equations.svg"
                alt="Locomotion & Balance"
                className={styles.featureImage}
                style={{maxWidth: '100%', height: 'auto'}}
              />
              <Heading as="h3">Locomotion & Balance</Heading>
              <p>Understand physics-based movement and dynamic stability</p>
            </div>
          </div>

          <div className="col col--4">
            <div className="text--center">
              <img
                src="diagrams/module-3/navigation-flowchart.svg"
                alt="Navigation & Planning"
                className={styles.featureImage}
                style={{maxWidth: '100%', height: 'auto'}}
              />
              <Heading as="h3">Navigation & Planning</Heading>
              <p>Explore path planning, mapping, and autonomous decision making</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}