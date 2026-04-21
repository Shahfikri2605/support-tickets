import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';



const socket = io('http://192.168.0.122:5000'); 


const TEAM_SEQUENCE = [
  'Team A', 
  'Team B', 
  'Team C', 
  'Team D', 
  'Team E', 
  'Team F', 
  'Team G', 
  'Part Time',  
  'ALL' 
];

const SLIDE_DURATION = 10000;

function App() {
  const [data, setData] = useState([]);
  const [connected, setConnected] = useState(false);
  const scrollRef = useRef(null); // Reference for our scrolling container
  
  const tDate = new Date();
  tDate.setDate(tDate.getDate()-2);
  const targetDateStr = tDate.toISOString().split('T')[0];
  
  // --- STATE ---
  const [showSettings, setShowSettings] = useState(false);
  const [targetDate, setTargetDate] = useState(targetDateStr); 
  const [viewMode, setViewMode] = useState('daily'); 
  const [sortOrder, setSortOrder] = useState('highest'); 
  
  // --- CAROUSEL STATE ---
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false); // Pause when settings are open

  // 1. Socket Connection
  useEffect(() => {
    socket.on('connect', () => setConnected(true));
    socket.on('disconnect', () => setConnected(false));
    socket.on('refresh_dashboard', (incomingData) => setData(incomingData));

    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('refresh_dashboard');
    };
  }, []);

  // 2. The Automatic Timer (Carousel Logic)
  useEffect(() => {
    let interval;
    if (!isPaused && !showSettings) {
        interval = setInterval(() => {
            setCurrentIndex((prevIndex) => (prevIndex + 1) % TEAM_SEQUENCE.length);
        }, SLIDE_DURATION);
    }
    return () => clearInterval(interval);
  }, [isPaused, showSettings]);

  // --- HANDLERS ---
  const handleDateChange = (e) => {
    const newDate = e.target.value;
    setTargetDate(newDate);
    socket.emit('change_date', newDate);
  };

  // Determine which team is currently active
  const currentTeamFilter = TEAM_SEQUENCE[currentIndex];

  // --- SORTING & FILTERING ---
  const processedData = [...data]
    .filter(row => {
        // FILTER BY CURRENT CAROUSEL TEAM
        if (currentTeamFilter === 'ALL') return true;
        return row.team === currentTeamFilter;
    })
    .sort((a, b) => {
        // const valA = viewMode === 'daily' ? a.daily_qty : a.monthly_qty;
        // const valB = viewMode === 'daily' ? b.daily_qty : b.monthly_qty;
        let valA, valB;
        if (viewMode === 'daily'){
          valA = a.daily_qty;
          valB = b.daily_qty;
        }else if (viewMode === 'weekly'){
          valA = a.weekly_qty;
          valB = b.weekly_qty;
        }else{
          valA = a.monthly_qty;
          valB = b.monthly_qty;
        }
        if (sortOrder === 'highest') return valB - valA;
        return valA - valB;
    });

  useEffect(() => {
      const scrollContainer = scrollRef.current;
      if (!scrollContainer || processedData.length === 0) return;

      // Reset scroll position to top whenever the team changes
      scrollContainer.scrollTop = 0;

      let scrollSpeed = 7; // 40ms is a smooth reading pace
      
      const interval = setInterval(() => {
          // Move down 1 pixel
          scrollContainer.scrollTop += 1;

          // Check if we hit the bottom
          const isAtBottom = Math.ceil(scrollContainer.scrollTop + scrollContainer.clientHeight) >= scrollContainer.scrollHeight - 50;
          
          if (isAtBottom) {
              clearInterval(interval);
              // Wait 3 seconds at the bottom, then snap back to top
              setTimeout(() => {
                  scrollContainer.scrollTo({ top: 0, behavior: 'smooth' });
              }, 15000);
          }
      }, scrollSpeed);

      return () => clearInterval(interval);
  }, [currentIndex, processedData]);

  // Helper for Medals
  const getRankIcon = (index) => {
    if (sortOrder === 'lowest') return `#${index + 1}`; 
    if (index === 0) return '🥇'; 
    if (index === 1) return '🥈'; 
    if (index === 2) return '🥉'; 
    return index + 1;
  };

  // Helper for Colors
  const getTeamColor = (teamName) => {
      if (teamName === 'Team A') return '#FF5722'; 
      if (teamName === 'Team B') return '#2196F3'; 
      if (teamName === 'Team C') return '#9C27B0'; 
      if (teamName === 'Team D') return '#00BCD4'; 
      if (teamName === 'Team E') return '#4CAF50'; 
      if (teamName === 'Team F') return '#E91E63'; 
      if (teamName === 'Team G') return '#FFC107'; 
      if (teamName === 'Part Time') return '#607D8B'; 
      return '#555';
  };

  return (
    <div style={{ padding: '20px', backgroundColor: '#1e1e2e', minHeight: '100vh', color: '#fff', fontFamily: 'Arial, sans-serif' }}>
      
      {/* --- HEADER --- */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        
        {/* Connection Status */}
        <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ 
            width: '15px', height: '15px', borderRadius: '50%', marginRight: '10px',
            backgroundColor: connected ? '#4CAF50' : '#F44336',
            boxShadow: `0 0 8px ${connected ? '#4CAF50' : '#F44336'}`
            }} />
            <span style={{ fontSize: '0.8rem', color: '#888' }}>{connected ? 'LIVE' : 'OFFLINE'}</span>
        </div>

        {/* Dynamic Title */}
        <div style={{ textAlign: 'center' }}>
            <h1 style={{ color: '#4CAF50', margin: 0, fontSize: '2.5rem' }}>
            {viewMode === 'daily' ? '🏭 Daily Production' : '📅 Monthly Production'}
            </h1>
            <h2 style={{ margin: '5px 0 0 0', color: '#fff', fontSize: '1.8rem' }}>
                Displaying: <span style={{ color: '#FFC107', borderBottom: '2px solid #FFC107' }}>{currentTeamFilter}</span>
            </h2>
        </div>

        {/* Settings Button */}
        <div 
          onClick={() => setShowSettings(!showSettings)}
          style={{ cursor: 'pointer', fontSize: '2rem', background: '#333', padding: '10px', borderRadius: '50%' }}
        >
          ⚙️
        </div>
      </div>

      {/* --- PROGRESS BAR (Optional Visual Touch) --- */}
      <div style={{ width: '100%', height: '4px', backgroundColor: '#333', marginBottom: '20px', borderRadius: '2px' }}>
          <div style={{ 
              width: `${((currentIndex + 1) / TEAM_SEQUENCE.length) * 100}%`, 
              height: '100%', 
              backgroundColor: '#4CAF50',
              transition: 'width 0.5s ease'
          }} />
      </div>

      {/* --- SETTINGS MENU --- */}
      {showSettings && (
        <div style={{ backgroundColor: '#333', padding: '20px', borderRadius: '10px', marginBottom: '20px', border: '1px solid #555', display: 'flex', gap: '20px', flexWrap: 'wrap', justifyContent: 'center' }}>
          
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{color: '#aaa', fontSize: '0.8rem'}}>Target Date</label>
            <input type="date" value={targetDate} onChange={handleDateChange} style={{ padding: '10px', borderRadius: '5px', border: 'none', fontSize: '1rem' }} />
          </div>

          <div style ={{display: 'flex', flexDirection: 'column'}}>
            <label style={{color: '#aaa', fontSize: '0.8rem'}}>View Mode</label>
            <select value={viewMode} onChange={(e) => setViewMode(e.target.value)}
              style ={{padding: '10px', borderRadius: '5px', border:'none',fontSize: '1rem'}}>
                <option value="daily">Daily View</option>
                <option value="weekly">Weekly View</option>
                <option value="monthly">Monthly View</option>
              </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{color: '#aaa', fontSize: '0.8rem'}}>Force Specific Team (Pauses Cycle)</label>
            <select 
                value={currentTeamFilter} 
                onChange={(e) => {
                    const idx = TEAM_SEQUENCE.indexOf(e.target.value);
                    setCurrentIndex(idx);
                    setIsPaused(true); // Pause automatic cycling
                }} 
                style={{ padding: '10px', borderRadius: '5px', border: 'none', fontSize: '1rem', minWidth: '150px' }}
            >
                {TEAM_SEQUENCE.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{color: '#aaa', fontSize: '0.8rem'}}>Cycle Status</label>
            <button 
                onClick={() => setIsPaused(!isPaused)}
                style={{ 
                    padding: '10px', borderRadius: '5px', border: 'none', fontSize: '1rem', cursor: 'pointer',
                    backgroundColor: isPaused ? '#F44336' : '#2196F3', color: 'white'
                }}
            >
                {isPaused ? "▶️ Resume Cycle" : "⏸️ Pause Cycle"}
            </button>
          </div>

          <button onClick={() => setShowSettings(false)} style={{ backgroundColor: '#4CAF50', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '5px', cursor: 'pointer', alignSelf: 'flex-end' }}>Close</button>
        </div>
      )}

    

      {/* --- DATA TABLE --- */}
      <div 
        ref={scrollRef} 
        className="table-container"
        style={{ 
          maxHeight: '80vh',    // This forces the box to be 70% of the screen height
          overflowY: 'auto',    // This creates the scrollbar when rows overflow the box
          scrollbarWidth: 'none', // Hides scrollbar in Firefox
          msOverflowStyle: 'none' // Hides scrollbar in Edge
        }}
      >
        <table style={{ width: '100%', marginTop: '10px', borderCollapse: 'collapse', marginBottom: '100px' }}>
          <thead>
          <tr style={{ background: '#333', fontSize: '1.2rem', color: '#aaa' }}>
            <th style={{ padding: '15px' }}>Rank</th>
            <th style={{ padding: '15px', textAlign: 'left' }}>Staff Name</th>
            <th style={{ padding: '15px' }}>Team</th>
            <th style={{ padding: '15px' }}>{viewMode === 'daily' ? "Today's Output" : viewMode ==='weekly'? "Total This Week" : "Total This Month"}</th>
            {viewMode === 'daily' && <th style={{ padding: '15px' }}>Vs Yesterday</th>}
            <th style={{ padding: '15px' }}>Monthly Best Record</th>
          </tr>
        </thead>
        <tbody>
          {processedData.map((row, index) => (
            <tr key={index} style={{ borderBottom: '1px solid #444', fontSize: '1.4rem', textAlign: 'center' }}>
              <td style={{ fontSize: '2rem' }}>{getRankIcon(index)}</td>
              <td style={{ textAlign: 'left', fontWeight: 'bold' }}>{row.name}</td>
              <td>
                <span style={{ backgroundColor: getTeamColor(row.team), padding: '5px 10px', borderRadius: '15px', fontSize: '1rem', fontWeight: 'bold', color: 'white' }}>
                    {row.team}
                </span>
              </td>
              <td style={{ color: '#4CAF50', fontWeight: 'bold', fontSize: '1.8rem' }}>
                {viewMode === 'daily' ? row.daily_qty : viewMode ==='weekly' ? row.weekly_qty:row.monthly_qty}
              </td>
              {viewMode === 'daily' && (
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: row.diff > 0 ? '#4CAF50' : row.diff < 0 ? '#F44336' : '#888' }}>
                    {row.diff > 0 ? '▲' : row.diff < 0 ? '▼' : ''} 
                    <span style={{ fontSize: '1rem', marginLeft: '5px' }}>{row.diff !== 0 ? Math.abs(row.diff) : '-'}</span>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#888' }}>(Yes: {row.yesterday_qty})</div>
                </td>
              )}
              <td style={{ color: '#FFC107' }}>🏆 {row.month_max}</td>
            </tr>
          ))}

          

     
          {/* EMPTY STATE - Show this if a team has no data for the day */}
          {processedData.length === 0 && (
              <tr>
                  <td colSpan="6" style={{ padding: '50px', textAlign: 'center', color: '#666', fontStyle: 'italic', fontSize: '1.5rem' }}>
                      💤 No production data found for {currentTeamFilter} today.
                  </td>
              </tr>
          )}
        </tbody>
      </table>
      </div> {/* This closes the new table-container div */}
    </div>
  );
}

export default App;
