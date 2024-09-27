import React, {useEffect} from 'react';
import axios from 'axios'

import {ControlPosition, Map, MapControl} from '@vis.gl/react-google-maps';

import {useDrawingManager} from './use-drawing-manager';
import ControlPanel from './control-panel';

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
    return (
    <>
        <ControlPanel />        
        <Map
            defaultZoom={12}
            defaultCenter={{lat: 60.192059, lng: 24.945831}}
            gestureHandling={'greedy'}
            disableDefaultUI={true}
        />
    </>
    );
};

export default BikeMap;