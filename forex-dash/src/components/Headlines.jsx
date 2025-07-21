import React, { useEffect, useState } from 'react';
import endPoints from '../app/api';
import Headline from './Headline';
import TitleHead from './TitleHead';

function Headlines() {
  const [headlines, setHeadlines] = useState(null);
  const [loading, setLoading] = useState(true); // Loading state for better UX
  const [error, setError] = useState(null); // Error state to handle failures

  useEffect(() => {
    loadHeadlines();
  }, []);

  const loadHeadlines = async () => {
    try {
      const data = await endPoints.headlines();
      if (!Array.isArray(data)) {
        throw new Error("Invalid data format: Expected an array");
      }
      setHeadlines(data);
    } catch (error) {
      console.error("Error loading headlines:", error);
      setError("Failed to load headlines. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <h2>Loading Headlines...</h2>;
  }

  if (error) {
    return <h2>{error}</h2>;
  }

  return (
    <div>
      <TitleHead title="Headlines" />
      <div className="segment">
        {headlines &&
          headlines.map((item, index) => {
            if (!item || !item.link || !item.headline) {
              console.warn("Skipping invalid headline:", item);
              return null; // Skip invalid headlines
            }
            return <Headline data={item} key={index} />;
          })}
      </div>
    </div>
  );
}

export default Headlines;
