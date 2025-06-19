"use client";

import { useState } from "react";
import {
  SCHEMA_STRUCTURE,
  SchemaContainer,
  SchemaField,
} from "../config/schema";

// Convert config structure to tree format
function convertToTreeNode(container: SchemaContainer): TreeSchemaNode {
  const node: TreeSchemaNode = {
    name: container.name,
    type: container.type,
    description: container.description,
    constraints: container.constraints,
    example: container.example,
  };

  // Convert fields to children
  if (container.fields) {
    node.children = container.fields.map((field) => ({
      name: field.name,
      type: field.type,
      description: field.description,
      constraints: field.constraints,
      example: field.example,
    }));
  }

  // Add nested containers as children
  if (container.children) {
    const containerChildren = container.children.map(convertToTreeNode);
    if (node.children) {
      node.children.push(...containerChildren);
    } else {
      node.children = containerChildren;
    }
  }

  return node;
}

interface TreeSchemaNode {
  name: string;
  type: string;
  description?: string;
  children?: TreeSchemaNode[];
  constraints?: string;
  example?: string;
}

const schemaData: TreeSchemaNode = convertToTreeNode(SCHEMA_STRUCTURE);

interface TreeNodeProps {
  node: TreeSchemaNode;
  level: number;
}

function TreeNode({ node, level }: TreeNodeProps) {
  const [isExpanded, setIsExpanded] = useState(level < 2);
  const hasChildren = node.children && node.children.length > 0;

  const indent = level * 24;
  const isContainer = node.type.includes("Container");
  const isList = node.type.includes("List");

  return (
    <div className="select-none">
      <div
        className={`flex items-center py-2 px-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer group ${
          level === 0
            ? "bg-lime-50 dark:bg-lime-950 border border-lime-200 dark:border-lime-800"
            : ""
        }`}
        style={{ marginLeft: `${indent}px` }}
        onClick={() => hasChildren && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-2 flex-1">
          {hasChildren && (
            <div
              className={`w-4 h-4 flex items-center justify-center text-gray-400 transition-transform duration-200 ease-in-out ${
                isExpanded ? "rotate-90" : ""
              }`}
            >
              ▶
            </div>
          )}
          {!hasChildren && <div className="w-4"></div>}

          <div className="flex items-center space-x-3 flex-1">
            <span
              className={`font-mono font-bold ${
                level === 0
                  ? "text-lime-600 dark:text-lime-400 text-lg"
                  : isContainer
                  ? "text-blue-600 dark:text-blue-400"
                  : isList
                  ? "text-purple-600 dark:text-purple-400"
                  : "text-gray-900 dark:text-gray-100"
              }`}
            >
              {node.name}
            </span>

            <span className="text-gray-500 dark:text-gray-400 font-mono text-sm">
              {node.type}
            </span>

            {node.constraints && (
              <span className="text-orange-600 dark:text-orange-400 font-mono text-xs bg-orange-100 dark:bg-orange-900 px-2 py-1 rounded">
                {node.constraints}
              </span>
            )}
          </div>
        </div>

        {node.description && (
          <div className="text-gray-600 dark:text-gray-400 text-sm max-w-md opacity-0 group-hover:opacity-100 transition-opacity">
            {node.description}
          </div>
        )}
      </div>

      {node.example && isExpanded && (
        <div className="ml-8 mt-2 mb-4 bg-gray-900 text-green-400 p-3 rounded font-mono text-xs">
          Example: {node.example}
        </div>
      )}

      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          hasChildren && isExpanded
            ? "max-h-[2000px] opacity-100"
            : "max-h-0 opacity-0"
        }`}
      >
        {hasChildren && (
          <div className="space-y-1 pt-2">
            {node.children!.map((child, index) => (
              <div
                key={index}
                className={`transform transition-all duration-200 ease-out ${
                  isExpanded
                    ? "translate-y-0 opacity-100"
                    : "-translate-y-2 opacity-0"
                }`}
                style={{
                  transitionDelay: isExpanded ? `${index * 50}ms` : "0ms",
                }}
              >
                <TreeNode node={child} level={level + 1} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function SchemaTree() {
  return (
    <div className="bg-gray-200 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-700 rounded-lg p-6">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
          Schema Explorer
        </h3>
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Click to expand/collapse • Hover for details
        </div>
      </div>

      <div className="space-y-1">
        <TreeNode node={schemaData} level={0} />
      </div>
    </div>
  );
}
