import axios from 'axios';
import { useEffect, useState } from 'react';

type LatLngLiteral = {
  lat: number;
  lng: number;
};

type NodeData = Array<{
  id: string;
  position: LatLngLiteral;
  type: 'pin' | 'html';
  zIndex: number;
}>;

const useNodeData = () => {
  const [data, setData] = useState<NodeData>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:5000/nodes?time_start=2022-01-01T00:00:00&time_end=2025-01-02T00:00:00&zero_rides=3&proportion=0.25');
        
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
  }, []);
  

  return data;
};

export default useNodeData;
