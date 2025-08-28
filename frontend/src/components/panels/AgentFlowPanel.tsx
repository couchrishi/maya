import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, Gamepad2, Image, Upload, Zap, CheckCircle, Clock, AlertCircle, ArrowDown, Plug, X } from "lucide-react";
import { useGame } from "@/contexts/GameContext";
import { useEffect, useState } from "react";
import { AgentState } from "@/contexts/GameContext";

interface AgentActivity {
  id: string;
  agent: string;
  action: string;
  timestamp: Date;
  type: 'info' | 'success' | 'warning' | 'error';
}

interface MCPServer {
  id: string;
  name: string;
  type: 'asset-generation' | 'firebase-hosting';
  status: 'active' | 'disabled' | 'standby';
  location?: string;
  lastUsed?: Date;
  metadata?: Record<string, any>;
}

interface AgentCardProps {
  agent: any;
  onClose: () => void;
  position: { x: number; y: number };
}


// Agent Card Component
function AgentCard({ agent, onClose }: AgentCardProps) {
  const { gameState } = useGame();
  const agentStatus = gameState.agents[agent.key]?.status || 'idle';
  const currentTask = gameState.agents[agent.key]?.currentTask || 'Standby';
  
  // Agent-specific data
  const getAgentData = () => {
    switch (agent.key) {
      case 'orchestrator':
        return {
          model: 'gemini-2.5-flash-lite',
          maxLlmCalls: 500,
          capabilities: [
            'Intelligent Request Routing',
            'Multi-Agent Coordination',
            'Decision Making Engine'
          ],
          tools: []
        };
      case 'assetGenerator':
        return {
          model: 'gemini-2.5-flash-lite',
          maxLlmCalls: 500,
          capabilities: [
            'AI Image Generation',
            'Visual Asset Creation',
            'Multi-Model Integration'
          ],
          tools: [
            { name: 'Imagen MCP', status: 'active' },
            { name: 'HF MCP', status: 'active' },
            { name: 'Vertex AI MCP', status: 'active' }
          ]
        };
      case 'gameCreator':
        return {
          model: 'gemini-2.5-flash-lite',
          maxLlmCalls: 500,
          capabilities: [
            'HTML5 Canvas Games',
            'Interactive Mechanics',
            'Real-time Code Streaming'
          ],
          tools: []
        };
      case 'publisher':
        return {
          model: 'gemini-2.5-flash-lite',
          maxLlmCalls: 500,
          capabilities: [
            'Firebase Deployment',
            'Static Site Hosting',
            'Asset Optimization'
          ],
          tools: [
            { name: 'Firebase MCP', status: 'active' },
            { name: 'Supabase MCP', status: 'disabled' }
          ]
        };
      default:
        return { model: '', maxLlmCalls: 0, capabilities: [], tools: [] };
    }
  };

  const agentData = getAgentData();
  
  return (
    <div 
      className="fixed inset-0 z-[99999] flex items-center justify-center bg-black/50"
      onClick={onClose}
    >
      <div 
        className="bg-black border-4 border-green-400 rounded-lg p-6 max-w-md w-full mx-4"
        onClick={(e) => e.stopPropagation()}
        style={{
          boxShadow: '0 0 30px rgba(34, 197, 94, 0.8)',
          animation: 'fadeIn 0.2s ease-out'
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <agent.icon className={`w-6 h-6 ${agent.color}`} />
            <h3 className="text-green-400 font-mono text-lg font-bold">
              {agent.displayName.toUpperCase()}
            </h3>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-1"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Status & Model Info */}
        <div className="space-y-3 mb-5">
          <div className="flex justify-between">
            <span className="text-gray-300 font-mono">Status:</span>
            <span className={`font-mono font-bold ${
              agentStatus === 'active' ? 'text-green-400' : 
              agentStatus === 'completed' ? 'text-blue-400' :
              agentStatus === 'error' ? 'text-red-400' : 'text-gray-400'
            }`}>
              {agentStatus.toUpperCase()}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-300 font-mono">Model:</span>
            <span className="text-green-200 font-mono">{agentData.model}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-300 font-mono">Max LLM Calls:</span>
            <span className="text-green-200 font-mono">{agentData.maxLlmCalls}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-300 font-mono">Current Task:</span>
            <span className="text-green-200 font-mono text-sm">{currentTask}</span>
          </div>
        </div>

        {/* Capabilities */}
        <div className="mb-5">
          <h4 className="text-green-400 font-mono font-bold mb-2">Capabilities:</h4>
          <div className="space-y-1">
            {agentData.capabilities.map((capability, index) => (
              <div key={index} className="flex items-center space-x-2">
                <span className="text-green-400">•</span>
                <span className="text-green-200 font-mono text-sm">{capability}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Tools & Integrations */}
        {agentData.tools.length > 0 && (
          <div>
            <h4 className="text-green-400 font-mono font-bold mb-2">Tools & Integrations:</h4>
            <div className="space-y-2">
              {agentData.tools.map((tool, index) => (
                <div key={index} className="flex items-center justify-between p-2 bg-gray-900/50 rounded">
                  <span className="text-green-200 font-mono text-sm">• {tool.name}</span>
                  <div className={`px-2 py-1 rounded font-mono text-xs font-bold ${
                    tool.status === 'active' 
                      ? 'bg-green-400/30 text-green-400 border border-green-400/50' 
                      : 'bg-gray-500/30 text-gray-400 border border-gray-500/50'
                  }`}>
                    {tool.status.toUpperCase()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export function AgentFlowPanel() {
  const { gameState, updateAgentState } = useGame();
  const [activities, setActivities] = useState<AgentActivity[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [showAgentCard, setShowAgentCard] = useState<{ agent: any; position: { x: number; y: number } } | null>(null);
  const [agentLogs, setAgentLogs] = useState<Record<string, AgentActivity[]>>({
    orchestrator: [],
    assetGenerator: [],
    gameCreator: [],
    publisher: [],
    'asset-mcp': [],
    'firebase-mcp': []
  });
  // Asset Generator MCP Servers
  const assetGeneratorMcpServers: MCPServer[] = [
    {
      id: 'imagen-mcp',
      name: 'Imagen MCP',
      type: 'asset-generation',
      status: 'active',
      location: 'Google Cloud',
      metadata: { model: 'imagen-3.0' }
    },
    {
      id: 'hf-mcp',
      name: 'HF MCP',
      type: 'asset-generation',
      status: 'active',
      location: 'Hugging Face',
      metadata: { model: 'flux-schnell' }
    },
    {
      id: 'vertex-ai-mcp',
      name: 'Vertex AI MCP',
      type: 'asset-generation',
      status: 'active',
      location: 'Vertex AI Endpoint',
      metadata: { model: 'flux-schnell-game-assets' }
    }
  ];

  // Publisher MCP Servers
  const publisherMcpServers: MCPServer[] = [
    {
      id: 'firebase-mcp',
      name: 'Firebase MCP',
      type: 'firebase-hosting',
      status: 'active',
      location: 'saib-ai-playground',
      metadata: { project: 'saib-ai-playground' }
    },
    {
      id: 'supabase-mcp',
      name: 'Supabase MCP',
      type: 'firebase-hosting',
      status: 'disabled',
      location: 'Supabase Cloud',
      metadata: { project: 'maya-games' }
    }
  ];

  // Modern agent configuration with cleaner design
  const agentDisplayConfig = [
    {
      key: 'orchestrator' as keyof AgentState,
      displayName: 'MAYA Orchestrator',
      shortName: 'MAYA',
      icon: Brain,
      color: 'text-blue-400',
      bgColor: 'bg-blue-400/10',
      borderColor: 'border-blue-400/20',
      description: 'Orchestrator routing and coordination'
    },
    {
      key: 'assetGenerator' as keyof AgentState,
      displayName: 'Asset Generator',
      shortName: 'ASSET',
      icon: Image,
      color: 'text-purple-400',
      bgColor: 'bg-purple-400/10',
      borderColor: 'border-purple-400/20',
      description: 'Visual asset creation',
      mcpServers: assetGeneratorMcpServers
    },
    {
      key: 'gameCreator' as keyof AgentState,
      displayName: 'Game Creator',
      shortName: 'GAME',
      icon: Gamepad2,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-400/10',
      borderColor: 'border-emerald-400/20',
      description: 'HTML5 game development'
    },
    {
      key: 'publisher' as keyof AgentState,
      displayName: 'Publisher',
      shortName: 'PUB',
      icon: Upload,
      color: 'text-orange-400',
      bgColor: 'bg-orange-400/10',
      borderColor: 'border-orange-400/20',
      description: 'Firebase deployment',
      mcpServers: publisherMcpServers
    }
  ];

  // Add activity to the log
  const addActivity = (agent: string, action: string, type: AgentActivity['type'] = 'info') => {
    const newActivity: AgentActivity = {
      id: Date.now().toString(),
      agent,
      action,
      timestamp: new Date(),
      type
    };
    setActivities(prev => [newActivity, ...prev.slice(0, 19)]); // Keep last 20 activities
    
    // Also add to specific agent logs
    const agentKey = agent.toLowerCase().replace('-', '');
    setAgentLogs(prev => ({
      ...prev,
      [agentKey]: [newActivity, ...prev[agentKey]?.slice(0, 9) || []] // Keep last 10 for each agent
    }));
  };

  // Handle Agent Card display
  const handleAgentCardClick = (event: React.MouseEvent, agent: any) => {
    console.log('🔧 Agent card click handler triggered', { agent, event });
    event.stopPropagation();
    event.preventDefault();
    
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
    console.log('📍 Click position:', { rect, x: rect.left, y: rect.bottom + 5 });
    
    setShowAgentCard({
      agent,
      position: { x: rect.left, y: rect.bottom + 5 }
    });
  };

  // Close Agent Card when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      console.log('👋 Closing Agent Card');
      setShowAgentCard(null);
    };
    if (showAgentCard) {
      console.log('📌 Agent Card shown, adding click listener');
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showAgentCard]);

  // Debug the Agent Card state
  useEffect(() => {
    console.log('🔍 Agent Card state changed:', showAgentCard);
  }, [showAgentCard]);

  // Get currently active agent
  const getActiveAgent = () => {
    return agentDisplayConfig.find(config => 
      gameState.agents[config.key].status === 'active'
    ) || agentDisplayConfig[0]; // Default to orchestrator
  };


  // Helper function to map agent names and update state
  const updateAgentStatus = (
    agentKey: keyof AgentState, 
    status: 'idle' | 'active' | 'completed' | 'error', 
    currentTask: string,
    lastActivity?: string
  ) => {
    updateAgentState(agentKey, { status, currentTask, lastActivity });
  };

  // Monitor game state changes and update agent activities and MCP servers
  useEffect(() => {
    const { statusBox, isGenerating, operationType, publisher } = gameState;

    // Handle different operation types
    if (operationType === 'publishing') {
      updateAgentStatus('orchestrator', 'active', 'Routing to Publisher');
      updateAgentStatus('gameCreator', 'completed', 'Game Ready');
      updateAgentStatus('assetGenerator', 'completed', 'Assets Ready');

      switch (publisher.status) {
        case 'validating':
          updateAgentStatus('publisher', 'active', 'Validating game data', 'Checking if game has been created...');
          addActivity('PUB', 'Checking if game has been created...', 'info');
          break;
        case 'preparing':
          updateAgentStatus('publisher', 'active', 'Preparing deployment', 'Game found! Preparing for deployment...');
          addActivity('PUB', 'Game found! Preparing for deployment...', 'success');
          break;
        case 'deploying':
          updateAgentStatus('publisher', 'active', 'Uploading to Firebase', 'Uploading files to Firebase hosting...');
          addActivity('PUB', 'Uploading files to Firebase hosting...', 'info');
          break;
        case 'published':
          updateAgentStatus('publisher', 'completed', 'Game Live!', 'Game deployed successfully!');
          addActivity('PUB', 'Game deployed successfully!', 'success');
          break;
        case 'error':
          updateAgentStatus('publisher', 'error', 'Deployment failed', `Deployment error: ${publisher.error}`);
          addActivity('PUB', `Deployment error: ${publisher.error}`, 'error');
          break;
      }
    } else if (operationType === 'game_creation') {
      updateAgentStatus('orchestrator', 'active', 'Coordinating agents');
      updateAgentStatus('publisher', 'idle', 'Standby');

      if (isGenerating) {
        switch (statusBox.phase) {
          case 'analyzing':
            updateAgentStatus('orchestrator', 'active', 'Analyzing request', 'Analyzing user request and determining approach');
            updateAgentStatus('gameCreator', 'idle', 'Standby');
            addActivity('MAYA', 'Analyzing user request and determining approach', 'info');
            break;
          case 'thinking':
            updateAgentStatus('orchestrator', 'active', 'Planning approach');
            updateAgentStatus('gameCreator', 'active', 'Initializing', 'Planning game concept and structure');
            addActivity('GAME', 'Planning game concept and structure', 'info');
            // Check if assets are being generated
            if (gameState.statusBox.bullets.some(bullet => bullet.includes('asset'))) {
              updateAgentStatus('assetGenerator', 'active', 'Generating assets');
              addActivity('ASSET', 'Asset generation initialized', 'info');
            }
            break;
          case 'outlining':
            updateAgentStatus('gameCreator', 'active', 'Designing concept', 'Creating game outline and features');
            addActivity('GAME', 'Creating game outline and features', 'info');
            break;
          case 'generating':
            updateAgentStatus('gameCreator', 'active', 'Writing game code', 'Streaming game code in real-time');
            if (gameState.codeStream.isStreaming) {
              addActivity('GAME', 'Streaming game code in real-time', 'info');
            }
            break;
          case 'completed':
            updateAgentStatus('orchestrator', 'completed', 'Mission Complete', 'Game code generation completed successfully');
            updateAgentStatus('gameCreator', 'completed', 'Game Generated', 'Game code generation completed successfully');
            addActivity('GAME', 'Game code generation completed successfully', 'success');
            break;
        }
      }
    } else {
      // Reset all agents to idle when no operation is active
      agentDisplayConfig.forEach(config => {
        if (gameState.agents[config.key].status !== 'idle') {
          updateAgentStatus(config.key, 'idle', 'Standby');
        }
      });
    }
  }, [gameState.statusBox.phase, gameState.isGenerating, gameState.operationType, gameState.publisher.status]);

  const getStatusIcon = (status: 'idle' | 'active' | 'completed' | 'error') => {
    switch (status) {
      case 'active':
        return <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getActivityIcon = (type: AgentActivity['type']) => {
    switch (type) {
      case 'success':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      default:
        return '🔄';
    }
  };

  const renderAgentWithMcp = (
    agent: any, 
    agentKey: string, 
    onClick: () => void,
    isSelected: boolean
  ) => {
    const agentStatus = gameState.agents[agentKey]?.status || 'idle';
    const isActive = agentStatus === 'active';
    const hasMcpServers = agent.mcpServers && agent.mcpServers.length > 0;
    
    return (
      <div className="flex flex-col items-center space-y-2">
        {/* Agent Card */}
        <div 
          className={`
            relative flex flex-col items-center p-6 rounded-xl border-2 transition-all duration-300 w-32 cursor-pointer
            ${isActive ? `${agent.borderColor.replace('/20', '')} shadow-lg shadow-current/50` : agent.borderColor}
            ${isActive ? 'bg-current/10' : 'bg-background/50'}
            ${isSelected ? 'ring-2 ring-white/50' : 'hover:scale-105'}
          `}
          onClick={onClick}
        >
          {/* Status Indicator */}
          <div className={`absolute -top-2 -right-2 w-4 h-4 rounded-full ${
            isActive ? 'bg-green-400 animate-pulse' : 'bg-gray-500'
          }`} />
          
          {/* Info Icon - shows agent details */}
          <div 
            className={`absolute -bottom-2 -right-2 w-5 h-5 rounded-full bg-blue-400 flex items-center justify-center cursor-pointer hover:bg-blue-300 z-10`}
            onClick={(e) => {
              console.log('🔥 INFO CLICKED!', { agent: agentKey });
              handleAgentCardClick(e, agent);
            }}
            onMouseDown={(e) => {
              console.log('🖱️ INFO MOUSE DOWN!');
              e.stopPropagation();
            }}
            title="View Agent Details"
          >
            <span className="text-black text-xs font-bold">i</span>
          </div>
          
          <agent.icon className={`w-12 h-12 mb-3 ${agent.color}`} />
          <div className={`text-base font-mono font-bold ${agent.color} mb-1`}>{agent.shortName}</div>
          <div className="text-xs text-muted-foreground text-center">{agent.description}</div>
        </div>
        
        {/* Status Label */}
        <div className={`text-xs px-2 py-1 rounded ${
          isActive ? 'bg-green-400/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
        }`}>
          {agentStatus.toUpperCase()}
        </div>
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col space-y-4 p-4">
      {/* Three-Level Agent Hierarchy */}
      <Card className="bg-background/50 border-primary/30 backdrop-blur cyber-grid flex-1">
        <CardHeader className="pb-4">
          <CardTitle className="text-primary font-orbitron flex items-center text-lg">
            <Zap className="w-6 h-6 mr-2" />
            Agent Flow
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1">
          <div className="flex flex-col items-center justify-center space-y-12 h-full py-8">
            
            {/* Orchestrator */}
            <div className="flex flex-col items-center">
              {renderAgentWithMcp(
                agentDisplayConfig[0], 
                'orchestrator', 
                () => setSelectedAgent(selectedAgent === 'orchestrator' ? null : 'orchestrator'),
                selectedAgent === 'orchestrator'
              )}
            </div>

            {/* Vertical Arrow */}
            <div className="flex items-center">
              <ArrowDown className="w-6 h-6 text-muted-foreground" />
            </div>

            {/* Agents with their MCP servers */}
            <div className="flex items-center justify-center space-x-16">
              {/* Asset Generator with Asset MCP */}
              {renderAgentWithMcp(
                agentDisplayConfig[1], // Asset Generator
                'assetGenerator', 
                () => setSelectedAgent(selectedAgent === 'assetGenerator' ? null : 'assetGenerator'),
                selectedAgent === 'assetGenerator'
              )}
              
              {/* Game Creator (no MCP) */}
              {renderAgentWithMcp(
                agentDisplayConfig[2], // Game Creator
                'gameCreator', 
                () => setSelectedAgent(selectedAgent === 'gameCreator' ? null : 'gameCreator'),
                selectedAgent === 'gameCreator'
              )}
              
              {/* Publisher with Firebase MCP */}
              {renderAgentWithMcp(
                agentDisplayConfig[3], // Publisher
                'publisher', 
                () => setSelectedAgent(selectedAgent === 'publisher' ? null : 'publisher'),
                selectedAgent === 'publisher'
              )}
            </div>

          </div>
        </CardContent>
      </Card>

      {/* Agent Terminal - Shows when an agent is selected */}
      {selectedAgent && (
        <Card className="bg-black/90 border-green-400/50 backdrop-blur">
          <CardHeader className="pb-3">
            <CardTitle className="text-green-400 font-mono text-sm flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse mr-3" />
                {selectedAgent.toUpperCase()} TERMINAL
              </div>
              <button 
                onClick={() => setSelectedAgent(null)}
                className="text-gray-500 hover:text-white text-xs"
              >
                [CLOSE]
              </button>
            </CardTitle>
          </CardHeader>
          <CardContent className="h-40 overflow-y-auto bg-black/50 rounded font-mono text-sm">
            {agentLogs[selectedAgent]?.length === 0 ? (
              <div className="text-green-400/70 text-center py-8">
                No activity logs for {selectedAgent.toUpperCase()}
              </div>
            ) : (
              <div className="space-y-1">
                {agentLogs[selectedAgent]?.map((log) => (
                  <div key={log.id} className="flex items-start space-x-2">
                    <span className="text-green-400/70 text-xs min-w-[60px]">
                      {log.timestamp.toLocaleTimeString('en-US', { 
                        hour12: false, 
                        hour: '2-digit', 
                        minute: '2-digit', 
                        second: '2-digit' 
                      })}
                    </span>
                    <span className="text-xs">{getActivityIcon(log.type)}</span>
                    <span className="text-green-400 text-xs">$</span>
                    <span className="text-green-200 text-xs flex-1">{log.action}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}


      {/* Agent Card */}
      {showAgentCard && (
        <AgentCard 
          agent={showAgentCard.agent}
          position={showAgentCard.position}
          onClose={() => setShowAgentCard(null)}
        />
      )}
    </div>
  );
}