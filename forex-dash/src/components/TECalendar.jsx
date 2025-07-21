import React from 'react';

function TECalendar({ data }) {
    return (
        <div>
         
            {data && data.length > 0 ? (
                <table border="1" style={{ width: '100%', textAlign: 'left' }}>
                    <thead>
                        <tr>
                            
                            <th>Category</th>
                            <th>Country</th>
                            <th>Date</th>
                            <th>Event</th>
                            <th>Actual</th>
                            <th>Forecast</th>
                            <th>Previous</th>
                            <th>Symbol</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((item, index) => (
                            <tr key={index}>
                               
                                <td>{item.category}</td>
                                <td>{item.country}</td>
                                <td>{new Date(item.date).toLocaleString()}</td>
                                <td>{item.event}</td>
                                <td>{item.actual}</td>
                                <td>{item.forecast}</td>
                                <td>{item.previous}</td>
                                <td>{item.symbol}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            ) : (
                <p>No data available</p>
            )}
        </div>
    );
}

export default TECalendar;
