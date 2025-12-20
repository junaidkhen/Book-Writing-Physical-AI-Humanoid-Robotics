import React from 'react';
import clsx from 'clsx';
import styles from './CitationList.module.css';

interface Citation {
  id: string;
  title: string;
  url: string;
  text: string;
  page?: number;
  chapter?: string;
}

interface CitationListProps {
  citations: Citation[];
  onCitationClick?: (citation: Citation) => void;
}

const CitationList: React.FC<CitationListProps> = ({ citations, onCitationClick }) => {
  if (!citations || citations.length === 0) {
    return null;
  }

  return (
    <div className={styles.citationList}>
      <div className={styles.citationTitle}>Sources Referenced:</div>
      <ul className={styles.citationItems}>
        {citations.map((citation) => (
          <li key={citation.id} className={styles.citationItem}>
            <a
              href={citation.url}
              className={styles.citationLink}
              onClick={(e) => {
                e.preventDefault();
                if (onCitationClick) {
                  onCitationClick(citation);
                } else {
                  // Default behavior: navigate to citation URL
                  if (citation.url) {
                    window.location.href = citation.url;
                  }
                }
              }}
            >
              <div className={styles.citationTitleText}>
                {citation.title}
                {citation.chapter && <span className={styles.chapterInfo}> ({citation.chapter})</span>}
                {citation.page && <span className={styles.pageInfo}> [p. {citation.page}]</span>}
              </div>
              <div className={styles.citationPreview}>{citation.text}</div>
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CitationList;