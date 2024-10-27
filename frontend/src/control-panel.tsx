// control-panel.tsx

import * as React from 'react';

function ControlPanel({
  zeroRides,
  proportion,
  dateStart,
  dateEnd,
  timeStart,
  timeEnd,
  updateNodes,
  accuracy,
}) {
  const [localZeroRides, setLocalZeroRides] = React.useState(zeroRides);
  const [localProportion, setLocalProportion] = React.useState(proportion);
  const [localDateStart, setLocalDateStart] = React.useState(dateStart);
  const [localTimeStart, setLocalTimeStart] = React.useState(timeStart);
  const [localDateEnd, setLocalDateEnd] = React.useState(dateEnd);
  const [localTimeEnd, setLocalTimeEnd] = React.useState(timeEnd);

  const handleSubmit = () => {
    console.log(
      'Parameters:',
      localZeroRides,
      localProportion,
      localDateStart,
      localDateEnd,
      localTimeStart,
      localTimeEnd
    );
    updateNodes(
      localZeroRides,
      localProportion,
      localDateStart,
      localDateEnd,
      localTimeStart,
      localTimeEnd
    );
  };

  return (
    <div className="controlPanel">
      <h3>Welcome to Biketainer!</h3>
      <p>
        Use the parameters in the input box to find at-risk bike stands for
        breakage.
      </p>
      <table>
        <tbody>
          <tr>
            <td>
              <label htmlFor="minimumZeroRides">Minimum number of zero-rides</label>
            </td>
            <td>
              <input
                id="minimumZeroRides"
                type="number"
                step="1"
                value={localZeroRides}
                onChange={(e) => setLocalZeroRides(Number(e.target.value))}
              />
            </td>
          </tr>
          <tr>
            <td>
              <label htmlFor="minimumProportion">Minimum proportion of zero-rides</label>
            </td>
            <td>
              <input
                id="minimumProportion"
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={localProportion}
                onChange={(e) => setLocalProportion(Number(e.target.value))}
              />
              <span id="minimumProportionValue">{localProportion.toFixed(2)}</span>
            </td>
          </tr>
          <tr>
            <td>
              <label htmlFor="dateStart">Date start (YYYY-MM-DD)</label>
            </td>
            <td>
              <input
                id="dateStart"
                type="date"
                value={localDateStart}
                onChange={(e) => setLocalDateStart(e.target.value)}
              />
              <input
                id="timeStart"
                type="time"
                value={localTimeStart}
                onChange={(e) => setLocalTimeStart(e.target.value)}
              />
            </td>
          </tr>
          <tr>
            <td>
              <label htmlFor="dateEnd">Date end (YYYY-MM-DD)</label>
            </td>
            <td>
              <input
                id="dateEnd"
                type="date"
                value={localDateEnd}
                onChange={(e) => setLocalDateEnd(e.target.value)}
              />
              <input
                id="timeEnd"
                type="time"
                value={localTimeEnd}
                onChange={(e) => setLocalTimeEnd(e.target.value)}
              />
            </td>
          </tr>
        </tbody>
      </table>
      <button type="button" onClick={handleSubmit}>
        Update Map
      </button>

      {/* Display Accuracy */}
      {accuracy !== null && (
        <div className="accuracy">
          <p>
            Prediction Accuracy: <strong>{accuracy.toFixed(2)}%</strong>
          </p>
        </div>
      )}

      <div
        className="links"
        style={{
          float: 'right',
          marginRight: '0em',
          marginTop: '-1.5em',
          position: 'absolute',
          right: 0,
          zIndex: 1000,
        }}
      >
        <a
          href="https://github.com/hki-intro-to-ds-project-2024/intro-to-ds-2024"
          target="_new"
        >
          View Source Code
        </a>
      </div>
    </div>
  );
}

export default React.memo(ControlPanel);
