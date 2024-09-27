import React, {useState, useCallback, useEffect} from 'react';
import axios from 'axios'

import {
    ControlPosition,
    AdvancedMarker,
    AdvancedMarkerProps,
    APIProvider,
    AdvancedMarkerContext,
    InfoWindow,
    Map,
    Pin,
    useAdvancedMarkerRef
  } from '@vis.gl/react-google-maps';


import {useDrawingManager} from './use-drawing-manager';
import ControlPanel from './control-panel';

import getData from './node-data';

const data = getData()
  .sort((a, b) => b.position.lat - a.position.lat)
  .map((dataItem, index) => ({...dataItem, zIndex: index}));

export type AnchorPointName = keyof typeof AdvancedMarkerContext;

const Z_INDEX_SELECTED = data.length;
const Z_INDEX_HOVER = data.length + 1;

const BikeMap = () => {
    useEffect(() => {
        console.log('effect')
        axios
          .get('http://localhost:5000/nodes')
          .then(response => {
            console.log(response.data)
          })
      }, [])
    
    const drawingManager = useDrawingManager();
    const [markers] = useState(data);

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
  

    return (
    <>
        <ControlPanel />        
        <Map
            mapId={'someMapId'}
            defaultZoom={12}
            defaultCenter={{lat: 60.192059, lng: 24.945831}}
            gestureHandling={'greedy'}
            disableDefaultUI={true}>
        {markers.map(({id, zIndex: zIndexDefault, position, type}) => {
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
                onMarkerClick={(
                  marker: google.maps.marker.AdvancedMarkerElement
                ) => onMarkerClick(id, marker)}
                onMouseEnter={() => onMouseEnter(id)}
                onMouseLeave={onMouseLeave}
                key={id}
                zIndex={zIndex}
                className="custom-marker"
                style={{
                  transform: `scale(${[hoverId, selectedId].includes(id) ? 1.4 : 1})`
                }}
                position={position}>
                <Pin
                  background={selectedId === id ? '#22ccff' : null}
                  borderColor={selectedId === id ? '#1e89a1' : null}
                  glyphColor={selectedId === id ? '#0f677a' : null}
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
                  onMouseLeave={onMouseLeave}>
                  <div
                    className={`custom-html-content ${selectedId === id ? 'selected' : ''}`}></div>
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
                  position={position}>
                  <div className="visualization-marker"></div>
                </AdvancedMarkerWithRef>
              </React.Fragment>
            );
          }
        })}

        {infoWindowShown && selectedMarker && (
          <InfoWindow
            anchor={selectedMarker}
            onCloseClick={handleInfowindowCloseClick}>
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
    const {children, onMarkerClick, ...advancedMarkerProps} = props;
    const [markerRef, marker] = useAdvancedMarkerRef();
  
    return (
      <AdvancedMarker
        onClick={() => {
          if (marker) {
            onMarkerClick(marker);
          }
        }}
        ref={markerRef}
        {...advancedMarkerProps}>
        {children}
      </AdvancedMarker>
    );
  };

export default BikeMap;