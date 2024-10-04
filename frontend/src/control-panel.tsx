import * as React from 'react';

function ControlPanel() {
  return (
    <div className="control-panel">
      <h3>Welcome to Biketainer!</h3>
      <p>
        Use the parameters in the input box to find at-risk bike stands for breakage.  (Doesn't work yet)
      </p>

      <table>
        <tbody>
          <tr>
            <td><label htmlFor="minimum-zero-rides">Minimum number of zero-rides</label></td>
            <td><input id="minimum-zero-rides" type="number"></input></td>
          </tr>
          <tr>
            <td><label htmlFor="minimum-proportion">Minimum proportion of zero-rides</label></td>
            <td><input id="minimum-proportion" type="number" step="0.01"></input></td>
          </tr>
          <tr>
            <td><label htmlFor="date-start">Date start (YYYY-MM-DD)</label></td>
            <td><input id="date-start" type="date"></input></td>
          </tr>
          <tr>
            <td><label htmlFor="date-end">Date end (YYYY-MM-DD)</label></td>
            <td><input id="date-end" type="date"></input></td>
          </tr>
        </tbody>
      </table>
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