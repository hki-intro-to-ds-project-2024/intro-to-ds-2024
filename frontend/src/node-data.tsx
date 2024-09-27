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
        const response = await axios.get('http://localhost:5000/nodes');
        
        console.log('Response For Node Request:', response);
        const backendNodes = Object.values(response.data); 

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
