"use client";

import { useState } from "react";

interface TreeNode {
  id: string;
  name: string;
  type: string;
  description?: string;
  children?: TreeNode[];
  required?: boolean;
  constraints?: string;
}

const schemaData: TreeNode = {
  id: "root",
  name: "BlockAccessList",
  type: "Container",
  description: "Root container with all account changes",
  children: [
    {
      id: "account_changes",
      name: "account_changes",
      type: "List[AccountChanges]",
      description: "List of all accounts with changes (max 300,000)",
      required: true,
      constraints: "defaults to []",
      children: [
        {
          id: "account_changes_item",
          name: "AccountChanges",
          type: "Container",
          description: "Changes for a single account within the block",
          children: [
            {
              id: "address",
              name: "address",
              type: "Address",
              description: "20-byte Ethereum address",
              required: true,
            },
            {
              id: "storage_changes",
              name: "storage_changes",
              type: "List[SlotChanges]",
              description: "Storage slot changes for this account (max 300,000)",
              required: true,
              constraints: "defaults to []",
              children: [
                {
                  id: "slot_changes",
                  name: "SlotChanges",
                  type: "Container",
                  description: "Changes to a single storage slot across transactions",
                  children: [
                    {
                      id: "slot",
                      name: "slot",
                      type: "StorageKey",
                      description: "32-byte storage slot identifier",
                      required: true,
                    },
                    {
                      id: "changes",
                      name: "changes",
                      type: "List[StorageChange]",
                      description: "List of changes to this slot (max 30,000)",
                      required: true,
                      children: [
                        {
                          id: "storage_change",
                          name: "StorageChange",
                          type: "Container",
                          description: "Storage change for a specific transaction",
                          children: [
                            {
                              id: "tx_index",
                              name: "tx_index",
                              type: "TxIndex",
                              description: "Transaction index (0-29999)",
                              required: true,
                            },
                            {
                              id: "new_value",
                              name: "new_value",
                              type: "StorageValue",
                              description: "32-byte storage value after transaction",
                              required: true,
                            },
                          ],
                        },
                      ],
                    },
                  ],
                },
              ],
            },
            {
              id: "storage_reads",
              name: "storage_reads",
              type: "List[StorageKey]",
              description: "Storage slots that were read but not modified (max 300,000)",
              required: true,
              constraints: "defaults to []",
            },
            {
              id: "balance_changes",
              name: "balance_changes",
              type: "List[BalanceChange]",
              description: "Balance changes for this account (max 30,000)",
              required: true,
              constraints: "defaults to []",
              children: [
                {
                  id: "balance_change",
                  name: "BalanceChange",
                  type: "Container",
                  description: "Balance change for a specific transaction",
                  children: [
                    {
                      id: "balance_tx_index",
                      name: "tx_index",
                      type: "TxIndex",
                      description: "Transaction index that caused balance change",
                      required: true,
                    },
                    {
                      id: "post_balance",
                      name: "post_balance",
                      type: "Balance",
                      description: "16-byte balance after transaction",
                      required: true,
                    },
                  ],
                },
              ],
            },
            {
              id: "nonce_changes",
              name: "nonce_changes",
              type: "List[NonceChange]",
              description: "Nonce changes for this account (max 30,000)",
              required: true,
              constraints: "defaults to []",
              children: [
                {
                  id: "nonce_change",
                  name: "NonceChange",
                  type: "Container",
                  description: "Nonce change for a specific transaction",
                  children: [
                    {
                      id: "nonce_tx_index",
                      name: "tx_index",
                      type: "TxIndex",
                      description: "Transaction index that changed nonce",
                      required: true,
                    },
                    {
                      id: "new_nonce",
                      name: "new_nonce",
                      type: "Nonce",
                      description: "New nonce value (uint64)",
                      required: true,
                    },
                  ],
                },
              ],
            },
            {
              id: "code_changes",
              name: "code_changes",
              type: "List[CodeChange]",
              description: "Code changes for this account (max 1)",
              required: true,
              constraints: "defaults to []",
              children: [
                {
                  id: "code_change",
                  name: "CodeChange",
                  type: "Container",
                  description: "Code change for a specific transaction",
                  children: [
                    {
                      id: "code_tx_index",
                      name: "tx_index",
                      type: "TxIndex",
                      description: "Transaction index that deployed code",
                      required: true,
                    },
                    {
                      id: "new_code",
                      name: "new_code",
                      type: "CodeData",
                      description: "Contract bytecode (max 24576 bytes)",
                      required: true,
                    },
                  ],
                },
              ],
            },
          ],
        },
      ],
    },
  ],
};

interface TreeNodeProps {
  node: TreeNode;
  level: number;
  expanded: Record<string, boolean>;
  onToggle: (id: string) => void;
}

function TreeNodeComponent({ node, level, expanded, onToggle }: TreeNodeProps) {
  const hasChildren = node.children && node.children.length > 0;
  const isExpanded = expanded[node.id];
  const indent = level * 20;

  const getTypeColor = (type: string) => {
    if (type === "Container") return "text-blue-600 dark:text-blue-400";
    if (type.startsWith("List[")) return "text-purple-600 dark:text-purple-400";
    return "text-green-600 dark:text-green-400";
  };

  const getNodeIcon = () => {
    if (!hasChildren) return "●";
    return isExpanded ? "▼" : "▶";
  };

  return (
    <div className="select-none">
      <div
        className={`flex items-center py-1 px-2 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 group ${
          level === 0 ? "bg-lime-50 dark:bg-lime-950 border border-lime-200 dark:border-lime-800" : ""
        }`}
        style={{ marginLeft: `${indent}px` }}
        onClick={() => hasChildren && onToggle(node.id)}
      >
        <span className={`w-4 text-center text-xs ${hasChildren ? "text-gray-600 dark:text-gray-400" : "text-gray-400"}`}>
          {getNodeIcon()}
        </span>
        
        <div className="flex items-center space-x-2 flex-1 ml-2">
          <span className={`font-mono font-semibold ${level === 0 ? "text-lime-600 dark:text-lime-400" : "text-gray-900 dark:text-gray-100"}`}>
            {node.name}
          </span>
          
          <span className={`font-mono text-sm ${getTypeColor(node.type)}`}>
            {node.type}
          </span>
          
          {node.required && (
            <span className="text-red-500 text-xs font-semibold">*</span>
          )}
          
          {node.constraints && (
            <span className="text-orange-600 dark:text-orange-400 text-xs bg-orange-100 dark:bg-orange-900 px-2 py-1 rounded">
              {node.constraints}
            </span>
          )}
        </div>
        
        {node.description && (
          <div className="text-gray-600 dark:text-gray-400 text-xs max-w-md opacity-0 group-hover:opacity-100 transition-opacity">
            {node.description}
          </div>
        )}
      </div>
      
      {hasChildren && isExpanded && (
        <div className="space-y-0">
          {node.children!.map((child, index) => (
            <TreeNodeComponent
              key={child.id}
              node={child}
              level={level + 1}
              expanded={expanded}
              onToggle={onToggle}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function SchemaTree() {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    root: true,
    account_changes: true,
  });

  const toggleNode = (id: string) => {
    setExpanded(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  return (
    <div className="bg-gray-200 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-lg p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
            Interactive Schema Tree
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Explore the EIP-7928 Block Access List structure
          </p>
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Click to expand/collapse • Hover for details
        </div>
      </div>

      <div className="space-y-1 font-mono text-sm">
        <TreeNodeComponent
          node={schemaData}
          level={0}
          expanded={expanded}
          onToggle={toggleNode}
        />
      </div>

      <div className="mt-4 pt-4 border-t border-gray-300 dark:border-gray-600">
        <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <span className="text-red-500">*</span>
              <span>Required field</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="text-blue-600 dark:text-blue-400">●</span>
              <span>Container</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="text-purple-600 dark:text-purple-400">●</span>
              <span>Array</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="text-green-600 dark:text-green-400">●</span>
              <span>Primitive</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}