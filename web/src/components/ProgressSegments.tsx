interface ProgressStage {
  id: string;
  name: string;
  color: string;
  description: string;
}

interface ProgressSegmentsProps {
  stages: ProgressStage[];
  currentStage: string;
}

export default function ProgressSegments({ stages, currentStage }: ProgressSegmentsProps) {
  return (
    <div className="flex space-x-1">
      {stages.map((stage, index) => {
        const currentStageIndex = stages.findIndex(s => s.id === currentStage);
        const isCompleted = index < currentStageIndex;
        const isCurrent = index === currentStageIndex;
        
        let segmentColor = 'bg-gray-300 dark:bg-gray-600'; // inactive
        if (isCompleted) {
          segmentColor = stage.color === 'red' ? 'bg-red-500' : 
                       stage.color === 'orange' ? 'bg-orange-500' : 
                       stage.color === 'yellow' ? 'bg-yellow-500' : 'bg-green-500';
        } else if (isCurrent) {
          segmentColor = stage.color === 'red' ? 'bg-red-500' : 
                       stage.color === 'orange' ? 'bg-orange-500' : 
                       stage.color === 'yellow' ? 'bg-yellow-500' : 'bg-green-500';
        }
        
        return (
          <div
            key={stage.id}
            className={`flex-1 h-1.5 rounded-sm transition-all duration-300 ${segmentColor} ${isCurrent ? 'animate-pulse' : ''}`}
            title={stage.name}
          />
        );
      })}
    </div>
  );
}