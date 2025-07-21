import React from 'react';
import './Cheatsheet.css';
import TitleHead from '../components/TitleHead';


function CheatSheet() {
  return ( 
    <>
        <div className="cheatsheet">
        <h1>Trade Checklist</h1>

        <div className="row">
            <div className="section">
            <TitleHead title="Trend Analysis"/>
            <ol>
                <li>Identify uptrend, downtrend, or range.</li>
                <li>Support/Resistance Levels: Mark critical price zones.</li>
                <li>Confirm with Indicators: RSI, MACD, or others.</li>
                <li>Set Entry, SL, and TP: Define risk/reward.</li>
                <li>Monitor News: Ensure no major event clashes.</li>
                <li>Execute and Monitor: Adjust if needed, don't overmanage.</li>
            </ol>
            </div>

            <div className="section">
            <TitleHead title="Risk Management Tips"/>

            <ul>
                <li>Risk-Reward Ratio: Aim for at least 1:2.</li>
                <li>Position Sizing: Risk 1-2% of account balance per trade.</li>
                <li>Leverage Management: Use conservative leverage (e.g., 1:10).</li>
                <li>Set Stop Loss: Avoid emotional decision-making.</li>
                <li>Avoid Overtrading: Stick to a trading plan.</li>
            </ul>
            </div>

            <div className="section">
          
            <TitleHead title="Candlestick Patterns"/>
            
            <ul>
                <li>
                Bullish Reversal:
                <ul>
                    <li>Hammer, Morning Star, Engulfing (bullish).</li>
                </ul>
                </li>
                <li>
                Bearish Reversal:
                <ul>
                    <li>Shooting Star, Evening Star, Engulfing (bearish).</li>
                </ul>
                </li>
                <li>
                Indecision/Neutral:
                <ul>
                    <li>Doji, Spinning Top.</li>
                </ul>
                </li>
            </ul>
            </div>
        </div>

        <div className="row">
            <div className="section">
            <TitleHead title="Common Chart Patterns"/>

            <ul>
                <li>
                Reversal Patterns:
                <ul>
                    <li>Head and Shoulders: Signals a reversal from uptrend to downtrend.</li>
                    <li>Double Top/Bottom: Indicates a reversal after two peaks/troughs.</li>
                </ul>
                </li>
                <li>
                Continuation Patterns:
                <ul>
                    <li>Flags and Pennants: Suggest continuation of the current trend.</li>
                    <li>Ascending/Descending Triangles: Breakouts in the trend direction.</li>
                </ul>
                </li>
            </ul>
            </div>

            <div className="section">
        
            <TitleHead title="Key Forex Terms"/>

            <p>Include definitions of key terms, like pips, lots, leverage, margin, etc.</p>
            </div>

            <div className="section">
            <TitleHead title="Popular Forex Strategies"/>

            <ol>
                <li>
                Scalping:
                <ul>
                    <li>Focus: Short-term trades (minutes).</li>
                    <li>Indicators: 1-minute charts, RSI, Bollinger Bands.</li>
                </ul>
                </li>
                <li>
                Day Trading:
                <ul>
                    <li>Focus: No overnight positions.</li>
                    <li>Tools: 15-minute to 1-hour charts, Moving Averages.</li>
                </ul>
                </li>
                <li>
                Swing Trading:
                <ul>
                    <li>Focus: Capture price swings over days/weeks.</li>
                    <li>Tools: Daily/4H charts, trendlines, Fibonacci retracement.</li>
                </ul>
                </li>
            </ol>
            </div>
        </div>

            <div>
                <TitleHead title="Economic Events to Watch"/>

                    <table border="3">
                    <thead >
                        <tr>
                        <th className='th_c'>Event</th>
                        <th className='th_c'>Impacted Pairs</th>
                        <th className='th_c'>Effect</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Non-Farm Payrolls (NFP)</td>
                            <td>USD pairs</td>
                            <td>High volatility</td>
                        </tr>
                        <tr>
                            <td>Interest Rate Decisions</td>
                            <td>All major currencies</td>
                            <td>Trend formation</td>
                        </tr>
                        <tr>
                            <td>GDP Reports</td>
                            <td>Major pairs</td>
                            <td>Economic strength</td>
                        </tr>
                        <tr>
                            <td>CPI (Inflation) Reports</td>
                            <td>Major pairs</td>
                            <td>Inflation impact</td>
                        </tr>
                        <tr>
                            <td>Central Bank Statements</td>
                            <td>All currencies</td>
                            <td>Market sentiment shifts</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div>
                <TitleHead title="Key Trading Sessions"/>
                    <table border="3">
                    <thead>
                        <tr>
                        <th className='th_c'>Session</th>
                        <th className='th_c'>Major Markets</th>
                        <th className='th_c'>Key Pairs</th>
                        <th className='th_c'> Volatility</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Tokyo</td>
                            <td>Japan, Australia</td>
                            <td>AUD/USD, USD/JPY</td>
                            <td>Low-Medium</td>
                        </tr>
                        <tr>
                            <td>London</td>
                            <td>UK, Europe</td>
                            <td>EUR/USD, GBP/USD</td>
                            <td>High</td>
                        </tr>
                        <tr>
                            <td>New York</td>
                            <td>US, Canada</td>
                            <td>USD/CAD, USD/JPY</td>
                        <td>High</td>
                        </tr>
                        <tr>
                            <td>Overlap (Lon-NY)</td>
                            <td>London, New York</td>
                            <td>Major pairs</td>
                            <td>Highest</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </>
 
)}

export default CheatSheet