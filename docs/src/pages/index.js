import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import InteractiveModuleSelector from '@site/src/components/InteractiveModuleSelector';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Start Reading - 13 Week Journey 🚀
          </Link>
          <Link
            className="button button--primary button--lg"
            to="/docs/module-1/week-01-foundations">
            Jump to Module 1
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Physical AI & Humanoid Robotics Textbook`}
      description="A comprehensive 13-week educational journey through Physical AI and Humanoid Robotics - from foundational concepts to advanced decision-making systems">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <InteractiveModuleSelector />
      </main>
    </Layout>
  );
}
