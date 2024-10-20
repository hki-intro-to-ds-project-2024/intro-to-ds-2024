import React, { useState, useCallback } from 'react';
import {
  AdvancedMarker,
  AdvancedMarkerProps,
  AdvancedMarkerContext,
  InfoWindow,
  Map,
  Pin,
  useAdvancedMarkerRef
} from '@vis.gl/react-google-maps';

import ControlPanel from './control-panel';
import useNodeData from './node-data';

export type AnchorPointName = keyof typeof AdvancedMarkerContext;
const BikeMap = () => {  
  const [dateStart, setDateStart] = useState<string | null>('2016-01-01');
  const [dateEnd, setDateEnd] = useState<string | null>('2026-01-01');
  const [timeStart, setTimeStart] = useState<string | null>('00:00');
  const [timeEnd, setTimeEnd] = useState<string | null>('00:00');
  const [zeroRides, setZeroRides] = useState(0);
  const [proportion, setProportion] = useState(0.0);

  const nodes = useNodeData({ zeroRides, proportion, dateStart, dateEnd, timeStart, timeEnd });
  const Z_INDEX_SELECTED = nodes.length;
  const Z_INDEX_HOVER = nodes.length + 1;

  const [hoverId, setHoverId] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [anchorPoint, setAnchorPoint] = useState('BOTTOM' as AnchorPointName);
  const [selectedMarker, setSelectedMarker] =
    useState<google.maps.marker.AdvancedMarkerElement | null>(null);
  const [infoWindowShown, setInfoWindowShown] = useState(false);

  const onMouseEnter = useCallback((id: string | null) => setHoverId(id), []);
  const onMouseLeave = useCallback(() => setHoverId(null), []);
  const onMarkerClick = useCallback(
    (id: string | null, marker?: google.maps.marker.AdvancedMarkerElement) => {
      setSelectedId(id);

      if (marker) {
        setSelectedMarker(marker);
      }

      if (id !== selectedId) {
        setInfoWindowShown(true);
      } else {
        setInfoWindowShown(isShown => !isShown);
      }
    },
    [selectedId]
  );

  const onMapClick = useCallback(() => {
    setSelectedId(null);
    setSelectedMarker(null);
    setInfoWindowShown(false);
  }, []);

  const handleInfowindowCloseClick = useCallback(
    () => setInfoWindowShown(false),
    []
  );

  const updateNodes = (newZeroRides: number, newProportion: number, newDateStart: string | null, newDateEnd: string | null,
     newTimeStart: string | null, newTimeEnd: string | null) => {
    console.log("old parameters:", zeroRides, proportion, dateStart, dateEnd, timeStart, timeEnd);
    setZeroRides(newZeroRides);
    setProportion(newProportion);
    setDateStart(newDateStart);
    setDateEnd(newDateEnd);
    setTimeStart(newTimeStart);
    setTimeEnd(newTimeEnd);
    console.log("new parameters:", newZeroRides, newProportion, newDateStart, newDateEnd, newTimeStart, newTimeEnd);
  };

  return (
    <>
      <ControlPanel
        zeroRides={zeroRides}
        proportion={proportion}
        dateStart={dateStart}
        dateEnd={dateEnd}
        timeStart={timeStart}
        timeEnd={timeEnd}
        updateNodes={updateNodes}
      />
      <Map
        mapId={'someMapId'}
        defaultZoom={12}
        defaultCenter={{ lat: 60.192059, lng: 24.945831 }}
        gestureHandling={'greedy'}
        disableDefaultUI={true}
        onClick={onMapClick}
      >
        {nodes.map(({ id, zIndex: zIndexDefault, position, type }) => {
          let zIndex = zIndexDefault;

          if (hoverId === id) {
            zIndex = Z_INDEX_HOVER;
          }

          if (selectedId === id) {
            zIndex = Z_INDEX_SELECTED;
          }

          if (type === 'pin') {
            return (
              <AdvancedMarkerWithRef
                key={id}
                onMarkerClick={(
                  marker: google.maps.marker.AdvancedMarkerElement
                ) => onMarkerClick(id, marker)}
                onMouseEnter={() => onMouseEnter(id)}
                onMouseLeave={onMouseLeave}
                zIndex={zIndex}
                className="custom-marker"
                style={{
                  transform: `scale(${[hoverId, selectedId].includes(id) ? 1.4 : 1})`
                }}
                position={position}
              >
                <Pin
                  background={selectedId === id ? '#22ccff' : undefined}
                  borderColor={selectedId === id ? '#1e89a1' : undefined}
                  glyphColor={selectedId === id ? '#0f677a' : undefined}
                />
              </AdvancedMarkerWithRef>
            );
          }

          if (type === 'html') {
            return (
              <React.Fragment key={id}>
                <AdvancedMarkerWithRef
                  position={position}
                  zIndex={zIndex}
                  anchorPoint={AdvancedMarkerContext[anchorPoint]}
                  className="custom-marker"
                  style={{
                    transform: `scale(${[hoverId, selectedId].includes(id) ? 1.4 : 1})`
                  }}
                  onMarkerClick={(
                    marker: google.maps.marker.AdvancedMarkerElement
                  ) => onMarkerClick(id, marker)}
                  onMouseEnter={() => onMouseEnter(id)}
                  onMouseLeave={onMouseLeave}
                >
                  <div
                    className={`custom-html-content ${selectedId === id ? 'selected' : ''}`}
                  ></div>
                </AdvancedMarkerWithRef>

                {/* anchor point visualization marker */}
                <AdvancedMarkerWithRef
                  onMarkerClick={(
                    marker: google.maps.marker.AdvancedMarkerElement
                  ) => onMarkerClick(id, marker)}
                  zIndex={zIndex}
                  onMouseEnter={() => onMouseEnter(id)}
                  onMouseLeave={onMouseLeave}
                  anchorPoint={AdvancedMarkerContext.CENTER}
                  position={position}
                >
                  <div className="visualization-marker"></div>
                </AdvancedMarkerWithRef>
              </React.Fragment>
            );
          }

          return null;
        })}

        {infoWindowShown && selectedMarker && (
          <InfoWindow
            anchor={selectedMarker}
            onCloseClick={handleInfowindowCloseClick}
          >
            <h2>Marker {selectedId}</h2>
            <p>Some arbitrary html to be rendered into the InfoWindow.</p>
          </InfoWindow>
        )}
      </Map>
    </>
  );
};

export const AdvancedMarkerWithRef = (
  props: AdvancedMarkerProps & {
    onMarkerClick: (marker: google.maps.marker.AdvancedMarkerElement) => void;
  }
) => {
  const { children, onMarkerClick, ...advancedMarkerProps } = props;
  const [markerRef, marker] = useAdvancedMarkerRef();

  return (
    <AdvancedMarker
      onClick={() => {
        if (marker) {
          onMarkerClick(marker);
        }
      }}
      ref={markerRef}
      {...advancedMarkerProps}
    >
      {children}
    </AdvancedMarker>
  );
};

export default BikeMap;
