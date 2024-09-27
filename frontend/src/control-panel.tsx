import * as React from 'react';

function ControlPanel() {
  return (
    <div className="control-panel">
      <h3>Helsinki Bicycle Map Project</h3>
      <p>
        Click on the map to add an additional bike stop and see how it affects the other edges.
      </p>
      <div className="links">
        <a
          href="https://codesandbox.io/s/github/visgl/react-google-maps/tree/main/examples/drawing"
          target="_new">
          Try on CodeSandbox ↗
        </a>

        <a
          href="https://github.com/visgl/react-google-maps/tree/main/examples/drawing"
          target="_new">
          View Code ↗
        </a>
      </div>
    </div>
  );
}

export default React.memo(ControlPanel);