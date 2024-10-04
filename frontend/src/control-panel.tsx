import * as React from 'react';

function ControlPanel() {
  return (
    <div className="control-panel">
      <h3>Welcome to Biketainer!</h3>
      <p>
        Use the parameters in the input box to find at-risk bike stands for breakage. 
      </p>

      <label htmlFor="minimum-zero-rides">Minimum number of zero-rides</label>
      <input id="minimum-zero-rides" type="number"></input>
      <div></div>
      <label htmlFor="minimum-proportion">Minimum proportion of zero-rides</label>
      <input id="minimum-proportion" type="number" step="0.01"></input>
      <div></div>
      <label htmlFor="date-start">Date start (YYYY-MM-DD)</label>
      <input id="date-start" type="date"></input>
      <div></div>
      <label htmlFor="date-end">Date end (YYYY-MM-DD)</label>
      <input id="date-end" type="date"></input>
      <div></div>
      <button type="button">Update Map</button>

      <div className="links" style={{float: 'right', marginRight: '0em', marginTop: '-1.5em', position: 'absolute', right: 0, zIndex: 1000}}>
        <a
          href="https://github.com/hki-intro-to-ds-project-2024/intro-to-ds-2024"
          target="_new">
          View Source Code ↗
        </a>
      </div>
    </div>
  );
}

export default React.memo(ControlPanel);