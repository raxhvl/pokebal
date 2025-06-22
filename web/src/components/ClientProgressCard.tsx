import ProgressSegments from './ProgressSegments';

interface ProgressStage {
  id: string;
  name: string;
  color: string;
  description: string;
}

interface Client {
  id: string;
  name: string;
  language: string;
  website: string;
  progress: string;
}

interface ClientProgressCardProps {
  client: Client;
  stages: ProgressStage[];
}

export default function ClientProgressCard({ client, stages }: ClientProgressCardProps) {
  const stageInfo = stages.find(stage => stage.id === client.progress);
  const currentStageIndex = stages.findIndex(stage => stage.id === client.progress);
  const stageColor = stageInfo?.color === 'red' ? 'bg-red-500' : 
                   stageInfo?.color === 'orange' ? 'bg-orange-500' : 
                   stageInfo?.color === 'yellow' ? 'bg-yellow-500' : 'bg-green-500';
  const stageTextColor = stageInfo?.color === 'red' ? 'text-red-500' : 
                       stageInfo?.color === 'orange' ? 'text-orange-500' : 
                       stageInfo?.color === 'yellow' ? 'text-yellow-500' : 'text-green-500';

  // Calculate percentage based on stage position
  const percentage = currentStageIndex >= 0 ? Math.round(((currentStageIndex + 1) / stages.length) * 100) : 0;

  return (
    <div className="bg-gray-100 dark:bg-gray-800 rounded p-2 space-y-2">
      {/* Client header with name and percentage */}
      <div className="flex justify-between items-center">
        <span className="text-xs font-bold text-gray-800 dark:text-gray-200">{client.name.toUpperCase()}</span>
        <span className="text-xs font-mono text-gray-700 dark:text-gray-300">{percentage}%</span>
      </div>
      
      {/* Segmented progress bar */}
      <ProgressSegments stages={stages} currentStage={client.progress} />
      
      {/* Stage indicator with better visual hierarchy */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 ${stageColor} rounded-sm ${client.progress === stages[0].id ? 'animate-pulse' : ''}`}></div>
          <span className={`text-xs font-bold ${stageTextColor} uppercase tracking-wide`}>{stageInfo?.name.replace('_', ' ')}</span>
        </div>
        <span className="text-xs text-gray-400 dark:text-gray-500">{client.language}</span>
      </div>
    </div>
  );
}