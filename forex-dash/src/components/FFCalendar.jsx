import React from 'react';


function FFCalendar({data}) {
    return (
        <div>
            
            {data && data.length > 0 ? (
                <table border="1" style={{ width: '100%', textAlign: 'left' }}>
                    <thead>
                        <tr>                     
                            <th>Date</th>
                            <th>Time</th>
                            <th>Currency</th>
                            <th>Event</th>
                            <th>Actual</th>
                            <th>Forecast</th>
                            <th>Previous</th>
                           
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((item, index) => (
                            <tr key={index}>
                               
                               <td>{item.Date}</td>
                               <td>{item.Time}</td>
                                <td>{item.Currency}</td>
                                <td>{item.Event}</td>
                                <td>{item.Actual}</td>
                                <td>{item.Forecast}</td>
                                <td>{item.Previous}</td>
                                
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

export default FFCalendar;
