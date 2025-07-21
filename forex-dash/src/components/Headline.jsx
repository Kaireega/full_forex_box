import React from 'react';

function Headline({ data }) {
  // Fallback for missing data
  if (!data || !data.link || !data.headline) {
    console.warn("Invalid data passed to Headline:", data);
    return null; // Don't render anything if data is invalid
  }

  return (
    <div className='headline'>
      <a href={data.link} target="_blank" rel="noreferrer">
        {data.headline}
      </a>
    </div>
  );
}

export default Headline;
