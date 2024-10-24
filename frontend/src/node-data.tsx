import axios from 'axios';
import { useEffect, useState } from 'react';

type LatLngLiteral = {
  lat: number;
  lng: number;
};

export type NodeData = Array<{
  id: string;
  position: LatLngLiteral;
  type: 'pin' | 'html';
  zIndex: number;
}>;
const useNodeData = (props) => {
  const [data, setData] = useState<NodeData>([]);

  console.log("Called useNodeData with:", props.zeroRides, props.proportion, props.dateStart, props.dateEnd, props.timeStart, props.timeEnd);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/nodes?time_start=${props.dateStart}T00:00:00&time_end=${props.dateEnd}T00:00:00&zero_rides=${props.zeroRides}&proportion=${props.proportion}`);
        
        console.log('Response For Node Request:', response);
        const backendNodes = Object.values(response.data); 
  
        console.log("Response data:", backendNodes);
  
        const newData = backendNodes.map((node: any) => ({
          id: node.id,
          position: {
            lat: node.position.lat,
            lng: node.position.lng,
          },
          zIndex: node.id, 
          type: 'pin', 
        }));
  
        setData(newData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
  
    fetchData();
  }, [props.zeroRides,
    props.proportion,
    props.dateStart,
    props.dateEnd,
    props.timeStart,
    props.timeEnd]);
  

  return data;
};

export default useNodeData;
