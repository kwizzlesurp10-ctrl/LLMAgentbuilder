import React, { useCallback, useState } from 'react';
import {
    ReactFlow,
    useNodesState,
    useEdgesState,
    addEdge,
    Background,
    Controls,
    MiniMap,
    Panel,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { AgentNode, ToolNode, DatabaseNode, TeamNode, KnowledgeBaseNode } from '../components/FlowNodes';

const nodeTypes = {
    agent: AgentNode,
    tool: ToolNode,
    database: DatabaseNode,
    team: TeamNode,
    knowledge: KnowledgeBaseNode
};

const initialNodes = [
    {
        id: 'agent-1',
        type: 'agent',
        position: { x: 250, y: 50 },
        data: {
            label: 'MyAgent',
            prompt: 'You are a helpful assistant.',
            model: 'claude-3-5-sonnet-20241022',
            onChange: () => { }
        },
    },
];

const FlowBuilder = () => {
    // ... (Hooks same as before)
    // We need to wrap the onChange handlers to update state
    const handleNodeChange = (id, value, field) => {
        setNodes((nds) =>
            nds.map((node) => {
                if (node.id === id) {
                    return {
                        ...node,
                        data: {
                            ...node.data,
                            [field]: value,
                        },
                    };
                }
                return node;
            })
        );
    };

    // Hydrate initial nodes with the handler
    const [nodes, setNodes, onNodesChange] = useNodesState(
        initialNodes.map(n => ({
            ...n,
            data: { ...n.data, onChange: (val, field) => handleNodeChange(n.id, val, field) }
        }))
    );
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generationResult, setGenerationResult] = useState(null);
    const [marketplaceTools, setMarketplaceTools] = useState([]);

    React.useEffect(() => {
        fetch('/api/tools')
            .then(res => res.json())
            .then(data => {
                if (data.tools) setMarketplaceTools(data.tools);
            })
            .catch(err => console.error("Failed to fetch tools", err));
    }, []);

    const onDragStart = (event, tool) => {
        event.dataTransfer.setData('application/reactflow/tool', JSON.stringify(tool));
        event.dataTransfer.effectAllowed = 'move';
    };

    const onConnect = useCallback(
        (params) => setEdges((eds) => addEdge(params, eds)),
        [setEdges],
    );

    const addNode = (type) => {
        const id = `${type}-${nodes.length + 1}`;
        const newNode = {
            id,
            type,
            position: { x: Math.random() * 400, y: Math.random() * 400 },
            data: {
                label: type === 'agent' ? 'NewAgent' : type,
                prompt: '',
                model: 'claude-3-5-sonnet-20241022',
                name: '',
                schema: '',
                path: '',
                strategy: 'round_robin', // for team
                onChange: (val, field) => handleNodeChange(id, val, field)
            },
        };
        setNodes((nds) => nds.concat(newNode));
    };

    const handleGenerate = async () => {
        setIsGenerating(true);
        setGenerationResult(null);
        try {
            // Check for Team Node
            const teamNode = nodes.find(n => n.type === 'team');

            if (teamNode) {
                // --- Swarm Generation Logic ---
                const connectedAgentEdges = edges.filter(e => e.target === teamNode.id);
                const connectedAgentIds = connectedAgentEdges.map(e => e.source);

                const agents = [];

                nodes.forEach(node => {
                    if (connectedAgentIds.includes(node.id) && node.type === 'agent') {
                        agents.push({
                            name: node.data.label || node.id,
                            prompt: node.data.prompt,
                            model: node.data.model
                        });
                    }
                });

                if (agents.length === 0) {
                    alert("Team node must have at least one Agent connected to it.");
                    setIsGenerating(false);
                    return;
                }

                const payload = {
                    name: teamNode.data.name || "MySwarm",
                    prompt: "Orchestrator", // Generic prompt for swarm container
                    task: "Manage agents",
                    model: "claude-3-5-sonnet-20241022",
                    provider: "swarm",
                    swarm_config: {
                        strategy: teamNode.data.strategy || "round_robin"
                    },
                    agents: agents
                };

                // Call API
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.detail || "Generation failed");
                }
                setGenerationResult(data);
                alert(`Swarm ${data.filename} generated successfully!`);


            } else {
                // --- Single Agent Generation Logic ---
                // 1. Find the Agent Node (Limit to 1 for now)
                const agentNode = nodes.find(n => n.type === 'agent');
                if (!agentNode) {
                    alert("Please add an Agent node.");
                    setIsGenerating(false);
                    return;
                }

                // 2. Find connected nodes
                const connectedToolEdges = edges.filter(e => e.target === agentNode.id);
                const connectedToolIds = connectedToolEdges.map(e => e.source);

                const tools = [];
                let dbPath = null;
                let docsPath = null;

                nodes.forEach(node => {
                    if (connectedToolIds.includes(node.id)) {
                        if (node.type === 'tool') {
                            try {
                                const schema = node.data.schema ? JSON.parse(node.data.schema) : {};
                                tools.push({
                                    name: node.data.name,
                                    description: "Custom tool",
                                    input_schema: schema
                                });
                            } catch (e) {
                                console.error(`Invalid JSON for tool ${node.id}`, e);
                                alert(`Invalid JSON schema for tool ${node.data.name || node.id}`);
                            }
                        } else if (node.type === 'database') {
                            dbPath = node.data.path;
                        } else if (node.type === 'knowledge') {
                            docsPath = node.data.path;
                        }
                    }
                });

                // 3. Construct Payload
                const payload = {
                    name: agentNode.data.label || "GeneratedAgent",
                    prompt: agentNode.data.prompt,
                    task: "Auto-generated task from Visual Builder",
                    model: agentNode.data.model,
                    provider: "anthropic",
                    tools: tools,
                    db_path: dbPath,
                    docs_path: docsPath
                };

                // 4. Call API
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.detail || "Generation failed");
                }

                setGenerationResult(data);
                alert(`Agent ${data.filename} generated successfully!`);
            }

        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}`);
        } finally {
            setIsGenerating(false);
        }
    };

    const onDragOver = useCallback((event) => {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
    }, []);

    const onDrop = useCallback(
        (event) => {
            event.preventDefault();

            const toolData = event.dataTransfer.getData('application/reactflow/tool');
            if (!toolData) return;

            const tool = JSON.parse(toolData);

            // Get coordinates (simplified, ideally utilize reactFlowInstance.project)
            // For now, simple random or offset from drop? 
            // Better: use screenToFlowPosition if verify ReactFlow provider.
            // Simplified fallback:
            const position = { x: event.clientX - 200, y: event.clientY - 100 };

            const newNode = {
                id: `tool-${nodes.length + 1}`,
                type: 'tool',
                position,
                data: {
                    label: tool.name,
                    name: tool.name,
                    schema: JSON.stringify(tool.input_schema, null, 2),
                    onChange: (val, field) => handleNodeChange(`tool-${nodes.length + 1}`, val, field)
                },
            };

            setNodes((nds) => nds.concat(newNode));
        },
        [nodes, setNodes]
    );

    return (
        <div className="h-screen w-full flex flex-col">
            <div className="bg-white border-b px-6 py-3 flex justify-between items-center z-10">
                <h1 className="text-xl font-bold text-gray-800">Visual Agent Builder</h1>
                <div className="space-x-2">
                    <button onClick={() => addNode('agent')} className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm font-medium">
                        + Agent
                    </button>
                    <button onClick={() => addNode('tool')} className="px-3 py-1 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 text-sm font-medium">
                        + Tool
                    </button>
                    <button onClick={() => addNode('database')} className="px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 text-sm font-medium">
                        + Database
                    </button>
                    <button onClick={() => addNode('knowledge')} className="px-3 py-1 bg-orange-100 text-orange-700 rounded hover:bg-orange-200 text-sm font-medium">
                        + Knowledge
                    </button>
                    <button onClick={() => addNode('team')} className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 text-sm font-medium">
                        + Team
                    </button>
                    <div className="h-6 w-px bg-gray-300 inline-block align-middle mx-2"></div>
                    <button
                        onClick={handleGenerate}
                        disabled={isGenerating}
                        className={`px-4 py-2 rounded text-white font-medium ${isGenerating ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'}`}
                    >
                        {isGenerating ? 'Generating...' : 'Generate Agent'}
                    </button>
                </div>
            </div>

            {generationResult && (
                <div className="bg-green-100 border-b border-green-200 px-6 py-2 flex justify-between items-center text-green-800 text-sm">
                    <span>
                        ✓ Agent <strong>{generationResult.filename}</strong> generated successfully!
                    </span>
                    <button
                        onClick={() => setGenerationResult(null)}
                        className="text-green-600 hover:text-green-800 font-bold"
                    >
                        ✕
                    </button>
                </div>
            )}

            <div className="flex flex-1 overflow-hidden">
                {/* Sidebar */}
                <div className="w-64 bg-white border-r p-4 overflow-y-auto">
                    <h2 className="text-sm font-bold text-gray-500 uppercase mb-4">Tool Marketplace</h2>
                    <div className="space-y-3">
                        {marketplaceTools.map((tool) => (
                            <div
                                key={tool.name}
                                className="p-3 bg-purple-50 border border-purple-200 rounded cursor-move hover:shadow-md transition-shadow"
                                draggable
                                onDragStart={(event) => onDragStart(event, tool)}
                            >
                                <div className="font-semibold text-purple-800 flex items-center gap-2">
                                    <span className="text-xs">🔧</span> {tool.name}
                                </div>
                                <div className="text-xs text-gray-600 mt-1">{tool.description}</div>
                            </div>
                        ))}
                    </div>
                    <div className="mt-8">
                        <h2 className="text-sm font-bold text-gray-500 uppercase mb-4">Manual Add</h2>
                        <div className="space-y-2">
                            <button onClick={() => addNode('agent')} className="w-full text-left px-3 py-2 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 text-sm font-medium border border-blue-200">
                                + Agent Node
                            </button>
                            <button onClick={() => addNode('tool')} className="w-full text-left px-3 py-2 bg-purple-50 text-purple-700 rounded hover:bg-purple-100 text-sm font-medium border border-purple-200">
                                + Custom Tool
                            </button>
                            <button onClick={() => addNode('database')} className="w-full text-left px-3 py-2 bg-green-50 text-green-700 rounded hover:bg-green-100 text-sm font-medium border border-green-200">
                                + Database
                            </button>
                            <button onClick={() => addNode('knowledge')} className="w-full text-left px-3 py-2 bg-orange-50 text-orange-700 rounded hover:bg-orange-100 text-sm font-medium border border-orange-200">
                                + Knowledge Base
                            </button>
                            <button onClick={() => addNode('team')} className="w-full text-left px-3 py-2 bg-red-50 text-red-700 rounded hover:bg-red-100 text-sm font-medium border border-red-200">
                                + Team (Swarm)
                            </button>
                        </div>
                    </div>
                </div>

                {/* Canvas */}
                <div className="flex-1 bg-gray-50 h-full" onDrop={onDrop} onDragOver={onDragOver}>
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onConnect={onConnect}
                        nodeTypes={nodeTypes}
                        fitView
                    >
                        <Background />
                        <Controls />
                        <MiniMap />
                        <Panel position="top-right" className="bg-white p-2 rounded shadow text-xs text-gray-500">
                            Drag tools from the sidebar to add them. Connect them to the Agent.
                        </Panel>
                    </ReactFlow>
                </div>
            </div>
        </div>
    );
};

export default FlowBuilder;
