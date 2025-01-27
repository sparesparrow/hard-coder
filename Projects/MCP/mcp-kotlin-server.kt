// src/main/kotlin/io/mcp/server/model/Types.kt
package io.mcp.server.model

import io.modelcontextprotocol.kotlin.sdk.types.*

data class ToolDefinition(
    val name: String,
    val description: String,
    val inputSchema: Map<String, Any>,
    val examples: List<ToolExample>? = null
)

data class ToolExample(
    val description: String,
    val arguments: Map<String, Any>
)

data class ToolContext(
    val progressReporter: suspend (current: Int, total: Int) -> Unit,
    val resourceLoader: suspend (uri: String) -> String,
    val logger: (level: String, message: String) -> Unit
)

// src/main/kotlin/io/mcp/server/tool/ToolExecutor.kt
package io.mcp.server.tool

import io.mcp.server.model.ToolContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import java.io.File

class ToolExecutor(private val logger: Logger = LoggerFactory.getLogger(ToolExecutor::class.java)) {
    suspend fun executeCommand(
        command: String, 
        args: List<String>,
        context: ToolContext
    ): String = withContext(Dispatchers.IO) {
        try {
            val process = ProcessBuilder(command)
                .apply { command().addAll(args) }
                .redirectOutput(ProcessBuilder.Redirect.PIPE)
                .redirectError(ProcessBuilder.Redirect.PIPE)
                .start()

            context.progressReporter(0, 100)
            
            val result = process.inputStream.bufferedReader().use { it.readText() }
            val error = process.errorStream.bufferedReader().use { it.readText() }
            
            process.waitFor()
            context.progressReporter(100, 100)

            if (process.exitValue() != 0) {
                throw RuntimeException("Command failed: $error")
            }

            result
        } catch (e: Exception) {
            logger.error("Failed to execute command: $command", e)
            throw e
        }
    }

    suspend fun analyzeCSV(
        filepath: String,
        operations: List<String>,
        context: ToolContext
    ): String = withContext(Dispatchers.IO) {
        try {
            val file = File(filepath)
            if (!file.exists()) {
                throw IllegalArgumentException("File not found: $filepath")
            }

            // Implement CSV analysis here
            "CSV analysis result"
        } catch (e: Exception) {
            logger.error("Failed to analyze CSV: $filepath", e)
            throw e
        }
    }
}

// src/main/kotlin/io/mcp/server/MCPServer.kt
package io.mcp.server

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import io.mcp.server.model.ToolDefinition
import io.mcp.server.model.ToolContext
import io.mcp.server.tool.ToolExecutor
import io.modelcontextprotocol.kotlin.sdk.Implementation
import io.modelcontextprotocol.kotlin.sdk.server.Server
import io.modelcontextprotocol.kotlin.sdk.server.ServerCapabilities
import io.modelcontextprotocol.kotlin.sdk.server.ServerOptions
import io.modelcontextprotocol.kotlin.sdk.types.*
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import org.slf4j.LoggerFactory
import java.io.File

class MCPServer(
    private val config: ServerConfig,
    private val scope: CoroutineScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
) : Server(
    Implementation("kotlin-mcp-server", "1.0.0"),
    ServerOptions(
        capabilities = ServerCapabilities(
            tools = ServerCapabilities.Tools(listChanged = true),
            logging = ServerCapabilities.Logging(),
            resources = ServerCapabilities.Resources(
                subscribe = true,
                listChanged = true
            )
        )
    )
) {
    private val logger = LoggerFactory.getLogger(MCPServer::class.java)
    private val mapper = jacksonObjectMapper()
    private val toolExecutor = ToolExecutor()
    private var tools: List<ToolDefinition> = emptyList()

    init {
        setupHandlers()
        loadTools()
    }

    private fun loadTools() {
        try {
            val toolsFile = File(config.toolsPath)
            if (!toolsFile.exists()) {
                logger.error("Tools file not found: ${config.toolsPath}")
                return
            }

            tools = mapper.readValue(toolsFile)
            logger.info("Loaded ${tools.size} tools")
        } catch (e: Exception) {
            logger.error("Failed to load tools", e)
        }
    }

    private fun setupHandlers() {
        // List tools handler
        addListToolsHandler { 
            ListToolsResult(
                tools = tools.map { tool ->
                    Tool(
                        name = tool.name,
                        description = tool.description,
                        inputSchema = tool.inputSchema
                    )
                }
            )
        }

        // Call tool handler
        addCallToolHandler { request ->
            val tool = tools.find { it.name == request.name }
                ?: throw IllegalArgumentException("Tool not found: ${request.name}")

            validateToolArguments(tool, request.arguments)

            try {
                val context = ToolContext(
                    progressReporter = { current, total ->
                        request.progressToken?.let { token ->
                            scope.launch {
                                sendProgress(token, current, total)
                            }
                        }
                    },
                    resourceLoader = { uri ->
                        readResource(uri).contents.first().text
                    },
                    logger = { level, message ->
                        when (level) {
                            "info" -> logger.info(message)
                            "warn" -> logger.warn(message)
                            "error" -> logger.error(message)
                            else -> logger.debug(message)
                        }
                    }
                )

                val result = when (tool.name) {
                    "execute_command" -> toolExecutor.executeCommand(
                        request.arguments["command"] as String,
                        (request.arguments["args"] as? List<String>) ?: emptyList(),
                        context
                    )
                    "analyze_csv" -> toolExecutor.analyzeCSV(
                        request.arguments["filepath"] as String,
                        (request.arguments["operations"] as? List<String>) ?: emptyList(),
                        context
                    )
                    else -> throw IllegalArgumentException("Unsupported tool: ${tool.name}")
                }

                CallToolResult(
                    content = listOf(
                        TextContent(
                            type = "text",
                            text = result
                        )
                    )
                )
            } catch (e: Exception) {
                logger.error("Tool execution failed", e)
                CallToolResult(
                    isError = true,
                    content = listOf(
                        TextContent(
                            type = "text",
                            text = "Error: ${e.message}"
                        )
                    )
                )
            }
        }
    }

    private fun validateToolArguments(
        tool: ToolDefinition,
        arguments: Map<String, Any>?
    ) {
        val requiredArgs = tool.inputSchema["required"] as? List<String> ?: emptyList()
        val missingArgs = requiredArgs.filter { !arguments?.containsKey(it) ?: true }
        
        if (missingArgs.isNotEmpty()) {
            throw IllegalArgumentException(
                "Missing required arguments: ${missingArgs.joinToString()}"
            )
        }
    }
}

// src/main/kotlin/io/mcp/server/transport/TransportManager.kt
package io.mcp.server.transport

import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.routing.*
import io.ktor.server.response.*
import io.modelcontextprotocol.kotlin.sdk.server.Server
import io.modelcontextprotocol.kotlin.sdk.server.SSEServerTransport
import io.modelcontextprotocol.kotlin.sdk.server.StdioServerTransport
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.launch
import org.slf4j.LoggerFactory

class TransportManager(
    private val server: Server,
    private val config: ServerConfig,
    private val scope: CoroutineScope
) {
    private val logger = LoggerFactory.getLogger(TransportManager::class.java)
    private var httpServer: ApplicationEngine? = null

    suspend fun start() {
        when (config.transport) {
            Transport.STDIO -> startStdio()
            Transport.HTTP -> startHttp()
        }
    }

    private suspend fun startStdio() {
        val transport = StdioServerTransport()
        server.connect(transport)
        logger.info("Started stdio transport")
    }

    private suspend fun startHttp() {
        val transport = SSEServerTransport()
        
        val server = embeddedServer(Netty, port = config.port) {
            routing {
                get("/sse") {
                    transport.handleSSE(call)
                }
                
                post("/message") {
                    transport.handleMessage(call)
                }
            }
        }

        httpServer = server.start()
        logger.info("Started HTTP transport on port ${config.port}")
    }

    suspend fun stop() {
        httpServer?.stop(1000, 2000)
        logger.info("Stopped transport")
    }
}

// src/main/kotlin/io/mcp/server/Config.kt
package io.mcp.server

data class ServerConfig(
    val toolsPath: String,
    val port: Int = 8000,
    val transport: Transport = Transport.STDIO,
    val logLevel: String = "INFO"
)

enum class Transport {
    STDIO, HTTP
}

// src/main/kotlin/io/mcp/server/Main.kt
package io.mcp.server

import kotlinx.coroutines.runBlocking
import org.slf4j.LoggerFactory
import kotlin.system.exitProcess

fun main(args: Array<String>) = runBlocking {
    val logger = LoggerFactory.getLogger("Main")

    val config = ServerConfig(
        toolsPath = System.getenv("TOOLS_PATH") ?: "tools.json",
        port = System.getenv("PORT")?.toIntOrNull() ?: 8000,
        transport = System.getenv("TRANSPORT")?.let {
            when (it.uppercase()) {
                "HTTP" -> Transport.HTTP
                else -> Transport.STDIO
            }
        } ?: Transport.STDIO,
        logLevel = System.getenv("LOG_LEVEL") ?: "INFO"
    )

    try {
        val server = MCPServer(config)
        val transportManager = TransportManager(server, config, this)
        
        // Handle shutdown gracefully
        Runtime.getRuntime().addShutdownHook(Thread {
            runBlocking {
                logger.info("Shutting down...")
                transportManager.stop()
            }
        })

        transportManager.start()
        logger.info("Server started successfully")
    } catch (e: Exception) {
        logger.error("Failed to start server", e)
        exitProcess(1)
    }
}
