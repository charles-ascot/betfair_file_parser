// MarketBrowser.jsx
import { useState } from 'react';

export default function MarketBrowser({ markets }) {
  const [selectedMarket, setSelectedMarket] = useState(null);

  if (!markets || markets.length === 0) {
    return <div className="market-browser"><p>No markets to display</p></div>;
  }

  return (
    <div className="market-browser">
      <h2>Market Browser</h2>
      <div className="markets-list">
        {markets.map((market) => (
          <div 
            key={market.market_id} 
            className={`market-item ${selectedMarket?.market_id === market.market_id ? 'active' : ''}`}
            onClick={() => setSelectedMarket(market)}
          >
            <h3>{market.market_name}</h3>
            <p>{market.number_of_runners} runners</p>
          </div>
        ))}
      </div>
      
      {selectedMarket && (
        <div className="market-details">
          <h3>{selectedMarket.market_name}</h3>
          <p>Total Matched: {selectedMarket.total_matched}</p>
          <p>Runners: {selectedMarket.number_of_runners}</p>
        </div>
      )}
    </div>
  );
}