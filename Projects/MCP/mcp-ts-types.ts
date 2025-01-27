// src/types.ts
export interface ToolDefinition {
  name: string;
  description: string;
  input_schema: {
    type: "object";
    properties?: Record<string, unknown>;
    required?: string[];
  };
  examples?: Array<{
    description: string;
    arguments: Record<string, unknown>;
  }>;
}

export interface ServerConfig {
  toolsPath: string;
  port?: number;
  transport: "stdio" | "sse";
  logLevel?: "debug" | "info" | "warn" | "error";
}

export interface ClientConfig {
  transport: 'stdio' | 'http';
  serverUrl?: string;
  serverCommand?: string;
  serverArgs?: string[];
  onProgress?: (current: number, total: number) => void;
  logLevel?: string;
}

export interface ToolContext {
  progressCallback?: (current: number, total: number) => Promise<void>;
  resourceLoader?: (uri: string) => Promise<string>;
  logger?: (level: string, message: string) => void;
}

export interface Logger {
  debug(message: string, ...args: any[]): void;
  info(message: string, ...args: any[]): void;
  warn(message: string, ...args: any[]): void;
  error(message: string, ...args: any[]): void;
}
