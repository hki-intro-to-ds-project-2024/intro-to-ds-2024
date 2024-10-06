import * as React from 'react';
import axios from 'axios'


function ControlPanel() {
  const [zero_values, set_zeros] = React.useState(0)
  const [zero_proportions, set_proportions] = React.useState(0.0)
  const [start_data, set_start_date] = React.useState()
  const [start_time, set_start_time] = React.useState()
  const [end_date, set_end_date] = React.useState()
  const [end_time, set_end_time] = React.useState()

  const handle_zeros_value = (event) => set_zeros(event.target.value)
  const handle_proportion = (event) => {
    set_proportions(event.currentTarget.value)
    document.getElementById('minimum-proportion-value')!.innerHTML = event.currentTarget.value
  }

  const handle_start_date = (event) => set_start_date(event.target.value)
  const handle_start_time = (event) => set_start_time(event.target.value)
  const handle_end_date = (event) => set_end_date(event.target.value)
  const handle_end_time = (event) => set_end_time(event.target.value)


  //handle data submition
  const submit_parameters = () => {
    //get data from server
    const url = "http://127.0.0.1:5000/nodes?time_start="+start_data+"T"+start_time+"&time_end="+end_date+"T"+end_time
    +"&zero_rides="+zero_values+"&proportion="+zero_proportions

    axios.get(url).then(response => console.log(response.data))
  }
  
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
            <td><input id="minimum-zero-rides" type="number" step="1" value={zero_values} onChange={handle_zeros_value}/></td>
          </tr>
          <tr>
            <td><label htmlFor="minimum-proportion">Minimum proportion of zero-rides</label></td>
            <td>
              <input
                id="minimum-proportion"
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={zero_proportions}
                onChange={handle_proportion}
              />
              <span id="minimum-proportion-value">1</span>
            </td>
          </tr>
          <tr>
            <td><label htmlFor="date-start">Date start (YYYY-MM-DD HH:MM:SS)</label></td>
            <td>
              <input id="date-start-date" type="date" value={start_data} onChange={handle_start_date} />
              <input id="date-start-time" type="time" value={start_time} onChange={handle_start_time}/>
            </td>
          </tr>
          <tr>
            <td><label htmlFor="date-end">Date end (YYYY-MM-DD HH:MM:SS)</label></td>
            <td>
              <input id="date-end-date" type="date" value={end_date} onChange={handle_end_date}></input>
              <input id="date-end-time" type="time" value={end_time} onChange={handle_end_time}></input>
            </td>
          </tr>
        </tbody>
      </table>
      <button type="button" onClick={submit_parameters}>Update Map</button>

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