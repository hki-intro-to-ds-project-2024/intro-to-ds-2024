import * as React from 'react';

function ControlPanel() {
  return (
    <div className="control-panel">
      <h3>Bicycle map</h3>
      <p>
        Welcome to [bicycle bs project] : ) here you can see the map of the world for some reason.
      </p>
      <div className="links">
        <a
          href="https://github.com/hki-intro-to-ds-project-2024/intro-to-ds-2024/commits/main/"
          target="_new">
          Check out the repository ↗
        </a>
      </div>
    </div>
  );
}

export default React.memo(ControlPanel);