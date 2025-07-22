// BAL Schema Configuration
// This file loads and processes the JSON Schema definition for Block Access Lists

import balSchema from "../schema/block-access-list.json";

export interface SchemaType {
  name: string;
  description: string;
  size?: string;
  encoding?: string;
  pattern?: string;
  examples?: string[];
}

export interface SchemaConstant {
  name: string;
  value: number | string;
  description: string;
  unit?: string;
}

export interface SchemaExample {
  title: string;
  description: string;
  data: any;
}

export interface SchemaField {
  name: string;
  type: string;
  description: string;
  constraints?: string;
  example?: string;
}

export interface SchemaContainer {
  name: string;
  type: string;
  description: string;
  fields?: SchemaField[];
  children?: SchemaContainer[];
  constraints?: string;
  example?: string;
}

// Extract constants from JSON Schema
export const SCHEMA_CONSTANTS: SchemaConstant[] = Object.entries(
  balSchema["x-constants"] || {}
).map(([name, config]: [string, any]) => ({
  name,
  value: config.value,
  description: config.description,
  unit: name === "MAX_CODE_SIZE" ? "bytes" : undefined,
}));

// Extract primitive types from JSON Schema
export const PRIMITIVE_TYPES: SchemaType[] = Object.entries(
  balSchema.$defs || {}
)
  .filter(
    ([name]) =>
      !name.includes("Account") &&
      !name.includes("Balance") &&
      !name.includes("PerTx") &&
      !name.includes("Slot")
  )
  .map(([name, def]: [string, any]) => ({
    name,
    description: def.description || def.title || "",
    size: getSizeFromType(name, def),
    encoding: getEncodingFromType(name, def),
    pattern: def.pattern,
    examples: def.examples,
  }));

function getSizeFromType(name: string, def: any): string {
  switch (name) {
    case "Address":
      return "20 bytes";
    case "StorageKey":
    case "StorageValue":
      return "32 bytes";
    case "BalanceDelta":
      return "12 bytes";
    case "TxIndex":
      return "2 bytes";
    case "Nonce":
      return "8 bytes";
    case "CodeData":
      return "≤24 KiB";
    default:
      return "";
  }
}

function getEncodingFromType(name: string, def: any): string {
  switch (name) {
    case "Address":
      return "ByteVector(20)";
    case "StorageKey":
    case "StorageValue":
      return "ByteVector(32)";
    case "BalanceDelta":
      return "ByteVector(12)";
    case "TxIndex":
      return "uint16";
    case "Nonce":
      return "uint64";
    case "CodeData":
      return "ByteVector(24576)";
    default:
      return "";
  }
}

// Convert JSON Schema to our schema structure format
function convertJsonSchemaToContainer(schema: any): SchemaContainer {
  return {
    name: "BlockAccessList",
    type: "Container",
    description: schema.description,
    children: Object.entries(schema.properties).map(
      ([name, prop]: [string, any]) => convertPropertyToContainer(name, prop, schema)
    ),
  };
}

function convertPropertyToContainer(name: string, prop: any, schema: any): SchemaContainer {
  if (prop.type === "array" && prop.items?.$ref) {
    const refName = prop.items.$ref.split("/").pop();
    const refDef = (schema.$defs as any)[refName];
    
    return {
      name,
      type: `List[${refName}]`,
      description: prop.description,
      constraints: prop.maxItems ? `Max ${prop.maxItems.toLocaleString()} items` : undefined,
      children: refDef ? [convertDefinitionToContainer(refDef, refName)] : undefined,
    };
  }
  
  return {
    name,
    type: prop.type,
    description: prop.description,
    constraints: getFieldConstraints(prop),
  };
}

function convertDefinitionToContainer(
  def: any,
  name?: string
): SchemaContainer {
  const container: SchemaContainer = {
    name: name || def.title || "Unknown",
    type: "Container",
    description: def.description,
  };

  if (def.properties) {
    const fields: SchemaField[] = [];
    const children: SchemaContainer[] = [];

    const addedContainers = new Set<string>();

    Object.entries(def.properties).forEach(([fieldName, fieldDef]: [string, any]) => {
      const isRequired = def.required && def.required.includes(fieldName);
      
      // Add field info
      fields.push({
        name: fieldName,
        type: getFieldType(fieldDef),
        description: fieldDef.description,
        constraints: getFieldConstraints(fieldDef, isRequired),
        example: fieldDef.examples?.[0],
      });

      // Add nested containers for complex types (avoid duplicates)
      let refName: string | undefined;
      if (fieldDef.$ref) {
        refName = fieldDef.$ref.split("/").pop();
      } else if (fieldDef.type === "array" && fieldDef.items?.$ref) {
        refName = fieldDef.items.$ref.split("/").pop();
      }
      
      if (refName && (balSchema.$defs as any)[refName] && !addedContainers.has(refName)) {
        children.push(convertDefinitionToContainer((balSchema.$defs as any)[refName], refName));
        addedContainers.add(refName);
      }
    });

    if (fields.length > 0) container.fields = fields;
    if (children.length > 0) container.children = children;
  }

  return container;
}

function getFieldType(prop: any): string {
  if (prop.$ref) {
    return prop.$ref.split("/").pop() || "Unknown";
  }
  if (prop.type === "array") {
    const itemType = prop.items?.$ref?.split("/").pop() || prop.items?.type || "Unknown";
    return `List[${itemType}]`;
  }
  return prop.type;
}

function getFieldConstraints(prop: any, isRequired: boolean = false): string | undefined {
  const constraints = [];
  
  if (isRequired) {
    constraints.push("Required");
  } else if (prop.default !== undefined) {
    constraints.push(`Default: ${JSON.stringify(prop.default)}`);
  }
  
  if (prop.minimum !== undefined) constraints.push(`>= ${prop.minimum}`);
  if (prop.maximum !== undefined) constraints.push(`<= ${prop.maximum}`);
  if (prop.pattern) constraints.push(`Pattern: ${prop.pattern}`);
  if (prop.maxLength) constraints.push(`Max length: ${prop.maxLength}`);
  if (prop.maxItems) constraints.push(`Max ${prop.maxItems.toLocaleString()} items`);
  
  return constraints.length > 0 ? constraints.join(", ") : undefined;
}

export const SCHEMA_STRUCTURE: SchemaContainer =
  convertJsonSchemaToContainer(balSchema);

// Extract field explanations from JSON Schema
export const FIELD_EXPLANATIONS = balSchema["x-implementation-notes"] || {};

// Extract validation rules from JSON Schema
export const VALIDATION_RULES = Object.entries(balSchema.properties || {}).map(
  ([field, prop]: [string, any]) => ({
    field,
    rule: prop.maxItems ? `Max ${prop.maxItems} items` : prop.description,
    rationale: `Schema constraint for ${field}`,
  })
);
