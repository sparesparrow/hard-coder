// src/server/server.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { readFile } from 'fs/promises';
import { ToolDefinition, ServerConfig, ToolContext, Logger } from '../types.js';
import { ToolExecutor } from './tool-executor.js';
import { TransportManager } from './transport-manager.js';
import { ValidationError, ToolExecutionError } from '../errors.js';

export class MCPServer extends Server {
  private tools: ToolDefinition[] = [];
  private toolExecutor: ToolExecutor;
  private config: ServerConfig;
  private logger: Logger;
  private transportManager?: TransportManager;

  constructor(config: ServerConfig, logger: Logger) {
    super({
      name: "mcp-typescript-server",
      version: "1.0.0",
    }, {
      capabilities: {
        tools: { listChanged: true },
        logging: {},
        resources: {
          subscribe: true,
          listChanged: true,
        },
        prompts: {
          listChanged: true
        }
      }
    });

    this.config = config;
    this.logger = logger;
    this.toolExecutor = new ToolExecutor(logger);
    this.setupRequestHandlers();
  }

  private async loadTools(): Promise<void> {
    try {
      const content = await readFile(this.config.toolsPath, 'utf-8');
      const tools = JSON.parse(content);
      
      await Promise.all(tools.map(tool => this.validateToolDefinition(tool)));
      
      this.tools = tools;
      this.logger.info(`Loaded ${tools.length} tools successfully`);
    } catch (error) {
      this.logger.error('Failed to load tools:', error);
      throw error;
    }
  }

  private validateToolDefinition(tool: unknown): asserts tool is ToolDefinition {
    if (!tool || typeof tool !== 'object') {
      throw new ValidationError('Tool must be an object');
    }

    const { name, description, input_schema } = tool as Partial<ToolDefinition>;

    if (!name || typeof name !== 'string') {
      throw new ValidationError('Tool must have a name string');
    }

    if (!description || typeof description !== 'string') {
      throw new ValidationError('Tool must have a description string');
    }

    if (!input_schema || typeof input_schema !== 'object') {
      throw new ValidationError('Tool must have an input_schema object');
    }

    if (input_schema.type !== 'object') {
      throw new ValidationError('Tool input_schema.type must be "object"');
    }
  }

  private setupRequestHandlers(): void {
    this.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: this.tools.map(tool => ({
          name: tool.name,
          description: tool.description,
          inputSchema: tool.input_schema
        }))
      };
    });

    this.setRequestHandler(CallToolRequestSchema, async (request) => {
      const progressToken = request.params._meta?.progressToken;
      const tool = this.tools.find(t => t.name === request.params.name);
      
      if (!tool) {
        throw new ValidationError(`Tool not found: ${request.params.name}`);
      }

      const context: ToolContext = {
        progressCallback: progressToken ? 
          async (current, total) => {
            await this.sendProgress(progressToken, current, total);
          } : undefined,
        resourceLoader: async (uri) => {
          const result = await this.readResource(uri);
          return result.contents[0].text;
        },
        logger: (level, message) => {
          this.logger[level](message);
        }
      };

      try {
        const result = await this.executeTool(
          tool, 
          request.params.arguments || {},
          context
        );
        
        return {
          content: [{
            type: "text",
            text: result
          }]
        };
      } catch (error) {
        this.logger.error('Tool execution failed:', error);
        
        return {
          isError: true,
          content: [{
            type: "text",
            text: error instanceof Error ? error.message : 'Unknown error'
          }]
        };
      }
    });
  }

  private async executeTool(
    tool: ToolDefinition,
    arguments_: Record<string, unknown>,
    context: ToolContext
  ): Promise<string> {
    const required = tool.input_schema.required || [];
    const missing = required.filter(arg => !(arg in arguments_));
    
    if (missing.length > 0) {
      throw new ValidationError(`Missing required arguments: ${missing.join(', ')}`);
    }

    try {
      return await this.toolExecutor.execute(tool.name, arguments_, context);
    } catch (error) {
      this.logger.error('Tool execution error:', {
        tool: tool.name,
        arguments: arguments_,
        error
      });
      throw error instanceof Error ? error : new ToolExecutionError('Unknown error');
    }
  }

  async start(): Promise<void> {
    try {
      await this.loadTools();
      
      this.transportManager = new TransportManager(
        this,
        this.config.transport,
        this.config.port,
        this.logger
      );
      
      await this.transportManager.start();
      this.logger.info(`Server started with ${this.config.transport} transport`);
    } catch (error) {
      this.logger.error('Failed to start server:', error);
      throw error;
    }
  }

  async stop(): Promise<void> {
    try {
      await this.transportManager?.stop();
      this.logger.info('Server stopped');
    } catch (error) {
      this.logger.error('Error stopping server:', error);
      throw error;
    }
  }
}
