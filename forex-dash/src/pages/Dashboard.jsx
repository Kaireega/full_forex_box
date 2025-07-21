import React, { useEffect, useState } from 'react';
import endPoints from '../app/api';
import { COUNTS, GRANULARITIES, PAIRS } from '../app/data';
import Button from '../components/Button';
import PriceChart from '../components/PriceChart';
import Select from '../components/Select';
import Technicals from '../components/Technicals';
import TitleHead from '../components/TitleHead';
import TECalendar from '../components/TECalendar';
import FFCalendar from '../components/FFCalendar';

function Dashboard() {

  const [ selectedPair, setSelectedPair ] = useState(null);
  const [ selectedGran, setSelectedGran ] = useState(null);
  const [ technicalsData, setTechnicalsData ] = useState(null);
  const [ priceData, setPriceData ] = useState(null);
  const [ selectedCount, setSelectedCount ] = useState(COUNTS[0].value);
  const [ options, setOptions ] = useState(null);
  const [ loading, setLoading ] = useState(true);

  const [startDate, setStartDate] = useState(""); // Start date input
  const [endDate, setEndDate] = useState("");   // End date input
  const [calendarData, setCalendarData] = useState(null); // Calendar data from API
  const [loadingTE, setLoadingTE] = useState(false); // Loading state for TE Calendar

  const [ffstartDate, setffStartDate] = useState(""); // Start date input
  const [ffcalendarData, setffCalendarData] = useState(null); // Calendar data from API
  const [loadingFF, setLoadingFF] = useState(false); // Loading state for FF Calendar


  useEffect(() => {
    loadOptions();
  }, []);

  
    const loadffCalendarData = async () => {
      if (!ffstartDate) {
          alert("Please select start.", ffstartDate);
          return;
      }
      const formattStartDate = formatDate(ffstartDate);

      setLoadingFF(true);
      try {
          const data = await endPoints.ff_calendar(formattStartDate);
          setffCalendarData(data);
          console.log(data);
      } catch (error) {
          console.error("Error fetching calendar data:", error);
          alert("Failed to fetch calendar data.");
      } finally {
          setLoadingFF(false);
      }
  };

  const loadteCalendarData = async () => {
    if (!startDate || !endDate) {
        alert("Please select both start and end dates.");
        return;
    }
    const formattedStartDate = formatDateForAPI(startDate);
    const formattedEndDate = formatDateForAPI(endDate);

    setLoadingTE(true);
    try {
        const data = await endPoints.te_calendar(formattedStartDate, formattedEndDate);
        setCalendarData(data);
    } catch (error) {
        console.error("Error fetching calendar data:", error);
        alert("Failed to fetch calendar data.");
    } finally {
        setLoadingTE(false);
    }
  };
  
    // Format date to desired format
    const formatDate = (date) => {
      if (!date) return "";
      const months = ["Jan.", "Feb.", "Mar.", "Apr.", "May.", "Jun.", "Jul.", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."];
      const [year, month] = date.split("-");
      const formattedMonth = months[parseInt(month, 10) - 1];
      return `${formattedMonth}${year}`
  };

  const formatDateForAPI = (date) => {
      if (!date) return "";
      const d = new Date(date);
      return `${d.toISOString().split(".")[0]}Z`; // Convert to ISO format and append 'Z'
  };



  const handleCountChange = (count) => {
    setSelectedCount(count);
    loadPrices(count);
  }

  const loadOptions = async () => {
    const data = await endPoints.options();
    setOptions(data);
    setSelectedGran(data.granularities[0].value);
    setSelectedPair(data.pairs[0].value);
    setLoading(false);
  }

  const loadPrices = async (count) => {
    const data = await endPoints.prices(selectedPair, selectedGran, count);
    setPriceData(data);
  }

  const loadTechnicals = async () => {
    const data = await endPoints.technicals(selectedPair, selectedGran);
    setTechnicalsData(data);
    loadPrices(selectedCount);
  }

  if(loading === true) return <h1>Loading...</h1>

  return (
    <div>
  
      <div className="segment_options">
        <Select 
          name="Currency"
          title="Select currency"
          options={options.pairs}
          defaultValue={selectedPair}
          onSelected={setSelectedPair}
        />
        <Select 
          name="Granularity"
          title="Select granularity"
          options={options.granularities}
          defaultValue={selectedGran}
          onSelected={setSelectedGran}
        />
        <Button text="Load" handleClick={() => loadTechnicals()} />
      </div>
      <TitleHead title="Technicals" />
      { technicalsData && <Technicals data={technicalsData} /> }
  
      { priceData && <PriceChart
        selectedCount={selectedCount}
        selectedPair={selectedPair}
        selectedGranularity={selectedGran}
        handleCountChange={handleCountChange}
        priceData={priceData}
      />}

<TitleHead title="TradingEconomics - Economic Calendar" />
            <div className="segment_options">
                <div className="date-picker">
                    <label>
                        Start Date: 
                        <input 
                            type="date" 
                            value={startDate} 
                            onChange={(e) => setStartDate(e.target.value)} 
                        />
                    </label>
                    <label>
                        End Date: 
                        <input 
                            type="date" 
                            value={endDate} 
                            onChange={(e) => setEndDate(e.target.value)} 
                        />
                    </label>
                    <div></div>
                </div>
                <Button text="Fetch Data" handleClick={loadteCalendarData} />
            </div>
            
            {loadingTE ? <h1>Loading...</h1> : calendarData && <TECalendar data={calendarData} />}

            <TitleHead title="Forex Factory - Economic Calendar" />
            <div className="segment_options">
                <div className="date-picker">
                    <label>
                        Start Date: 
                        <input 
                            type="date" 
                            value={ffstartDate} 
                            onChange={(e) => setffStartDate(e.target.value)}
                        />
                    </label>
                    <div></div>
                </div>
                <Button text="Fetch Data" handleClick={loadffCalendarData} />
            </div>
           
            {loadingFF ? <h1>Loading...</h1> : ffcalendarData && <FFCalendar data={ffcalendarData} />}

    </div>
  )
}

export default Dashboard