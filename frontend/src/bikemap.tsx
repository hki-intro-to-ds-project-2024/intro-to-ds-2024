// bikemap.tsx

import React, { useState, useCallback } from 'react';
import {
  AdvancedMarker,
  AdvancedMarkerProps,
  AdvancedMarkerContext,
  InfoWindow,
  Map,
  Pin,
  useAdvancedMarkerRef,
} from '@vis.gl/react-google-maps';

import ControlPanel from './control-panel';
import useNodeData from './node-data';

export type AnchorPointName = keyof typeof AdvancedMarkerContext;

const BikeMap = () => {
  const [dateStart, setDateStart] = useState<string>('2019-06-01');
  const [dateEnd, setDateEnd] = useState<string>('2019-06-02');
  const [timeStart, setTimeStart] = useState<string>('00:00');
  const [timeEnd, setTimeEnd] = useState<string>('23:59');
  const [zeroRides, setZeroRides] = useState<number>(0);
  const [proportion, setProportion] = useState<number>(0.0);

  const { data: nodes, accuracy } = useNodeData({
    zeroRides,
    proportion,
    dateStart,
    dateEnd,
    timeStart,
    timeEnd,
  });
  const Z_INDEX_SELECTED = nodes.length;
  const Z_INDEX_HOVER = nodes.length + 1;

  const [hoverId, setHoverId] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [anchorPoint] = useState('BOTTOM' as AnchorPointName);
  const [selectedMarker, setSelectedMarker] =
    useState<google.maps.marker.AdvancedMarkerElement | null>(null);
  const [infoWindowShown, setInfoWindowShown] = useState<boolean>(false);

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
        setInfoWindowShown((isShown) => !isShown);
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

  const updateNodes = (
    newZeroRides: number,
    newProportion: number,
    newDateStart: string,
    newDateEnd: string,
    newTimeStart: string,
    newTimeEnd: string
  ) => {
    console.log(
      'old parameters:',
      zeroRides,
      proportion,
      dateStart,
      dateEnd,
      timeStart,
      timeEnd
    );
    setZeroRides(newZeroRides);
    setProportion(newProportion);
    setDateStart(newDateStart);
    setDateEnd(newDateEnd);
    setTimeStart(newTimeStart);
    setTimeEnd(newTimeEnd);
    console.log(
      'new parameters:',
      newZeroRides,
      newProportion,
      newDateStart,
      newDateEnd,
      newTimeStart,
      newTimeEnd
    );
  };

  // Find the selected node to access its properties in the InfoWindow
  const selectedNode = nodes.find((node) => node.id === selectedId);

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
        accuracy={accuracy}
      />
      <Map
        mapId={'someMapId'}
        defaultZoom={12}
        defaultCenter={{ lat: 60.192059, lng: 24.945831 }}
        gestureHandling={'greedy'}
        disableDefaultUI={true}
        onClick={onMapClick}
      >
        {nodes.map(({ id, zIndex: zIndexDefault, position, type, source }) => {
          let zIndex = zIndexDefault;

          if (hoverId === id) {
            zIndex = Z_INDEX_HOVER;
          }

          if (selectedId === id) {
            zIndex = Z_INDEX_SELECTED;
          }

          if (type === 'pin' || type === 'prediction') {
            const isPrediction = source === 'predictions';

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
                  transform: `scale(${
                    [hoverId, selectedId].includes(id) ? 1.4 : 1
                  })`,
                }}
                position={position}
              >
                <Pin
                  background={
                    selectedId === id
                      ? '#22ccff'
                      : isPrediction
                      ? '#ffcc00'
                      : undefined
                  }
                  borderColor={
                    selectedId === id
                      ? '#1e89a1'
                      : isPrediction
                      ? '#ff9900'
                      : undefined
                  }
                  glyphColor={
                    selectedId === id
                      ? '#0f677a'
                      : isPrediction
                      ? '#cc6600'
                      : undefined
                  }
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
                    transform: `scale(${
                      [hoverId, selectedId].includes(id) ? 1.4 : 1
                    })`,
                  }}
                  onMarkerClick={(
                    marker: google.maps.marker.AdvancedMarkerElement
                  ) => onMarkerClick(id, marker)}
                  onMouseEnter={() => onMouseEnter(id)}
                  onMouseLeave={onMouseLeave}
                >
                  <div
                    className={`custom-html-content ${
                      selectedId === id ? 'selected' : ''
                    }`}
                  ></div>
                </AdvancedMarkerWithRef>

                {/* Anchor point visualization marker */}
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

        {infoWindowShown && selectedMarker && selectedNode && (
          <InfoWindow
            anchor={selectedMarker}
            onCloseClick={handleInfowindowCloseClick}
          >
            <h2>
              {selectedNode.source === 'predictions' ? 'Prediction' : 'Marker'}{' '}
              {selectedId}
            </h2>
            <p>
              {selectedNode.source === 'predictions'
                ? 'This is a predicted at-risk bike stand.'
                : 'This is an existing bike stand.'}
            </p>
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
