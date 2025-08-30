#!/usr/bin/env python3
"""
Wealth Management MCP Server - Phase 4: Integration & Advanced Queries
Complete implementation with cross-tool functionality, error handling, and validation
"""

import asyncio
import json
import logging
import random
import re
import sys
from datetime import datetime, timedelta
from typing import Any, Sequence, Dict, List, Optional, Set, Tuple
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)
from mcp.server.stdio import stdio_server
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wealth-management-mcp-server")


class WealthManagementServer:

    # Cache for client positions to ensure consistency
    CLIENT_POSITIONS_CACHE = {}

    def __init__(self):
        self.server = Server("wealth-management-mcp-server")
        self._register_tools()
        
    def generate_client_positions(self, client_id: str) -> List[Dict[str, Any]]:
        """Generate realistic portfolio positions for a client based on their risk profile"""
        client = next((c for c in SAMPLE_CLIENTS if c["client_id"] == client_id), None)
        if not client:
            return []
        
        positions = []
        risk_profile = client["risk_profile"]
        total_aum = client["total_aum"]
        
        # Get available securities
        equities = [isin for isin, data in SECURITIES_DATABASE.items() if data["type"] == "equity"]
        bonds = [isin for isin, data in SECURITIES_DATABASE.items() if data["type"] == "bond"]
        
        # Risk-based allocation
        if risk_profile == "Conservative":
            cash_pct = random.uniform(0.15, 0.25)  # 15-25% cash
            bond_pct = random.uniform(0.50, 0.65)  # 50-65% bonds
            equity_pct = 1 - cash_pct - bond_pct   # Remainder in equities
            num_equities = random.randint(2, 4)
            num_bonds = random.randint(3, 6)
        elif risk_profile == "Moderate":
            cash_pct = random.uniform(0.05, 0.15)  # 5-15% cash
            bond_pct = random.uniform(0.30, 0.45)  # 30-45% bonds
            equity_pct = 1 - cash_pct - bond_pct   # Remainder in equities
            num_equities = random.randint(4, 7)
            num_bonds = random.randint(2, 4)
        else:  # Aggressive
            cash_pct = random.uniform(0.02, 0.08)  # 2-8% cash
            bond_pct = random.uniform(0.10, 0.25)  # 10-25% bonds
            equity_pct = 1 - cash_pct - bond_pct   # Remainder in equities
            num_equities = random.randint(6, 10)
            num_bonds = random.randint(1, 3)
        
        # Add cash position
        cash_amount = total_aum * cash_pct
        positions.append({
            "type": "cash",
            "currency": "USD",
            "amount": round(cash_amount, 2),
            "weight": round(cash_pct * 100, 2)
        })
        
        # Add equity positions
        selected_equities = random.sample(equities, min(num_equities, len(equities)))
        equity_allocation = total_aum * equity_pct
        
        for i, isin in enumerate(selected_equities):
            # Distribute equity allocation across positions
            if i == len(selected_equities) - 1:  # Last position gets remainder
                position_value = equity_allocation
            else:
                position_value = equity_allocation * random.uniform(0.8, 1.2) / len(selected_equities)
                equity_allocation -= position_value
            
            # Calculate shares and price
            base_price = random.uniform(50, 400)
            shares = int(position_value / base_price)
            actual_value = shares * base_price
            
            positions.append({
                "type": "equity",
                "isin": isin,
                "name": SECURITIES_DATABASE[isin]["name"],
                "shares": shares,
                "price": round(base_price, 2),
                "valuation": round(actual_value, 2),
                "weight": round((actual_value / total_aum) * 100, 2),
                "sector": SECURITIES_DATABASE[isin]["sector"]
            })
        
        # Add bond positions
        selected_bonds = random.sample(bonds, min(num_bonds, len(bonds)))
        bond_allocation = total_aum * bond_pct
        
        for i, isin in enumerate(selected_bonds):
            # Distribute bond allocation
            if i == len(selected_bonds) - 1:  # Last position gets remainder
                position_value = bond_allocation
            else:
                position_value = bond_allocation * random.uniform(0.8, 1.2) / len(selected_bonds)
                bond_allocation -= position_value
                
            nominal = int(position_value / 100) * 100  # Round to nearest $100
            price_percent = random.uniform(98, 104)
            actual_value = nominal * (price_percent / 100)
            
            positions.append({
                "type": "bond",
                "isin": isin,
                "name": SECURITIES_DATABASE[isin]["name"],
                "nominal": nominal,
                "price_percent": round(price_percent, 2),
                "valuation": round(actual_value, 2),
                "weight": round((actual_value / total_aum) * 100, 2),
                "maturity": SECURITIES_DATABASE[isin]["maturity"],
                "rating": SECURITIES_DATABASE[isin]["rating"]
            })
        
        return positions

    def get_client_positions(self, client_id: str) -> List[Dict[str, Any]]:
        """Get or generate client positions"""
        if client_id not in self.CLIENT_POSITIONS_CACHE:
            self.CLIENT_POSITIONS_CACHE[client_id] = self.generate_client_positions(client_id)
        return self.CLIENT_POSITIONS_CACHE[client_id]

    def validate_client_id(self, client_id: str) -> bool:
        """Validate client ID format"""
        pattern = r'^BZ-\d{5}$'
        return bool(re.match(pattern, client_id))

    def get_clients_with_sell_rated_positions(self) -> List[Dict[str, Any]]:
        """Advanced query: Find clients with SELL-rated positions"""
        results = []
        
        for client in SAMPLE_CLIENTS:
            client_id = client["client_id"]
            positions = self.get_client_positions(client_id)
            
            sell_positions = []
            for position in positions:
                if position["type"] in ["equity", "bond"] and "isin" in position:
                    isin = position["isin"]
                    if isin in RECOMMENDATIONS_DATABASE:
                        recommendation = RECOMMENDATIONS_DATABASE[isin]
                        if recommendation["rating"] == "SELL":
                            sell_positions.append({
                                "isin": isin,
                                "name": position["name"],
                                "type": position["type"],
                                "weight": position["weight"],
                                "valuation": position["valuation"],
                                "recommendation": recommendation
                            })
            
            if sell_positions:
                total_sell_exposure = sum(pos["valuation"] for pos in sell_positions)
                results.append({
                    "client": client,
                    "sell_positions": sell_positions,
                    "total_sell_exposure": round(total_sell_exposure, 2),
                    "sell_exposure_percentage": round((total_sell_exposure / client["total_aum"]) * 100, 2)
                })
        
        return results

    def get_clients_by_cash_threshold(self, threshold_pct: float) -> List[Dict[str, Any]]:
        """Advanced query: Find clients with cash above threshold"""
        results = []
        
        for client in SAMPLE_CLIENTS:
            client_id = client["client_id"]
            positions = self.get_client_positions(client_id)
            
            cash_positions = [pos for pos in positions if pos["type"] == "cash"]
            total_cash = sum(pos["amount"] for pos in cash_positions)
            cash_percentage = (total_cash / client["total_aum"]) * 100
            
            if cash_percentage > threshold_pct:
                results.append({
                    "client": client,
                    "cash_amount": round(total_cash, 2),
                    "cash_percentage": round(cash_percentage, 2),
                    "excess_cash": round(total_cash - (client["total_aum"] * threshold_pct / 100), 2)
                })
        
        return results

    def get_clients_holding_security(self, isin: str) -> List[Dict[str, Any]]:
        """Advanced query: Find clients holding specific security"""
        results = []
        
        for client in SAMPLE_CLIENTS:
            client_id = client["client_id"]
            positions = self.get_client_positions(client_id)
            
            matching_positions = [pos for pos in positions if pos.get("isin") == isin]
            
            if matching_positions:
                for position in matching_positions:
                    recommendation = RECOMMENDATIONS_DATABASE.get(isin, {})
                    results.append({
                        "client": client,
                        "position": position,
                        "recommendation": recommendation,
                        "exposure_percentage": position["weight"]
                    })
        
        return results

    def get_clients_by_asset_type(self, asset_type: str, exclude: bool = False) -> List[Dict[str, Any]]:
        """Advanced query: Find clients with/without specific asset types"""
        results = []
        
        for client in SAMPLE_CLIENTS:
            client_id = client["client_id"]
            positions = get_client_positions(client_id)
            
            has_asset_type = any(pos["type"] == asset_type for pos in positions)
            
            if (has_asset_type and not exclude) or (not has_asset_type and exclude):
                asset_positions = [pos for pos in positions if pos["type"] == asset_type]
                total_exposure = sum(pos.get("valuation", pos.get("amount", 0)) for pos in asset_positions)
                
                results.append({
                    "client": client,
                    "has_asset_type": has_asset_type,
                    "positions": asset_positions,
                    "total_exposure": round(total_exposure, 2),
                    "exposure_percentage": round((total_exposure / client["total_aum"]) * 100, 2) if total_exposure > 0 else 0
                })
        
        return results

    def _register_tools(self):

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List all available wealth management tools"""
            return [
                Tool(
                    name="get_clients",
                    description="Retrieve list of all clients managed by the advisor. Returns comprehensive client information including IDs, names, risk profiles, and AUM.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filter_by": {
                                "type": "string",
                                "enum": ["active", "under_review", "high_aum", "new_clients", "all"],
                                "description": "Optional filter criteria: 'active', 'under_review', 'high_aum' (>10M), 'new_clients' (last 90 days)"
                            },
                            "sort_by": {
                                "type": "string", 
                                "enum": ["name", "client_id", "total_aum", "onboarding_date", "last_review"],
                                "description": "Sort criteria for client list"
                            },
                            "limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "description": "Maximum number of clients to return (default: all)"
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
                                "pattern": "^BZ-[0-9]{5}$",
                                "description": "Client identifier in format BZ-xxxxx"
                            },
                            "asset_type": {
                                "type": "string",
                                "enum": ["equity", "bond", "cash", "all"],
                                "description": "Filter by asset type (optional)"
                            },
                            "min_weight": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "Minimum position weight threshold (optional)"
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
        async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
            """Handle tool calls with enhanced error handling and validation"""
            
            try:
                if name == "get_clients":
                    # Enhanced client retrieval with better filtering
                    filter_by = arguments.get("filter_by", "all") if arguments else "all"
                    sort_by = arguments.get("sort_by", "name") if arguments else "name"  
                    limit = arguments.get("limit") if arguments else None
                    
                    clients = SAMPLE_CLIENTS.copy()
                    
                    # Apply filters
                    if filter_by == "high_aum":
                        clients = [c for c in clients if c["total_aum"] > 10000000]
                    elif filter_by == "under_review":
                        clients = [c for c in clients if c["status"] == "under_review"]
                    elif filter_by == "active":
                        clients = [c for c in clients if c["status"] == "active"]
                    elif filter_by == "new_clients":
                        # Clients onboarded in last 90 days
                        cutoff_date = datetime.now() - timedelta(days=90)
                        clients = [c for c in clients if datetime.strptime(c["onboarding_date"], "%Y-%m-%d") > cutoff_date]
                        
                    # Apply sorting
                    if sort_by == "total_aum":
                        clients.sort(key=lambda x: x["total_aum"], reverse=True)
                    elif sort_by == "name":
                        clients.sort(key=lambda x: x["name"])
                    elif sort_by == "onboarding_date":
                        clients.sort(key=lambda x: x["onboarding_date"], reverse=True)
                    elif sort_by == "last_review":
                        clients.sort(key=lambda x: x["last_review"], reverse=True)
                        
                    # Apply limit
                    if limit and limit > 0:
                        clients = clients[:limit]
                        
                    # Enhanced response with analytics
                    total_aum = sum(c["total_aum"] for c in clients)
                    risk_breakdown = {}
                    for client in clients:
                        risk = client["risk_profile"]
                        if risk not in risk_breakdown:
                            risk_breakdown[risk] = {"count": 0, "total_aum": 0}
                        risk_breakdown[risk]["count"] += 1
                        risk_breakdown[risk]["total_aum"] += client["total_aum"]
                    
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "clients": clients,
                            "summary": {
                                "total_count": len(clients),
                                "total_aum": round(total_aum, 2),
                                "average_aum": round(total_aum / len(clients), 2) if clients else 0,
                                "risk_profile_breakdown": risk_breakdown
                            },
                            "metadata": {
                                "filter_applied": filter_by,
                                "sort_by": sort_by,
                                "timestamp": datetime.now().isoformat(),
                                "query_performance": "optimized"
                            }
                        }, indent=2)
                    )]
                
                elif name == "get_client_positions":
                    # Enhanced position retrieval with validation
                    if not arguments or "client_id" not in arguments:
                        return [types.TextContent(type="text", text=json.dumps({
                            "error": "client_id is required",
                            "error_code": "MISSING_PARAMETER"
                        }, indent=2))]
                        
                    client_id = arguments["client_id"]
                    
                    # Validate client ID format
                    if not self.validate_client_id(client_id):
                        return [types.TextContent(type="text", text=json.dumps({
                            "error": f"Invalid client_id format: {client_id}. Expected format: BZ-XXXXX",
                            "error_code": "INVALID_FORMAT"
                        }, indent=2))]
                    
                    asset_type = arguments.get("asset_type", "all")
                    min_weight = arguments.get("min_weight", 0)
                    
                    # Validate client exists
                    client = next((c for c in SAMPLE_CLIENTS if c["client_id"] == client_id), None)
                    if not client:
                        return [types.TextContent(type="text", text=json.dumps({
                            "error": f"Client {client_id} not found",
                            "error_code": "CLIENT_NOT_FOUND",
                            "available_clients": [c["client_id"] for c in SAMPLE_CLIENTS[:5]]  # Show first 5 as examples
                        }, indent=2))]
                    
                    # Get positions
                    positions = self.get_client_positions(client_id)
                    
                    # Apply filters
                    if asset_type != "all":
                        positions = [p for p in positions if p["type"] == asset_type]
                        
                    if min_weight > 0:
                        positions = [p for p in positions if p["weight"] >= min_weight * 100]
                        
                    # Calculate enhanced summary
                    total_value = sum(pos["valuation"] if "valuation" in pos else pos["amount"] for pos in positions)
                    
                    # Asset breakdown with recommendations
                    asset_breakdown = {}
                    recommendation_summary = {"BUY": 0, "SELL": 0, "NEUTRAL": 0, "NO_RATING": 0}
                    
                    for pos in positions:
                        asset_type_key = pos["type"]
                        value = pos["valuation"] if "valuation" in pos else pos["amount"]
                        
                        if asset_type_key not in asset_breakdown:
                            asset_breakdown[asset_type_key] = {"count": 0, "total_value": 0, "percentage": 0}
                        asset_breakdown[asset_type_key]["count"] += 1
                        asset_breakdown[asset_type_key]["total_value"] += value
                        
                        # Add recommendation info for securities
                        if "isin" in pos:
                            isin = pos["isin"]
                            if isin in RECOMMENDATIONS_DATABASE:
                                rating = RECOMMENDATIONS_DATABASE[isin]["rating"]
                                pos["recommendation"] = RECOMMENDATIONS_DATABASE[isin]
                                recommendation_summary[rating] += 1
                            else:
                                recommendation_summary["NO_RATING"] += 1
                    
                    # Calculate percentages
                    for asset_type_key, data in asset_breakdown.items():
                        data["total_value"] = round(data["total_value"], 2)
                        data["percentage"] = round((data["total_value"] / total_value) * 100, 2)
                    
                    response = {
                        "client_id": client_id,
                        "client_name": client["name"],
                        "client_info": {
                            "risk_profile": client["risk_profile"],
                            "total_aum": client["total_aum"],
                            "last_review": client["last_review"],
                            "status": client["status"]
                        },
                        "positions": positions,
                        "summary": {
                            "total_positions": len(positions),
                            "total_value": round(total_value, 2),
                            "asset_breakdown": asset_breakdown,
                            "recommendation_summary": recommendation_summary,
                            "alignment_with_risk_profile": self._assess_risk_alignment(client, positions)
                        },
                        "metadata": {
                            "timestamp": datetime.now().isoformat(),
                            "filters_applied": {
                                "asset_type": asset_type,
                                "min_weight": min_weight
                            },
                            "data_quality": "validated"
                        }
                    }
                    
                    return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
                
                elif name == "get_recommendations":
                    # Enhanced recommendation retrieval
                    isins = arguments.get("isins", []) if arguments else []
                    rating_filter = arguments.get("rating_filter", "all") if arguments else "all" 
                    asset_type = arguments.get("asset_type", "all") if arguments else "all"
                    
                    recommendations = []
                    
                    # If no specific ISINs requested, get all available recommendations
                    target_isins = isins if isins else list(RECOMMENDATIONS_DATABASE.keys())
                    
                    for isin in target_isins:
                        if isin not in RECOMMENDATIONS_DATABASE:
                            continue
                            
                        recommendation = RECOMMENDATIONS_DATABASE[isin].copy()
                        security_info = SECURITIES_DATABASE.get(isin, {})
                        
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
                        
                        # Add performance metrics
                        current_price = recommendation.get("current_price", 0)
                        target_price = recommendation.get("target_price", 0)
                        if current_price > 0 and target_price > 0:
                            recommendation["upside_potential"] = round(((target_price - current_price) / current_price) * 100, 2)
                        
                        recommendations.append(recommendation)
                    
                    # Sort by rating priority (BUY > NEUTRAL > SELL) then by upside potential
                    rating_priority = {"BUY": 3, "NEUTRAL": 2, "SELL": 1}
                    recommendations.sort(
                        key=lambda x: (
                            rating_priority.get(x["rating"], 0), 
                            x.get("upside_potential", 0)
                        ), 
                        reverse=True
                    )
                    
                    # Calculate enhanced summary statistics
                    rating_counts = {"BUY": 0, "SELL": 0, "NEUTRAL": 0}
                    sector_breakdown = {}
                    avg_upside = 0
                    upside_count = 0
                    
                    for rec in recommendations:
                        rating_counts[rec["rating"]] += 1
                        
                        sector = rec.get("sector", "Unknown")
                        if sector not in sector_breakdown:
                            sector_breakdown[sector] = {"BUY": 0, "SELL": 0, "NEUTRAL": 0}
                        sector_breakdown[sector][rec["rating"]] += 1
                        
                        if "upside_potential" in rec:
                            avg_upside += rec["upside_potential"]
                            upside_count += 1
                    
                    if upside_count > 0:
                        avg_upside = round(avg_upside / upside_count, 2)
                    
                    response = {
                        "recommendations": recommendations,
                        "summary": {
                            "total_recommendations": len(recommendations), 
                            "rating_breakdown": rating_counts,
                            "sector_breakdown": sector_breakdown,
                            "avg_upside_potential": avg_upside,
                            "filters_applied": {
                                "specific_isins": len(arguments.get("isins", [])) > 0 if arguments else False,
                                "rating_filter": rating_filter,
                                "asset_type": asset_type
                            }
                        },
                        "metadata": {
                            "timestamp": datetime.now().isoformat(),
                            "research_coverage": len(RECOMMENDATIONS_DATABASE),
                            "data_freshness": "daily_updates"
                        }
                    }
                    
                    return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
                
                else:
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "error": f"Unknown tool: {name}",
                            "error_code": "TOOL_NOT_FOUND",
                            "available_tools": ["get_clients", "get_client_positions", "get_recommendations"]
                        }, indent=2)
                    )]
                    
            except Exception as e:
                # Comprehensive error handling
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Internal server error: {str(e)}",
                        "error_code": "INTERNAL_ERROR",
                        "timestamp": datetime.now().isoformat(),
                        "tool_name": name,
                        "arguments": arguments
                    }, indent=2)
                )]


    def _assess_risk_alignment(self, client: Dict[str, Any], positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess how well the portfolio aligns with client risk profile"""
        risk_profile = client["risk_profile"]
        
        # Calculate asset allocation
        total_value = sum(pos["valuation"] if "valuation" in pos else pos["amount"] for pos in positions)
        cash_pct = sum(pos["amount"] for pos in positions if pos["type"] == "cash") / total_value * 100
        equity_pct = sum(pos["valuation"] for pos in positions if pos["type"] == "equity") / total_value * 100
        bond_pct = sum(pos["valuation"] for pos in positions if pos["type"] == "bond") / total_value * 100
        
        # Define target allocations by risk profile
        targets = {
            "Conservative": {"cash": (15, 25), "bonds": (50, 65), "equities": (15, 30)},
            "Moderate": {"cash": (5, 15), "bonds": (30, 45), "equities": (40, 65)},
            "Aggressive": {"cash": (2, 8), "bonds": (10, 25), "equities": (65, 85)}
        }
        
        target = targets.get(risk_profile, targets["Moderate"])
        
        # Check alignment
        alignment_score = 0
        issues = []
        
        if target["cash"][0] <= cash_pct <= target["cash"][1]:
            alignment_score += 33
        else:
            issues.append(f"Cash allocation {cash_pct:.1f}% outside target range {target['cash'][0]}-{target['cash'][1]}%")
        
        if target["bonds"][0] <= bond_pct <= target["bonds"][1]:
            alignment_score += 33
        else:
            issues.append(f"Bond allocation {bond_pct:.1f}% outside target range {target['bonds'][0]}-{target['bonds'][1]}%")
        
        if target["equities"][0] <= equity_pct <= target["equities"][1]:
            alignment_score += 34
        else:
            issues.append(f"Equity allocation {equity_pct:.1f}% outside target range {target['equities'][0]}-{target['equities'][1]}%")
        
        return {
            "alignment_score": alignment_score,
            "current_allocation": {
                "cash": round(cash_pct, 1),
                "bonds": round(bond_pct, 1),
                "equities": round(equity_pct, 1)
            },
            "target_allocation": target,
            "issues": issues,
            "recommendation": "ALIGNED" if alignment_score >= 80 else "NEEDS_REBALANCING" if alignment_score >= 50 else "MAJOR_MISALIGNMENT"
        }


    async def run(self):
        logger.info("Starting Wealth Management MCP Server")
        try:
            # Use stdio transport for MCP communication
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="wealth-management-mcp-server",
                        server_version="2.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities=dict(),
                        ),
                    ),
                )
        except Exception as e:
            print(f"Server error: {e}", file=sys.stderr)
            raise


async def main():
    server = WealthManagementServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())


# Enhanced client data with more realistic attributes
SAMPLE_CLIENTS = [
    {
        "client_id": "BZ-00001", "name": "Maria Sklodowska-Curie", "risk_profile": "Conservative", 
        "total_aum": 2500000, "onboarding_date": "2023-03-15", "last_review": "2025-06-10",
        "status": "active", "advisor_notes": "Prefers stable, dividend-paying securities"
    },
    {
        "client_id": "BZ-00002", "name": "Lech Wałęsa", "risk_profile": "Moderate", 
        "total_aum": 1800000, "onboarding_date": "2024-01-20", "last_review": "2025-07-05",
        "status": "active", "advisor_notes": "Interested in ESG investing"
    },
    {
        "client_id": "BZ-00003", "name": "Fryderyk Chopin", "risk_profile": "Aggressive", 
        "total_aum": 5200000, "onboarding_date": "2022-11-08", "last_review": "2025-07-15",
        "status": "active", "advisor_notes": "Tech sector focus, high risk tolerance"
    },
    {
        "client_id": "BZ-00004", "name": "Nicolaus Copernicus", "risk_profile": "Conservative", 
        "total_aum": 950000, "onboarding_date": "2024-05-12", "last_review": "2025-05-20",
        "status": "under_review", "advisor_notes": "Retirement planning focus"
    },
    {
        "client_id": "BZ-00005", "name": "Andrzej Wajda", "risk_profile": "Moderate", 
        "total_aum": 3100000, "onboarding_date": "2023-09-03", "last_review": "2025-07-08",
        "status": "active", "advisor_notes": "Balanced approach, quarterly rebalancing"
    },
    {
        "client_id": "BZ-00006", "name": "Wisława Szymborska", "risk_profile": "Aggressive", 
        "total_aum": 4750000, "onboarding_date": "2024-02-28", "last_review": "2025-06-25",
        "status": "active", "advisor_notes": "Growth stocks and emerging markets"
    },
    {
        "client_id": "BZ-00007", "name": "Krzysztof Kieślowski", "risk_profile": "Conservative", 
        "total_aum": 1200000, "onboarding_date": "2023-07-19", "last_review": "2025-04-18",
        "status": "active", "advisor_notes": "Fixed income preference"
    },
    {
        "client_id": "BZ-00008", "name": "Stanisław Lem", "risk_profile": "Moderate", 
        "total_aum": 2800000, "onboarding_date": "2024-04-05", "last_review": "2025-07-12",
        "status": "active", "advisor_notes": "Education funding goals"
    },
    {
        "client_id": "BZ-00009", "name": "Jerzy Grotowski", "risk_profile": "Aggressive", 
        "total_aum": 6100000, "onboarding_date": "2022-06-14", "last_review": "2025-07-18",
        "status": "active", "advisor_notes": "Options trading approved"
    },
    {
        "client_id": "BZ-00010", "name": "Henryk Górecki", "risk_profile": "Conservative", 
        "total_aum": 1450000, "onboarding_date": "2024-06-01", "last_review": "2025-06-30",
        "status": "active", "advisor_notes": "Capital preservation priority"
    }
]

# Enhanced securities database with more metadata
SECURITIES_DATABASE = {
    # Technology Equities
    "US0378331005": {"name": "Apple Inc.", "type": "equity", "sector": "Technology", "currency": "USD", "exchange": "NASDAQ", "market_cap": "large"},
    "US5949181045": {"name": "Microsoft Corp.", "type": "equity", "sector": "Technology", "currency": "USD", "exchange": "NASDAQ", "market_cap": "large"},
    "US02079K3059": {"name": "Alphabet Inc.", "type": "equity", "sector": "Technology", "currency": "USD", "exchange": "NASDAQ", "market_cap": "large"},
    "US0231351067": {"name": "Amazon.com Inc.", "type": "equity", "sector": "Consumer Discretionary", "currency": "USD", "exchange": "NASDAQ", "market_cap": "large"},
    "US88160R1014": {"name": "Tesla Inc.", "type": "equity", "sector": "Consumer Discretionary", "currency": "USD", "exchange": "NASDAQ", "market_cap": "large"},
    "US17275R1023": {"name": "Cisco Systems Inc.", "type": "equity", "sector": "Technology", "currency": "USD", "exchange": "NASDAQ", "market_cap": "large"},
    "US4592001014": {"name": "Intel Corp.", "type": "equity", "sector": "Technology", "currency": "USD", "exchange": "NASDAQ", "market_cap": "large"},
    "US67066G1040": {"name": "NVIDIA Corp.", "type": "equity", "sector": "Technology", "currency": "USD", "exchange": "NASDAQ", "market_cap": "large"},
    "US30303M1027": {"name": "Meta Platforms Inc.", "type": "equity", "sector": "Technology", "currency": "USD", "exchange": "NASDAQ", "market_cap": "large"},
    
    # Financial Services
    "US6174464486": {"name": "Morgan Stanley", "type": "equity", "sector": "Financial Services", "currency": "USD", "exchange": "NYSE", "market_cap": "large"},
    "US46625H100": {"name": "JPMorgan Chase & Co.", "type": "equity", "sector": "Financial Services", "currency": "USD", "exchange": "NYSE", "market_cap": "large"},
    
    # Government Bonds
    "US912828Z490": {"name": "US Treasury 10Y", "type": "bond", "maturity": "2034-05-15", "currency": "USD", "rating": "AAA", "yield": 4.2},
    "US9128283H60": {"name": "US Treasury 30Y", "type": "bond", "maturity": "2054-02-15", "currency": "USD", "rating": "AAA", "yield": 4.4},
    "US912828XE93": {"name": "US Treasury 5Y", "type": "bond", "maturity": "2030-01-31", "currency": "USD", "rating": "AAA", "yield": 4.0},
    
    # Corporate Bonds
    "US037833100": {"name": "Apple Inc. Corporate Bond", "type": "bond", "maturity": "2032-02-23", "currency": "USD", "rating": "AA+", "yield": 3.8},
    "US594918104": {"name": "Microsoft Corporate Bond", "type": "bond", "maturity": "2031-06-01", "currency": "USD", "rating": "AAA", "yield": 3.6},
    "US02079K305": {"name": "Alphabet Corporate Bond", "type": "bond", "maturity": "2030-08-15", "currency": "USD", "rating": "AA+", "yield": 3.7},
    "US464287200": {"name": "JPMorgan Chase Bond", "type": "bond", "maturity": "2029-04-23", "currency": "USD", "rating": "A+", "yield": 4.1},
    "US254687FX05": {"name": "Disney Corporate Bond", "type": "bond", "maturity": "2028-12-01", "currency": "USD", "rating": "A", "yield": 4.3},
    "US717081103": {"name": "Pfizer Corporate Bond", "type": "bond", "maturity": "2033-03-15", "currency": "USD", "rating": "AA", "yield": 3.9}
}

# Enhanced recommendations with more detailed analysis
RECOMMENDATIONS_DATABASE = {
    # Technology stocks
    "US0378331005": {
        "rating": "BUY", "target_price": 250.00, "current_price": 235.50, "analyst": "Tech Research Team", 
        "last_updated": "2025-07-18", "rationale": "Strong iPhone sales and AI integration driving growth",
        "risk_factors": ["Supply chain disruptions", "China market exposure"], "confidence": "High"
    },
    "US5949181045": {
        "rating": "BUY", "target_price": 480.00, "current_price": 445.25, "analyst": "Tech Research Team",
        "last_updated": "2025-07-17", "rationale": "Azure growth and AI leadership position",
        "risk_factors": ["Cloud competition", "Regulatory scrutiny"], "confidence": "High"
    },
    "US02079K3059": {
        "rating": "NEUTRAL", "target_price": 180.00, "current_price": 175.80, "analyst": "Tech Research Team",
        "last_updated": "2025-07-16", "rationale": "Search market maturity offset by AI opportunities",
        "risk_factors": ["AI competition", "Regulatory challenges"], "confidence": "Medium"
    },
    "US0231351067": {
        "rating": "BUY", "target_price": 200.00, "current_price": 185.30, "analyst": "Consumer Research Team",
        "last_updated": "2025-07-15", "rationale": "AWS growth and retail optimization initiatives",
        "risk_factors": ["E-commerce competition", "Labor costs"], "confidence": "High"
    },
    "US88160R1014": {
        "rating": "SELL", "target_price": 180.00, "current_price": 195.75, "analyst": "Auto Research Team",
        "last_updated": "2025-07-19", "rationale": "EV market competition intensifying, valuation concerns",
        "risk_factors": ["Production challenges", "Competition from legacy automakers"], "confidence": "Medium"
    },
    "US17275R1023": {
        "rating": "NEUTRAL", "target_price": 55.00, "current_price": 52.40, "analyst": "Tech Research Team",
        "last_updated": "2025-07-14", "rationale": "Steady networking demand but limited growth prospects",
        "risk_factors": ["Cloud transition", "Competition"], "confidence": "Medium"
    },
    "US4592001014": {
        "rating": "SELL", "target_price": 35.00, "current_price": 38.90, "analyst": "Semiconductor Team",
        "last_updated": "2025-07-18", "rationale": "Losing market share to AMD and ARM-based solutions",
        "risk_factors": ["Technology transition", "Competitive pressure"], "confidence": "High"
    },
    "US67066G1040": {
        "rating": "BUY", "target_price": 1200.00, "current_price": 1050.00, "analyst": "AI Research Team",
        "last_updated": "2025-07-19", "rationale": "AI chip demand continues to surge, market leadership",
        "risk_factors": ["Valuation levels", "Geopolitical tensions"], "confidence": "High"
    },
    "US30303M1027": {
        "rating": "NEUTRAL", "target_price": 550.00, "current_price": 525.60, "analyst": "Tech Research Team",
        "last_updated": "2025-07-16", "rationale": "Metaverse investments vs. core advertising business strength",
        "risk_factors": ["Ad market volatility", "Regulatory pressure"], "confidence": "Medium"
    },
    "US6174464486": {
        "rating": "BUY", "target_price": 120.00, "current_price": 108.75, "analyst": "Financial Services Team",
        "last_updated": "2025-07-17", "rationale": "Strong wealth management division and rising rates benefit",
        "risk_factors": ["Credit losses", "Market volatility"], "confidence": "High"
    },
    "US46625H100": {
        "rating": "BUY", "target_price": 190.00, "current_price": 175.20, "analyst": "Financial Services Team",
        "last_updated": "2025-07-16", "rationale": "Diversified revenue streams and strong credit quality",
        "risk_factors": ["Interest rate sensitivity", "Loan losses"], "confidence": "High"
    },
    
    # Bonds
    "US912828Z490": {
        "rating": "BUY", "target_price": 102.50, "current_price": 101.20, "analyst": "Fixed Income Team",
        "last_updated": "2025-07-18", "rationale": "Safe haven amid market volatility, attractive yield",
        "risk_factors": ["Duration risk", "Inflation expectations"], "confidence": "High"
    },
    "US9128283H60": {
        "rating": "NEUTRAL", "target_price": 98.75, "current_price": 97.90, "analyst": "Fixed Income Team",
        "last_updated": "2025-07-17", "rationale": "Duration risk vs. yield attractiveness balance",
        "risk_factors": ["Interest rate sensitivity", "Inflation"], "confidence": "Medium"
    },
    "US912828XE93": {
        "rating": "BUY", "target_price": 103.25, "current_price": 102.10, "analyst": "Fixed Income Team",
        "last_updated": "2025-07-15", "rationale": "Sweet spot for duration and yield balance",
        "risk_factors": ["Rate volatility"], "confidence": "High"
    },
    "US037833100": {
        "rating": "BUY", "target_price": 104.25, "current_price": 103.40, "analyst": "Credit Research Team",
        "last_updated": "2025-07-16", "rationale": "Strong corporate fundamentals and credit quality",
        "risk_factors": ["Credit spread widening"], "confidence": "High"
    },
    "US594918104": {
        "rating": "BUY", "target_price": 103.80, "current_price": 102.95, "analyst": "Credit Research Team",
        "last_updated": "2025-07-15", "rationale": "Excellent credit quality and attractive yield premium",
        "risk_factors": ["Corporate earnings"], "confidence": "High"
    },
    "US02079K305": {
        "rating": "NEUTRAL", "target_price": 101.20, "current_price": 100.85, "analyst": "Credit Research Team",
        "last_updated": "2025-07-14", "rationale": "Fair value at current levels, limited upside",
        "risk_factors": ["Tech sector volatility"], "confidence": "Medium"
    },
    "US464287200": {
        "rating": "BUY", "target_price": 105.10, "current_price": 104.20, "analyst": "Financial Services Team",
        "last_updated": "2025-07-13", "rationale": "Bank strength supports credit, rising rate environment positive",
        "risk_factors": ["Credit cycle"], "confidence": "High"
    },
    "US254687FX05": {
        "rating": "SELL", "target_price": 96.50, "current_price": 98.75, "analyst": "Media Research Team",
        "last_updated": "2025-07-18", "rationale": "Streaming competition pressures and cord-cutting trends",
        "risk_factors": ["Content costs", "Subscriber growth"], "confidence": "Medium"
    },
    "US717081103": {
        "rating": "NEUTRAL", "target_price": 102.00, "current_price": 101.60, "analyst": "Healthcare Team",
        "last_updated": "2025-07-17", "rationale": "Stable pharma fundamentals but limited growth catalysts",
        "risk_factors": ["Drug pricing pressure"], "confidence": "Medium"
    }
}
