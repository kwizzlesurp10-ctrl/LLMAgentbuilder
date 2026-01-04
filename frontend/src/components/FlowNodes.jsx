import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Bot, Wrench, Database, BookOpen } from 'lucide-react';

const NodeWrapper = ({ children, title, icon: Icon, color }) => (
    <div className={`px-4 py-2 shadow-md rounded-md bg-white border-2 border-[${color}] min-w-[200px]`}>
        <div className="flex items-center">
            <div className={`rounded-full w-8 h-8 flex justify-center items-center bg-[${color}]/10`}>
                <Icon size={20} className={`text-[${color}]`} />
            </div>
            <div className="ml-2">
                <div className="text-lg font-bold text-gray-700">{title}</div>
            </div>
        </div>
        <div className="mt-2 text-gray-500 text-sm">
            {children}
        </div>
    </div>
);

export const AgentNode = memo(({ data, isConnectable }) => {
    return (
        <>
            <Handle
                type="target"
                position={Position.Top}
                isConnectable={isConnectable}
                className="w-3 h-3 bg-blue-500"
            />
            <NodeWrapper title={`Agent: ${data.label}`} icon={Bot} color="#3b82f6">
                <div className="space-y-2">
                    <div>
                        <label className="text-xs font-semibold text-gray-500 uppercase">System Prompt</label>
                        <textarea
                            className="w-full text-xs p-1 border rounded resize-none focus:outline-none focus:border-blue-500 bg-gray-50 text-gray-800"
                            rows={3}
                            value={data.prompt}
                            onChange={(evt) => data.onChange(evt.target.value, 'prompt')}
                            placeholder="You are a helpful assistant..."
                        />
                    </div>
                    <div>
                        <label className="text-xs font-semibold text-gray-500 uppercase">Model</label>
                        <select
                            className="w-full text-xs p-1 border rounded focus:outline-none focus:border-blue-500 bg-gray-50 text-gray-800"
                            value={data.model}
                            onChange={(evt) => data.onChange(evt.target.value, 'model')}
                        >
                            <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                            <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                            <option value="gpt-4o">GPT-4o</option>
                        </select>
                    </div>
                </div>
            </NodeWrapper>
            <Handle
                type="source"
                position={Position.Bottom}
                isConnectable={isConnectable}
                className="w-3 h-3 bg-blue-500"
            />
        </>
    );
});

export const ToolNode = memo(({ data, isConnectable }) => {
    return (
        <>
            <Handle
                type="source"
                position={Position.Top}
                isConnectable={isConnectable}
                className="w-3 h-3 bg-purple-500"
            />
            <NodeWrapper title="Tool" icon={Wrench} color="#a855f7">
                <div className="space-y-2">
                    <div>
                        <label className="text-xs font-semibold text-gray-500 uppercase">Name</label>
                        <input
                            className="w-full text-xs p-1 border rounded focus:outline-none focus:border-purple-500 text-gray-800"
                            value={data.name}
                            onChange={(evt) => data.onChange(evt.target.value, 'name')}
                            placeholder="search_web"
                        />
                    </div>
                    <div>
                        <label className="text-xs font-semibold text-gray-500 uppercase">Input Schema (JSON)</label>
                        <textarea
                            className="w-full text-xs p-1 border rounded resize-none font-mono focus:outline-none focus:border-purple-500 bg-gray-50 text-gray-800"
                            rows={4}
                            value={data.schema}
                            onChange={(evt) => data.onChange(evt.target.value, 'schema')}
                            placeholder='{"type": "object", ...}'
                        />
                    </div>
                </div>
            </NodeWrapper>
        </>
    );
});

export const DatabaseNode = memo(({ data, isConnectable }) => {
    return (
        <>
            <Handle
                type="source"
                position={Position.Top}
                isConnectable={isConnectable}
                className="w-3 h-3 bg-green-500"
            />
            <NodeWrapper title="Database" icon={Database} color="#22c55e">
                <div>
                    <label className="text-xs font-semibold text-gray-500 uppercase">SQLite Path</label>
                    <input
                        className="w-full text-xs p-1 border rounded focus:outline-none focus:border-green-500 text-gray-800"
                        value={data.path}
                        onChange={(evt) => data.onChange(evt.target.value, 'path')}
                        placeholder="/path/to/db.sqlite"
                    />
                </div>
            </NodeWrapper>
        </>
    );
});

export const TeamNode = memo(({ data, isConnectable }) => {
    return (
        <>
            <Handle
                type="target"
                position={Position.Top}
                isConnectable={isConnectable}
                className="w-3 h-3 bg-red-500"
            />
            <NodeWrapper title="Team (Swarm)" icon={Bot} color="#ef4444">
                <div className="space-y-2">
                    <div>
                        <label className="text-xs font-semibold text-gray-500 uppercase">Team Name</label>
                        <input
                            className="w-full text-xs p-1 border rounded focus:outline-none focus:border-red-500 text-gray-800"
                            value={data.name}
                            onChange={(evt) => data.onChange(evt.target.value, 'name')}
                            placeholder="My Swarm"
                        />
                    </div>
                    <div>
                        <label className="text-xs font-semibold text-gray-500 uppercase">Strategy</label>
                        <select
                            className="w-full text-xs p-1 border rounded focus:outline-none focus:border-red-500 bg-gray-50 text-gray-800"
                            value={data.strategy}
                            onChange={(evt) => data.onChange(evt.target.value, 'strategy')}
                        >
                            <option value="round_robin">Round Robin</option>
                            <option value="parallel">Parallel</option>
                        </select>
                    </div>
                </div>
            </NodeWrapper>
            <Handle
                type="source"
                position={Position.Bottom}
                isConnectable={isConnectable}
                className="w-3 h-3 bg-red-500"
            />
        </>
    );
});

export const KnowledgeBaseNode = memo(({ data, isConnectable }) => {
    return (
        <>
            <Handle
                type="source"
                position={Position.Top}
                isConnectable={isConnectable}
                className="w-3 h-3 bg-orange-500"
            />
            <NodeWrapper title="Knowledge Base" icon={BookOpen} color="#f97316">
                <div>
                    <label className="text-xs font-semibold text-gray-500 uppercase">Documents Path</label>
                    <input
                        className="w-full text-xs p-1 border rounded focus:outline-none focus:border-orange-500 text-gray-800"
                        value={data.path}
                        onChange={(evt) => data.onChange(evt.target.value, 'path')}
                        placeholder="/path/to/docs"
                    />
                </div>
            </NodeWrapper>
        </>
    );
});
