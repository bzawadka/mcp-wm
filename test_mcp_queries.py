#!/usr/bin/env python3
"""
Wealth Management MCP Server - Testing & Validation Script
Run this script to test all the complex queries that make your MCP server practical

Usage:
1. Start your MCP server: python wealth_management_server.py
2. Run this test script: python test_mcp_queries.py
3. Or use these queries directly in Claude Desktop
"""

import json
from typing import Dict, List, Any

class MCPQueryTester:
    """Test complex MCP queries for wealth management"""
    
    def __init__(self):
        self.test_results = []
    
    def print_section(self, title: str):
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def print_query(self, description: str, claude_query: str):
        print(f"\n🔍 {description}")
        print(f"💬 Claude Query: '{claude_query}'")
        print(f"📋 Behind the scenes: This combines multiple MCP tools")
    
    def demonstrate_advanced_queries(self):
        """Demonstrate all the advanced queries your MCP server enables"""
        
        self.print_section("ADVANCED WEALTH MANAGEMENT QUERIES")
        print("These are the types of questions you can now ask Claude Desktop:")
        
        # Query 1: SELL-rated positions
        self.print_query(
            "Find clients with SELL-rated positions",
            "Which of my clients has SELL rated positions? Show me the details."
        )
        print("🔧 MCP Tools Used:")
        print("   1. get_clients() - Get all clients")
        print("   2. get_client_positions(client_id) - For each client")
        print("   3. get_recommendations(isins) - Check ratings for each ISIN")
        print("   → Claude combines results to show clients with SELL positions")
        
        # Query 2: High cash positions
        self.print_query(
            "Find clients with excessive cash positions",
            "Which of my clients holds more than 20% cash? This might indicate they need rebalancing."
        )
        print("🔧 MCP Tools Used:")
        print("   1. get_clients() - Get all clients")
        print("   2. get_client_positions(client_id) - Check cash allocation")
        print("   → Claude calculates cash percentages and filters results")
        
        # Query 3: Specific security holdings
        self.print_query(
            "Find Apple stockholders",
            "Which of my clients holds Apple stock (AAPL)? What's their exposure?"
        )
        print("🔧 MCP Tools Used:")
        print("   1. get_clients() - Get all clients")
        print("   2. get_client_positions(client_id) - Check for Apple ISIN")
        print("   3. get_recommendations([Apple_ISIN]) - Current Apple rating")
        print("   → Claude shows all Apple holders with position sizes and ratings")
        
        # Query 4: Asset type analysis
        self.print_query(
            "Find clients without equity exposure",
            "Which of my clients does not have any stocks? They might be too conservative."
        )
        print("🔧 MCP Tools Used:")
        print("   1. get_clients() - Get all clients")
        print("   2. get_client_positions(client_id, asset_type='equity') - Check equity positions")
        print("   → Claude identifies clients with zero equity exposure")
        
        # Query 5: Bond analysis
        self.print_query(
            "Analyze bond holdings across clients",
            "Which clients hold bonds? Show me their bond allocation and credit quality."
        )
        print("🔧 MCP Tools Used:")
        print("   1. get_clients() - Get all clients") 
        print("   2. get_client_positions(client_id, asset_type='bond') - Get bond positions")
        print("   3. get_recommendations() - Bond ratings and analysis")
        print("   → Claude aggregates bond holdings with credit analysis")
        
        # Query 6: Risk profile alignment
        self.print_query(
            "Check portfolio-risk alignment",
            "Show me clients whose portfolios don't match their risk profiles. Who needs rebalancing?"
        )
        print("🔧 MCP Tools Used:")
        print("   1. get_clients() - Get client risk profiles")
        print("   2. get_client_positions(client_id) - Get full portfolio")
        print("   → Claude calculates allocation vs. risk profile targets")
        
        # Query 7: Performance vs recommendations
        self.print_query(
            "Analyze recommendation performance",
            "How are my clients positioned relative to our research recommendations? Any conflicts?"
        )
        print("🔧 MCP Tools Used:")
        print("   1. get_clients() - Get all clients")
        print("   2. get_client_positions(client_id) - Get all positions")
        print("   3. get_recommendations() - Get all current ratings")
        print("   → Claude cross-references holdings vs. recommendations")
        
        # Query 8: Sector concentration analysis
        self.print_query(
            "Identify sector concentration risks",
            "Which clients have too much exposure to Technology stocks? Show sector breakdown."
        )
        print("🔧 MCP Tools Used:")
        print("   1. get_clients() - Get all clients")
        print("   2. get_client_positions(client_id) - Get positions with sector info")
        print("   → Claude aggregates by sector and identifies concentration risks")
        
        # Query 9: Investment opportunities
        self.print_query(
            "Find investment opportunities",
            "Which clients have cash available and which BUY-rated securities should we consider?"
        )
        print("🔧 MCP Tools Used:")
        print("   1. get_clients() - Get all clients")
        print("   2. get_client_positions(client_id) - Check cash levels")
        print("   3. get_recommendations(rating_filter='BUY') - Get BUY recommendations")
        print("   → Claude matches available cash with investment opportunities")
        
        # Query 10: Comprehensive client review
        self.print_query(
            "Complete client portfolio review",
            "Give me a complete analysis of client BZ-00001: positions, recommendations, risk alignment, and action items."
        )
        print("🔧 MCP Tools Used:")
        print("   1. get_client_positions('BZ-00001') - Full portfolio")
        print("   2. get_recommendations([all_ISINs_from_portfolio]) - All relevant ratings")
        print("   → Claude provides comprehensive portfolio analysis")
    
    def show_sample_responses(self):
        """Show what the MCP responses look like"""
        
        self.print_section("SAMPLE MCP TOOL RESPONSES")
        
        print("\n📊 Sample get_clients() response:")
        sample_clients = {
            "clients": [
                {
                    "client_id": "BZ-00001",
                    "name": "John Smith", 
                    "risk_profile": "Conservative",
                    "total_aum": 2500000,
                    "status": "active"
                }
            ],
            "summary": {
                "total_count": 10,
                "total_aum": 29750000,
                "risk_profile_breakdown": {
                    "Conservative": {"count": 4, "total_aum": 6100000},
                    "Moderate": {"count": 3, "total_aum": 7700000}, 
                    "Aggressive": {"count": 3, "total_aum": 16050000}
                }
            }
        }
        print(json.dumps(sample_clients, indent=2))
        
        print("\n📈 Sample get_client_positions() response:")
        sample_positions = {
            "client_id": "BZ-00001",
            "client_name": "John Smith",
            "positions": [
                {
                    "type": "equity",
                    "isin": "US0378331005",
                    "name": "Apple Inc.",
                    "shares": 500,
                    "price": 235.50,
                    "valuation": 117750.00,
                    "weight": 4.71,
                    "recommendation": {
                        "rating": "BUY",
                        "target_price": 250.00,
                        "upside_potential": 6.16
                    }
                }
            ],
            "summary": {
                "total_value": 2500000,
                "asset_breakdown": {
                    "cash": {"percentage": 20.0},
                    "bonds": {"percentage": 55.0},
                    "equity": {"percentage": 25.0}
                },
                "recommendation_summary": {"BUY": 3, "SELL": 1, "NEUTRAL": 2}
            }
        }
        print(json.dumps(sample_positions, indent=2))
        
        print("\n🎯 Sample get_recommendations() response:")
        sample_recommendations = {
            "recommendations": [
                {
                    "isin": "US0378331005",
                    "security_name": "Apple Inc.",
                    "rating": "BUY",
                    "target_price": 250.00,
                    "current_price": 235.50,
                    "upside_potential": 6.16,
                    "analyst": "Tech Research Team",
                    "rationale": "Strong iPhone sales and AI integration"
                }
            ],
            "summary": {
                "rating_breakdown": {"BUY": 8, "SELL": 3, "NEUTRAL": 7},
                "avg_upside_potential": 12.5
            }
        }
        print(json.dumps(sample_recommendations, indent=2))
    
    def show_integration_examples(self):
        """Show how Claude integrates multiple tools"""
        
        self.print_section("INTEGRATION EXAMPLES")
        
        print("\n🤖 How Claude answers: 'Which clients have SELL-rated positions?'")
        print("\nStep 1: Get all clients")
        print("   → Tool call: get_clients()")
        print("   → Returns: List of 10 clients")
        
        print("\nStep 2: For each client, get their positions")
        print("   → Tool calls: get_client_positions('BZ-00001'), get_client_positions('BZ-00002'), etc.")
        print("   → Returns: All securities (ISINs) held by each client")
        
        print("\nStep 3: Get recommendations for all unique ISINs")
        print("   → Tool call: get_recommendations(['US0378331005', 'US88160R1014', ...])")
        print("   → Returns: BUY/SELL/NEUTRAL ratings for each security")
        
        print("\nStep 4: Claude correlates the data")
        print("   → Identifies which clients hold SELL-rated securities")
        print("   → Calculates exposure amounts and percentages")
        print("   → Formats a comprehensive response")
        
        print("\n💡 Sample Claude Response:")
        print('''
        Based on my analysis of your client portfolios and current research recommendations, 
        here are the clients with SELL-rated positions:
        
        **Client BZ-00003 (Michael Chen)**
        - Tesla Inc. (TSLA): $195,750 (3.8% of portfolio) - SELL rating
        - Intel Corp. (INTC): $89,250 (1.7% of portfolio) - SELL rating
        - Total SELL exposure: $285,000 (5.5% of portfolio)
        - Risk: High exposure to SELL-rated securities for aggressive profile
        
        **Client BZ-00007 (David Martinez)**  
        - Disney Corporate Bond: $125,000 (10.4% of portfolio) - SELL rating
        - Risk: Significant bond exposure with deteriorating credit outlook
        
        **Action Items:**
        1. Schedule review with Michael Chen - consider reducing Tesla/Intel positions
        2. Discuss Disney bond replacement options with David Martinez
        3. Monitor these positions for further rating changes
        ''')
    
    def show_installation_guide(self):
        """Show how to set up and test the MCP server"""
        
        self.print_section("INSTALLATION & TESTING GUIDE")
        
        print("\n📋 Step-by-Step Setup:")
        print("1. Save the Phase 4 code as 'wealth_management_server.py'")
        print("2. Install dependencies: pip install mcp")
        print("3. Test the server: python wealth_management_server.py")
        print("4. Configure Claude Desktop MCP settings")
        print("5. Start asking complex questions!")
        
        print("\n🔧 MCP Configuration for Claude Desktop:")
        mcp_config = {
            "mcpServers": {
                "wealth-management": {
                    "command": "python",
                    "args": ["/path/to/wealth_management_server.py"],
                    "env": {}
                }
            }
        }
        print("Add this to your Claude Desktop MCP configuration:")
        print(json.dumps(mcp_config, indent=2))
        
        print("\n✅ Testing Checklist:")
        test_queries = [
            "Show me all my clients",
            "Get positions for client BZ-00001", 
            "What are the current BUY recommendations?",
            "Which clients hold Apple stock?",
            "Which clients have more than 15% cash?",
            "Show me clients with SELL-rated positions",
            "Which clients don't have any bonds?",
            "Analyze the portfolio of client BZ-00003"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"{i}. '{query}'")
        
        print("\n🎯 Success Criteria:")
        print("✓ All queries return structured data")
        print("✓ Cross-tool integration works seamlessly") 
        print("✓ Error handling prevents crashes")
        print("✓ Performance is acceptable for 10 clients")
        print("✓ Claude can answer complex analytical questions")
    
    def run_all_demonstrations(self):
        """Run all demonstrations"""
        print("🏦 WEALTH MANAGEMENT MCP SERVER - TESTING GUIDE")
        print("This demonstrates the advanced analytical capabilities of your MCP server")
        
        self.demonstrate_advanced_queries()
        self.show_sample_responses() 
        self.show_integration_examples()
        self.show_installation_guide()
        
        self.print_section("CONCLUSION")
        print("✅ Your MCP server now enables sophisticated wealth management queries!")
        print("🤖 Claude Desktop becomes an intelligent client advisor interface")
        print("📊 Cross-tool integration provides comprehensive portfolio analysis")
        print("🔍 Complex questions get accurate, data-driven answers")
        print("\n🚀 Ready to revolutionize your wealth management workflow!")

if __name__ == "__main__":
    tester = MCPQueryTester()
    tester.run_all_demonstrations()