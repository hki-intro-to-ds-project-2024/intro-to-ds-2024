import axios from 'axios';
import { useEffect, useState } from 'react';

type LatLngLiteral = {
  lat: number;
  lng: number;
};

export type Node = {
  id: string;
  position: LatLngLiteral;
  // Include other properties if necessary
};

export type NodeDataItem = Node & {
  type: 'pin' | 'html' | 'prediction';
  zIndex: number;
  source: 'nodes' | 'predictions';
};

export type NodeData = NodeDataItem[];

const useNodeData = (props) => {
  const [data, setData] = useState<NodeData>([]);
  const [accuracy, setAccuracy] = useState<number | null>(null);

  console.log(
    'Called useNodeData with:',
    props.zeroRides,
    props.proportion,
    props.dateStart,
    props.dateEnd,
    props.timeStart,
    props.timeEnd
  );

  useEffect(() => {
    const fetchData = async () => {
      try {
        const nodesResponse = await axios.get(
          `http://127.0.0.1:5000/nodes?time_start=${props.dateStart}T${props.timeStart}:00&time_end=${props.dateEnd}T${props.timeEnd}:00&zero_rides=${props.zeroRides}&proportion=${props.proportion}`
        );
        console.log('Response For Node Request:', nodesResponse);
        const backendNodes = nodesResponse.data as Node[];
        console.log('Response data:', backendNodes);

        const predResponse = await axios.get(
          `http://127.0.0.1:5000/predictions?time_start=${props.dateStart}T${props.timeStart}:00&time_end=${props.dateEnd}T${props.timeEnd}:00&zero_rides=${props.zeroRides}`
        );
        console.log('Response For prediction request:', predResponse);
        const predNodes = predResponse.data as Node[];
        console.log('Response data:', predNodes);

        const actualPositions = new Set(
          backendNodes.map((node) => `${node.position.lat},${node.position.lng}`)
        );
        const predictedPositions = predNodes.map(
          (node) => `${node.position.lat},${node.position.lng}`
        );

        const correctPredictions = predictedPositions.filter((position) =>
          actualPositions.has(position)
        ).length;

        const totalPredictions = predictedPositions.length;

        const calculatedAccuracy =
          totalPredictions > 0
            ? (correctPredictions / totalPredictions) * 100
            : null;

        setAccuracy(calculatedAccuracy);

        const jitter = () => (Math.random() - 0.5) * 0.0001; // Small jitter function

        const allNodes: NodeDataItem[] = [
          ...backendNodes.map((node) => ({
            ...node,
            position: {
              lat: node.position.lat + jitter(),
              lng: node.position.lng + jitter(),
            },
            source: 'nodes' as const,
          })),
          ...predNodes.map((node) => ({
            ...node,
            position: {
              lat: node.position.lat + jitter(),
              lng: node.position.lng + jitter(),
            },
            source: 'predictions' as const,
          })),
        ];

        // Map combined data to the required format
        const newData: NodeData = allNodes.map((node) => ({
          ...node,
          zIndex: parseInt(node.id, 10),
          type: node.source === 'predictions' ? 'prediction' : 'pin',
        }));

        setData(newData);
      } catch (error) {
        console.error('Error fetching data:', error);
        setAccuracy(null);
      }
    };

    fetchData();
  }, [
    props.zeroRides,
    props.proportion,
    props.dateStart,
    props.dateEnd,
    props.timeStart,
    props.timeEnd,
  ]);

  return { data, accuracy };
};

export default useNodeData;
