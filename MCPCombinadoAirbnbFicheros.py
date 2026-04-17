import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain.tools import tool
import json
from textwrap import indent
# lanzar pip install mcp_weather_server




async def main():

    client = MultiServerMCPClient(
        {
            "mcpServers": {
                "transport": "stdio",
                "command": "/home/inta/.nvm/versions/node/v20.20.2/bin/npx", 
                "args": [
                    "-y",
                    "@openbnb/mcp-server-airbnb",
                    "--ignore-robots-txt"
                ]
                            
            },
            
            "filesystem": {
            "transport": "stdio", # stdio
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "/home/inta/Documentos"
            ]
            }
        }
    )

    # Nos descargamos las herramientas
    tools = await client.get_tools()

    try:
        prompts = await client.get_prompt("weather", "nombrePrompt1") # Ejemplo
    except Exception as e:
        print("No existe el prompt con el nombre asociado")
    
    try:
        resources = await client.get_resources()
    except Exception as e:
        print("No existen recursos en este MCP")

    agente = create_agent(
        model=ChatOllama(model="gemma4:26b", reasoning=True, num_ctx=100000),
        tools=tools,
        system_prompt="Eres un asistente que llama a herramientas. " \
        "Devuelve la salida en español si la tool devuelve la información en inglés."
    )


    while (prompt := input("> ")) != "end":
       async for paso in agente.astream({
            "messages": [
                HumanMessage(prompt)
            ]
        }, stream_mode="values"):
            ultimo_mensaje = paso["messages"][-1]

            hayRazonamiento = ""
            if hasattr(ultimo_mensaje, "additional_kwargs"): # sí, asi de escondido está el razonamiento
                hayRazonamiento = ultimo_mensaje.additional_kwargs.get("reasoning_content", "")

            if hayRazonamiento:
                print("\n=== PENSANDO ===")
                print(hayRazonamiento)

            print("\n=== MENSAJE ===")
            ultimo_mensaje.pretty_print()


# Lanzamos de forma concurrente. Es como la clase Thread de Java
asyncio.run(main())