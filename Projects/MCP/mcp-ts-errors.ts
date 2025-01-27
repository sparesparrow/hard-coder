// src/errors.ts
export class ToolExecutionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ToolExecutionError';
  }
}

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class ConnectionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConnectionError';
  }
}

export class TransportError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'TransportError';
  }
}
