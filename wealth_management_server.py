#!/usr/bin/env python3
"""
MCP Wealth Management Server
Client Advisory Tools for Wealth Management

This server provides tools for client advisors to manage and query client information.
Phase 1: Tool 1 - Client List Management
Phase 2: Tool 2 - Client Position Management
Phase 3: Tool 3 - Recommendations Tool
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
    # Recommendations database - simulates research team recommendations
    RECOMMENDATIONS_DATABASE = {
        # Technology stocks - mixed recommendations
        "US0378331005": {"rating": "BUY", "target_price": 250.00, "analyst": "Tech Research Team", "last_updated": "2025-07-18", "rationale": "Strong iPhone sales and AI integration"},
        "US5949181045": {"rating": "BUY", "target_price": 480.00, "analyst": "Tech Research Team", "last_updated": "2025-07-17", "rationale": "Azure growth and AI leadership"},
        "US02079K3059": {"rating": "NEUTRAL", "target_price": 180.00, "analyst": "Tech Research Team", "last_updated": "2025-07-16", "rationale": "Search market maturity offset by AI opportunities"},
        "US0231351067": {"rating": "BUY", "target_price": 200.00, "analyst": "Consumer Research Team", "last_updated": "2025-07-15", "rationale": "AWS growth and retail optimization"},
        "US88160R1014": {"rating": "SELL", "target_price": 180.00, "analyst": "Auto Research Team", "last_updated": "2025-07-19", "rationale": "EV market competition intensifying"},
        "US17275R1023": {"rating": "NEUTRAL", "target_price": 55.00, "analyst": "Tech Research Team", "last_updated": "2025-07-14", "rationale": "Steady networking demand but limited growth"},
        "US4592001014": {"rating": "SELL", "target_price": 35.00, "analyst": "Semiconductor Team", "last_updated": "2025-07-18", "rationale": "Losing market share to AMD and ARM"},
        "US6174464486": {"rating": "BUY", "target_price": 120.00, "analyst": "Financial Services Team", "last_updated": "2025-07-17", "rationale": "Strong wealth management division"},
        "US30303M1027": {"rating": "NEUTRAL", "target_price": 550.00, "analyst": "Tech Research Team", "last_updated": "2025-07-16", "rationale": "Metaverse investments vs. core business strength"},
        "US67066G1040": {"rating": "BUY", "target_price": 1200.00, "analyst": "AI Research Team", "last_updated": "2025-07-19", "rationale": "AI chip demand continues to surge"},
        
        # Bonds - generally neutral/conservative recommendations
        "US912828Z490": {"rating": "BUY", "target_price": 102.50, "analyst": "Fixed Income Team", "last_updated": "2025-07-18", "rationale": "Safe haven amid market volatility"},
        "US9128283H60": {"rating": "NEUTRAL", "target_price": 98.75, "analyst": "Fixed Income Team", "last_updated": "2025-07-17", "rationale": "Duration risk vs. yield attractiveness"},
        "US037833100": {"rating": "BUY", "target_price": 104.25, "analyst": "Credit Research Team", "last_updated": "2025-07-16", "rationale": "Strong corporate fundamentals"},
        "US594918104": {"rating": "BUY", "target_price": 103.80, "analyst": "Credit Research Team", "last_updated": "2025-07-15", "rationale": "Excellent credit quality and yield"},
        "US02079K305": {"rating": "NEUTRAL", "target_price": 101.20, "analyst": "Credit Research Team", "last_updated": "2025-07-14", "rationale": "Fair value at current levels"},
        "US464287200": {"rating": "BUY", "target_price": 105.10, "analyst": "Financial Services Team", "last_updated": "2025-07-13", "rationale": "Bank strength supports credit"},
        "US254687FX05": {"rating": "SELL", "target_price": 96.50, "analyst": "Media Research Team", "last_updated": "2025-07-18", "rationale": "Streaming competition pressures"},
        "US717081103": {"rating": "NEUTRAL", "target_price": 102.00, "analyst": "Healthcare Team", "last_updated": "2025-07-17", "rationale": "Stable pharma fundamentals"}
    }

    SECURITIES_DATABASE = {
        # Equities
        "US0378331005": {"name": "Apple Inc.", "type": "equity", "sector": "Technology", "currency": "USD"},
        "US5949181045": {"name": "Microsoft Corp.", "type": "equity", "sector": "Technology", "currency": "USD"},
        "US02079K3059": {"name": "Alphabet Inc.", "type": "equity", "sector": "Technology", "currency": "USD"},
        "US0231351067": {"name": "Amazon.com Inc.", "type": "equity", "sector": "Consumer Discretionary", "currency": "USD"},
        "US88160R1014": {"name": "Tesla Inc.", "type": "equity", "sector": "Consumer Discretionary", "currency": "USD"},
        "US17275R1023": {"name": "Cisco Systems Inc.", "type": "equity", "sector": "Technology", "currency": "USD"},
        "US4592001014": {"name": "Intel Corp.", "type": "equity", "sector": "Technology", "currency": "USD"},
        "US6174464486": {"name": "Morgan Stanley", "type": "equity", "sector": "Financial Services", "currency": "USD"},
        "US30303M1027": {"name": "Meta Platforms Inc.", "type": "equity", "sector": "Technology", "currency": "USD"},
        "US67066G1040": {"name": "NVIDIA Corp.", "type": "equity", "sector": "Technology", "currency": "USD"},
        
        # Bonds
        "US912828Z490": {"name": "US Treasury 10Y", "type": "bond", "maturity": "2034-05-15", "currency": "USD"},
        "US9128283H60": {"name": "US Treasury 30Y", "type": "bond", "maturity": "2054-02-15", "currency": "USD"},
        "US037833100": {"name": "Apple Inc. Corporate Bond", "type": "bond", "maturity": "2032-02-23", "currency": "USD"},
        "US594918104": {"name": "Microsoft Corporate Bond", "type": "bond", "maturity": "2031-06-01", "currency": "USD"},
        "US02079K305": {"name": "Alphabet Corporate Bond", "type": "bond", "maturity": "2030-08-15", "currency": "USD"},
        "US464287200": {"name": "JPMorgan Chase Bond", "type": "bond", "maturity": "2029-04-23", "currency": "USD"},
        "US254687FX05": {"name": "Disney Corporate Bond", "type": "bond", "maturity": "2028-12-01", "currency": "USD"},
        "US717081103": {"name": "Pfizer Corporate Bond", "type": "bond", "maturity": "2033-03-15", "currency": "USD"}
    }

    def __init__(self):
        self.server = Server("wealth-management-mcp-server")
        self.clients_data = self._generate_sample_clients()
        self.positions_data = self._generate_sample_positions()
        
        # Register tools
        self._register_tools()
        
        # Set up request handlers
        self._setup_handlers()


    def _generate_sample_clients(self) -> List[Dict[str, Any]]:
        """Generate sample client data for testing"""
        clients = []
        
        # Sample client names - famous Polish people
        sample_names = [
            "Maria Sklodowska-Curie", "Lech Wałęsa", "Fryderyk Chopin", "Nicolaus Copernicus",
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


    def _generate_sample_positions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate sample position data for all clients"""
        positions = {}
        
        # Sample securities with ISINs
        equities = [
            {"name": "Apple Inc.", "isin": "US0378331005", "sector": "Technology"},
            {"name": "Microsoft Corp.", "isin": "US5949181045", "sector": "Technology"},
            {"name": "Amazon.com Inc.", "isin": "US0231351067", "sector": "Consumer Discretionary"},
            {"name": "Alphabet Inc.", "isin": "US02079K3059", "sector": "Technology"},
            {"name": "Tesla Inc.", "isin": "US88160R1014", "sector": "Consumer Discretionary"},
            {"name": "Meta Platforms Inc.", "isin": "US30303M1027", "sector": "Technology"},
            {"name": "NVIDIA Corp.", "isin": "US67066G1040", "sector": "Technology"},
            {"name": "JPMorgan Chase & Co.", "isin": "US46625H1005", "sector": "Financials"},
            {"name": "Johnson & Johnson", "isin": "US4781601046", "sector": "Healthcare"},
            {"name": "Procter & Gamble Co.", "isin": "US7427181091", "sector": "Consumer Staples"}
        ]
        
        bonds = [
            {"name": "US Treasury 10Y", "isin": "US912810TM37", "type": "Government"},
            {"name": "US Treasury 30Y", "isin": "US912810TK92", "type": "Government"},
            {"name": "iShares 20+ Year Treasury Bond ETF", "isin": "US4642876555", "type": "ETF"},
            {"name": "Corporate Bond AAA", "isin": "US037833100", "type": "Corporate"},
            {"name": "Municipal Bond Fund", "isin": "US65339F1012", "type": "Municipal"},
            {"name": "High Yield Corporate Bond", "isin": "US4642874477", "type": "Corporate"},
            {"name": "International Bond Fund", "isin": "US9229085538", "type": "International"},
            {"name": "Inflation Protected Securities", "isin": "US4642875433", "type": "TIPS"}
        ]
        
        # Generate positions for each client
        for client in self.clients_data:
            client_id = client["client_id"]
            client_positions = []
            
            # Determine number of positions based on AUM
            if client["total_aum"] > 10000000:  # High AUM clients
                num_positions = random.randint(7, 10)
            elif client["total_aum"] > 1000000:  # Medium AUM clients
                num_positions = random.randint(5, 8)
            else:  # Lower AUM clients
                num_positions = random.randint(3, 6)
            
            total_allocated = 0
            
            # Add equity positions (40-70% of portfolio)
            equity_allocation = random.uniform(0.4, 0.7)
            num_equities = min(random.randint(2, 5), len(equities))
            selected_equities = random.sample(equities, num_equities)
            
            for i, equity in enumerate(selected_equities):
                if i == len(selected_equities) - 1:  # Last equity gets remaining allocation
                    position_weight = equity_allocation - sum(pos["weight"] for pos in client_positions if pos["asset_type"] == "equity")
                else:
                    position_weight = equity_allocation / num_equities * random.uniform(0.7, 1.3)
                
                position_value = client["total_aum"] * position_weight
                share_price = random.uniform(50, 500)
                shares = int(position_value / share_price)
                actual_value = shares * share_price
                
                client_positions.append({
                    "position_id": f"POS-{client_id}-{len(client_positions)+1:03d}",
                    "asset_type": "equity",
                    "name": equity["name"],
                    "isin": equity["isin"],
                    "sector": equity["sector"],
                    "shares": shares,
                    "price_per_share": round(share_price, 2),
                    "market_value": round(actual_value, 2),
                    "weight": round(actual_value / client["total_aum"], 4),
                    "currency": "USD"
                })
                total_allocated += actual_value
            
            # Add bond positions (20-40% of portfolio)
            bond_allocation = random.uniform(0.2, 0.4)
            num_bonds = min(random.randint(1, 3), len(bonds))
            selected_bonds = random.sample(bonds, num_bonds)
            
            for i, bond in enumerate(selected_bonds):
                if i == len(selected_bonds) - 1:  # Last bond gets remaining allocation
                    position_weight = bond_allocation - sum(pos["weight"] for pos in client_positions if pos["asset_type"] == "bond")
                else:
                    position_weight = bond_allocation / num_bonds * random.uniform(0.8, 1.2)
                
                position_value = client["total_aum"] * position_weight
                bond_price = random.uniform(95, 105)  # Bond price as percentage of par
                nominal_value = position_value / (bond_price / 100)
                actual_value = nominal_value * (bond_price / 100)
                
                client_positions.append({
                    "position_id": f"POS-{client_id}-{len(client_positions)+1:03d}",
                    "asset_type": "bond",
                    "name": bond["name"],
                    "isin": bond["isin"],
                    "type": bond["type"],
                    "nominal_value": round(nominal_value, 2),
                    "price_percentage": round(bond_price, 2),
                    "market_value": round(actual_value, 2),
                    "weight": round(actual_value / client["total_aum"], 4),
                    "currency": "USD",
                    "coupon_rate": round(random.uniform(2.0, 6.0), 2),
                    "maturity_date": (datetime.now() + timedelta(days=random.randint(365, 3650))).strftime("%Y-%m-%d")
                })
                total_allocated += actual_value
            
            # Add cash position (remaining allocation)
            cash_value = client["total_aum"] - total_allocated
            if cash_value > 0:
                client_positions.append({
                    "position_id": f"POS-{client_id}-{len(client_positions)+1:03d}",
                    "asset_type": "cash",
                    "name": "Cash Position",
                    "isin": None,
                    "amount": round(cash_value, 2),
                    "weight": round(cash_value / client["total_aum"], 4),
                    "currency": "USD",
                    "account_type": "Money Market"
                })
            
            positions[client_id] = client_positions
        
        return positions


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
                ),
                Tool(
                    name="get_client_positions",
                    description="Retrieve detailed position information for a specific client. Returns equities, bonds, and cash positions with valuations, weights, and metadata.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "client_id": {
                                "type": "string",
                                "description": "Client identifier in format BZ-xxxxx",
                                "pattern": "^BZ-[0-9]{5}$"
                            },
                            "asset_type": {
                                "type": "string",
                                "description": "Filter by asset type (optional)",
                                "enum": ["equity", "bond", "cash", "all"]
                            },
                            "min_weight": {
                                "type": "number",
                                "description": "Minimum position weight threshold (optional)",
                                "minimum": 0,
                                "maximum": 1
                            }
                        },
                        "required": ["client_id"]
                    }
                ),
                Tool(
                    name="get_recommendations", 
                    description="Get investment recommendations (BUY/SELL/NEUTRAL) for specific ISINs or all available securities. Provides analyst ratings, target prices, and rationale.",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "isins": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of ISINs to get recommendations for. If empty, returns all available recommendations."
                            },
                            "rating_filter": {
                                "type": "string",
                                "enum": ["BUY", "SELL", "NEUTRAL", "all"],
                                "description": "Filter recommendations by rating (optional)"
                            },
                            "asset_type": {
                                "type": "string", 
                                "enum": ["equity", "bond", "all"],
                                "description": "Filter by asset type (optional)"
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
            elif name == "get_client_positions":
                return await self._get_client_positions(arguments)
            elif name == "get_recommendations":
                return await self._get_recommendations(arguments)
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


    async def _get_client_positions(self, arguments: dict) -> list[TextContent]:
        """Handle get_client_positions tool calls"""
        try:
            client_id = arguments.get("client_id")
            asset_type = arguments.get("asset_type", "all")
            min_weight = arguments.get("min_weight", 0)
            
            if not client_id:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": "client_id is required"
                    })
                )]
            
            # Validate client exists
            client = next((c for c in self.clients_data if c["client_id"] == client_id), None)
            if not client:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Client {client_id} not found"
                    })
                )]
            
            # Get positions for client
            positions = self.positions_data.get(client_id, [])
            
            # Filter by asset type
            if asset_type != "all":
                positions = [pos for pos in positions if pos["asset_type"] == asset_type]
            
            # Filter by minimum weight
            if min_weight > 0:
                positions = [pos for pos in positions if pos["weight"] >= min_weight]
            
            # Calculate summary statistics
            total_value = sum(pos.get("market_value", pos.get("amount", 0)) for pos in positions)
            equity_count = len([pos for pos in positions if pos["asset_type"] == "equity"])
            bond_count = len([pos for pos in positions if pos["asset_type"] == "bond"])
            cash_count = len([pos for pos in positions if pos["asset_type"] == "cash"])
            
            # Prepare response
            response = {
                "status": "success",
                "client_id": client_id,
                "client_name": client["name"],
                "total_aum": client["total_aum"],
                "positions_summary": {
                    "total_positions": len(positions),
                    "total_value": round(total_value, 2),
                    "equity_positions": equity_count,
                    "bond_positions": bond_count,
                    "cash_positions": cash_count
                },
                "filters_applied": {
                    "asset_type": asset_type,
                    "min_weight": min_weight
                },
                "positions": positions
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(response, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error in get_client_positions: {str(e)}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Error retrieving client positions: {str(e)}"
                })
            )]



    async def _get_recommendations(self, arguments: dict) -> list[TextContent]:
        logger.info("Serving recommendations request with arguments: %s", arguments)

        """Handle get_recommendations tool calls"""
        try:
            isins = arguments.get("isins", []) if arguments else []
            rating_filter = arguments.get("rating_filter", "all") if arguments else "all" 
            asset_type = arguments.get("asset_type", "all") if arguments else "all"
            
            recommendations = []
            
            # If no specific ISINs requested, get all available recommendations
            if not isins:
                isins = list(self.RECOMMENDATIONS_DATABASE.keys())
            
            for isin in isins:
                if isin not in self.RECOMMENDATIONS_DATABASE:
                    continue
                    
                recommendation = self.RECOMMENDATIONS_DATABASE[isin].copy()
                security_info = self.SECURITIES_DATABASE.get(isin, {})
                
                # Apply asset type filter
                if asset_type != "all" and security_info.get("type") != asset_type:
                    continue
                    
                # Apply rating filter  
                if rating_filter != "all" and recommendation["rating"] != rating_filter:
                    continue
                    
                # Enhance with security information
                recommendation["isin"] = isin
                recommendation["security_name"] = security_info.get("name", "Unknown")
                recommendation["security_type"] = security_info.get("type", "unknown")
                recommendation["sector"] = security_info.get("sector", "N/A")
                
                recommendations.append(recommendation)
            
            # Sort by rating priority (BUY > NEUTRAL > SELL) then by last_updated
            rating_priority = {"BUY": 3, "NEUTRAL": 2, "SELL": 1}
            recommendations.sort(key=lambda x: (rating_priority.get(x["rating"], 0), x["last_updated"]), reverse=True)
            
            # Calculate summary statistics
            rating_counts = {"BUY": 0, "SELL": 0, "NEUTRAL": 0}
            for rec in recommendations:
                rating_counts[rec["rating"]] += 1
                
            response = {
                "recommendations": recommendations,
                "summary": {
                    "total_recommendations": len(recommendations), 
                    "rating_breakdown": rating_counts,
                    "filters_applied": {
                        "specific_isins": len(arguments.get("isins", [])) > 0 if arguments else False,
                        "rating_filter": rating_filter,
                        "asset_type": asset_type
                    }
                },
                "metadata": {
                    "timestamp": "2025-07-19T10:30:00Z",
                    "research_teams": ["Tech Research Team", "Fixed Income Team", "Credit Research Team", 
                                    "Auto Research Team", "Financial Services Team", "AI Research Team",
                                    "Consumer Research Team", "Semiconductor Team", "Media Research Team", 
                                    "Healthcare Team"]
                }
            }
            
            return [TextContent(type="text", text=json.dumps(response, indent=2))]

                        
        except Exception as e:
            logger.error(f"Error in get_recommendations: {str(e)}")
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "message": f"Error retrieving recommendations: {str(e)}"
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
        logger.info(f"Generated positions for {len(self.clients_data)} clients")
        
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
