from typing import Any
from modules.config import Settings
from modules.oci_client import Client
from modules.db import DataBase
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
load_dotenv()
from langchain_community.chat_models import ChatOCIGenAI
from langgraph.prebuilt import create_react_agent

mcp = FastMCP("file_server")

settings = Settings("path")

llm = ChatOCIGenAI(
    model_id="cohere.command-a-03-2025",
    service_endpoint=settings.oci_client.endpoint,
    compartment_id=settings.oci_client.compartiment,
    model_kwargs={"temperature":0.7, "max_tokens":500},
    auth_profile=settings.oci_client.configProfile,
    auth_file_location=settings.oci_client.config_path
)

agent = create_react_agent(
    model=llm
)

@mcp.tool()
def split_file_content(content:str)->str:
    """ Uses a text splitter to reduce the file content into the core components and have a smaller file size """

@mcp.tool()
def build_metadata(content:str)->str:
    """ Given the content of a file, generates a JSON metadata format """

