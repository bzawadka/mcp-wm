#!/usr/bin/env python3
"""
MCP Wealth Management Server - Phase 1
Client Advisory Tools for Wealth Management

This server provides tools for client advisors to manage and query client information.
Phase 1 includes: Tool 1 - Client List Management
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import random

# MCP imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wealth-management-mcp-server")


class WealthManagementServer:
    def __init__(self):
        self.server = Server("wealth-management-mcp-server")
        self.clients_data = self._generate_sample_clients()
        
        # Register tools
        self._register_tools()
        
        # Set up request handlers
        self._setup_handlers()
    
    def _generate_sample_clients(self) -> List[Dict[str, Any]]:
        """Generate sample client data for testing"""
        clients = []
        
        # Sample client names - famous Polish people
        sample_names = [
            "Marie Curie", "Lech Wałęsa", "Frédéric Chopin", "Nicolaus Copernicus",
            "Andrzej Wajda", "Wisława Szymborska", "Krzysztof Kieślowski", "Stanisław Lem",
            "Jerzy Grotowski", "Agnieszka Holland", "Roman Polanski", "Henryk Górecki",
            "Czesław Miłosz", "Witold Gombrowicz", "Krzysztof Penderecki", "Andrzej Sapkowski",
            "Magdalena Abakanowicz", "Zbigniew Brzezinski", "Jan Karski", "Irena Sendler"
        ]
        
        client_types = ["Individual", "Corporate", "Trust", "Foundation"]
        risk_profiles = ["Conservative", "Moderate", "Aggressive", "Very Aggressive"]
        
        for i in range(20):  # Generate 20 sample clients
            client_id = f"BZ-{str(i+1).zfill(5)}"  # BZ-00001, BZ-00002, etc.
            
            # Random client data
            name = sample_names[i] if i < len(sample_names) else f"Polish Client {i+1}"
            
            client = {
                "client_id": client_id,
                "name": name,
                "client_type": random.choice(client_types),
                "risk_profile": random.choice(risk_profiles),
                "onboarding_date": (datetime.now() - timedelta(days=random.randint(30, 1095))).strftime("%Y-%m-%d"),
                "total_aum": round(random.uniform(100000, 50000000), 2),  # Assets Under Management
                "currency": "USD",
                "advisor_notes": f"Client since {2020 + random.randint(0, 4)}. {random.choice(['Active trader', 'Long-term investor', 'Income focused', 'Growth oriented'])}.",
                "last_review": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                "status": random.choice(["Active", "Active", "Active", "Under Review"])  # Mostly active
            }
            
            clients.append(client)
        
        return clients
    
    def _register_tools(self):
        """Register all MCP tools"""
        
        # Tool 1: Get client list
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            return [
                Tool(
                    name="get_clients",
                    description="Retrieve list of all clients managed by the advisor. Returns comprehensive client information including IDs, names, risk profiles, and AUM.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter_by": {
                                "type": "string",
                                "description": "Optional filter criteria: 'active', 'under_review', 'high_aum' (>10M), 'new_clients' (last 90 days)",
                                "enum": ["active", "under_review", "high_aum", "new_clients", "all"]
                            },
                            "sort_by": {
                                "type": "string",
                                "description": "Sort criteria for client list",
                                "enum": ["name", "client_id", "total_aum", "onboarding_date", "last_review"]
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of clients to return (default: all)",
                                "minimum": 1,
                                "maximum": 100
                            }
                        },
                        "required": []
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            if name == "get_clients":
                return await self._get_clients(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")


    async def _get_clients(self, arguments: dict) -> list[TextContent]:
        logger.info("Serving clients request with arguments: %s", arguments)

        """Handle get_clients tool calls"""
        try:
            filter_by = arguments.get("filter_by", "all")
            sort_by = arguments.get("sort_by", "name")
            limit = arguments.get("limit", None)
            
            # Filter clients
            filtered_clients = self._filter_clients(filter_by)
            
            # Sort clients
            filtered_clients = self._sort_clients(filtered_clients, sort_by)
            
            # Apply limit
            if limit:
                filtered_clients = filtered_clients[:limit]
            
            # Prepare response
            response = {
                "status": "success",
                "total_clients": len(filtered_clients),
                "filter_applied": filter_by,
                "sort_by": sort_by,
                "clients": filtered_clients
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(response, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error in get_clients: {str(e)}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Error retrieving client list: {str(e)}"
                })
            )]


    def _filter_clients(self, filter_by: str) -> List[Dict[str, Any]]:
        """Filter clients based on criteria"""
        if filter_by == "all":
            return self.clients_data
        
        filtered = []
        current_date = datetime.now()
        
        for client in self.clients_data:
            if filter_by == "active":
                if client["status"] == "Active":
                    filtered.append(client)
            elif filter_by == "under_review":
                if client["status"] == "Under Review":
                    filtered.append(client)
            elif filter_by == "high_aum":
                if client["total_aum"] > 10000000:  # >10M
                    filtered.append(client)
            elif filter_by == "new_clients":
                onboarding_date = datetime.strptime(client["onboarding_date"], "%Y-%m-%d")
                if (current_date - onboarding_date).days <= 90:
                    filtered.append(client)
        
        return filtered


    def _sort_clients(self, clients: List[Dict[str, Any]], sort_by: str) -> List[Dict[str, Any]]:
        """Sort clients based on criteria"""
        if sort_by == "name":
            return sorted(clients, key=lambda x: x["name"])
        elif sort_by == "client_id":
            return sorted(clients, key=lambda x: x["client_id"])
        elif sort_by == "total_aum":
            return sorted(clients, key=lambda x: x["total_aum"], reverse=True)
        elif sort_by == "onboarding_date":
            return sorted(clients, key=lambda x: x["onboarding_date"], reverse=True)
        elif sort_by == "last_review":
            return sorted(clients, key=lambda x: x["last_review"], reverse=True)
        else:
            return clients


    def _setup_handlers(self):
        """Set up additional MCP handlers"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            return []
        
        @self.server.read_resource()
        async def handle_read_resource(uri: 'AnyUrl') -> str:
            raise ValueError(f"Resource not found: {uri}")


    async def run(self):
        """Run the MCP server"""
        logger.info("Starting Wealth Management MCP Server - Phase 1")
        logger.info(f"Generated {len(self.clients_data)} sample clients")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="wealth-management-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities=dict(),
                    ),
                ),
            )


async def main():
    """Main entry point"""
    server = WealthManagementServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())