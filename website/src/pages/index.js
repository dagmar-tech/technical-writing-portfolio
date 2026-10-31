import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import styles from './index.module.css';

export default function Home() {
  return (
    <Layout
      title="Home"
      description="Technical writing portfolio featuring tutorials and practical software projects."
    >
      <header className={styles.hero}>
        <div className="container">
          <p className={styles.eyebrow}>
            TECHNICAL WRITING · DOCUMENTATION · AUTOMATION
          </p>

          <h1 className={styles.title}>
            Technical writing portfolio
          </h1>

          <p className={styles.subtitle}>
            I figure out how software works and explain it clearly
            so readers can get things done.
          </p>

          <div className={styles.buttons}>
            <Link
              className="button button--primary button--lg"
              to="/docs/tutorials/releasing-a-versioned-phrasebook-package"
            >
              Explore tutorials
            </Link>

            <Link
              className="button button--secondary button--lg"
              to="/docs/projects/outdated-reference-finder"
            >
              Explore projects
            </Link>
                
            <Link
              className="button button--secondary button--lg"
              to="/docs/projects/grafana-fundamentals-tutorial-review"
            >
              Explore documentation reviews
            </Link>
          </div>
        </div>
      </header>

      <main className={`container ${styles.main}`}>
        <section aria-labelledby="samples-heading">
          <h2 id="samples-heading" className={styles.sectionTitle}>
            Selected samples
          </h2>

          <div className={styles.grid}>
            <article className={styles.card}>
              <p className={styles.cardCategory}>TUTORIAL</p>

              <h3>
                <Link to="/docs/tutorials/releasing-a-versioned-phrasebook-package">
                  Releasing a versioned Phrasebook package
                </Link>
              </h3>

              <p>
                A step-by-step guide to preparing and validating resources,
                extracting files, using Git and pull requests, and completing
                quality assurance.
              </p>

              <Link
                className={styles.cardLink}
                to="/docs/tutorials/releasing-a-versioned-phrasebook-package"
              >
                Read tutorial →
              </Link>
            </article>

            <article className={styles.card}>
              <p className={styles.cardCategory}>PROJECT</p>

              <h3>
                <Link to="/docs/projects/outdated-reference-finder">
                  Outdated reference finder
                </Link>
              </h3>

              <p>
                A Python tool that identifies potential outdated references,
                generates prioritized CSV reports, and supports human review
                before changes are applied.
              </p>

              <Link
                className={styles.cardLink}
                to="/docs/projects/outdated-reference-finder"
              >
                Explore project →
              </Link>
            </article>
                              
            <article className={styles.card}>
              <p className={styles.cardCategory}>DOCUMENTATION REVIEW</p>

              <h3>
                <Link to="/docs/projects/grafana-fundamentals-tutorial-review">
                  Grafana Fundamentals: hands-on documentation review
                </Link>
              </h3>

              <p>
                An independent, hands-on review of Grafana's Fundamentals
                tutorial, identifying usability issues, outdated instructions,
                and opportunities to improve the learning experience.
              </p>

              <Link
                className={styles.cardLink}
                to="/docs/projects/grafana-fundamentals-tutorial-review"
              >
                Read documentation review →
              </Link>
            </article>
          </div>
        </section>

        <section className={styles.about} aria-labelledby="about-heading">
          <h2 id="about-heading">About</h2>

          <p>
            I have experience in conversational AI, technical support,
            language engineering, and automation. I enjoy figuring out how
            software works and explaining it clearly so readers can get
            things done.
          </p>

          <p>
            The portfolio includes a fictional tutorial and an
            anonymized, experience-based project demo.
          </p>

          <p>
            <a href="https://github.com/dagmar-tech/technical-writing-portfolio">
              View the source files on GitHub →
            </a>
          </p>
        </section>
      </main>
    </Layout>
  );
}
