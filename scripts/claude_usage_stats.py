#!/usr/bin/env python3
"""
Claude Usage Statistics

This script fetches and displays usage statistics for Claude Code,
including token usage and cost information for current session,
daily, weekly, and monthly periods.
"""

# /// script
# dependencies = [
#   "requests>=2.28.0",
# ]
# ///

import argparse
import datetime
import json
import os
import subprocess
import sys
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

# Constants
COST_PER_1K_INPUT_TOKENS = 0.03  # Claude 3 Opus input cost per 1K tokens
COST_PER_1K_OUTPUT_TOKENS = 0.15  # Claude 3 Opus output cost per 1K tokens

# Default limits for log fetching
DAILY_LOG_LIMIT = 100
WEEKLY_LOG_LIMIT = 500
MONTHLY_LOG_LIMIT = 1000
SESSION_LOG_LIMIT = 50


def run_command(command: List[str]) -> Tuple[str, bool]:
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout, True
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}", False


def get_claude_version() -> str:
    """Get Claude CLI version information."""
    cmd, success = run_command(["claude", "--version"])
    if success:
        return cmd.strip()
    return "Unknown"


def get_claude_config() -> Dict[str, Any]:
    """Get Claude CLI configuration."""
    config_paths = [
        os.path.expanduser("~/.config/claude/config.json"),
        os.path.expanduser("~/.claude/config.json")
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading Claude config at {config_path}: {e}")
    
    print("Claude config not found")
    return {}


def get_current_session_stats() -> Dict[str, Any]:
    """Get statistics for the current Claude Code session."""
    # Use claude stats command to get current session stats
    cmd, success = run_command(["claude", "stats", "--format", "json"])
    
    if success:
        try:
            stats = json.loads(cmd)
            # Add session start time if not present
            if "session_start" not in stats:
                stats["session_start"] = (datetime.now() - timedelta(hours=1)).isoformat()
            return stats
        except json.JSONDecodeError as e:
            print(f"Error parsing stats data: {e}")
    
    # If stats command failed, try to build stats from logs
    cmd, success = run_command(["claude", "logs", "--format", "json", "--limit", str(SESSION_LOG_LIMIT)])
    
    if success:
        try:
            logs = json.loads(cmd)
            # Process logs to extract token usage
            input_tokens = 0
            output_tokens = 0
            first_timestamp = None
            last_timestamp = None
            
            for entry in logs:
                if "tokens" in entry:
                    input_tokens += entry.get("tokens", {}).get("prompt", 0)
                    output_tokens += entry.get("tokens", {}).get("completion", 0)
                
                # Track timestamps for session duration
                timestamp = entry.get("timestamp")
                if timestamp:
                    try:
                        entry_time = datetime.fromisoformat(timestamp.replace("Z", ""))
                        if not first_timestamp or entry_time < first_timestamp:
                            first_timestamp = entry_time
                        if not last_timestamp or entry_time > last_timestamp:
                            last_timestamp = entry_time
                    except (ValueError, TypeError):
                        pass
            
            session_start = first_timestamp.isoformat() if first_timestamp else datetime.now().isoformat()
            
            return {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "session_start": session_start
            }
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error processing logs: {e}")
    
    # Create empty stats as a last resort
    now = datetime.now()
    session_start = now - timedelta(hours=1)
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "session_start": session_start.isoformat()
    }


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate cost based on token usage."""
    input_cost = (input_tokens / 1000) * COST_PER_1K_INPUT_TOKENS
    output_cost = (output_tokens / 1000) * COST_PER_1K_OUTPUT_TOKENS
    return input_cost + output_cost


def format_cost(cost: float) -> str:
    """Format cost as a dollar amount."""
    return f"${cost:.2f}"


def get_time_period_stats(period: str, start_time: Optional[datetime] = None, 
                         end_time: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Get statistics for a specific time period using the Claude stats command.
    
    Args:
        period: The time period identifier (daily, weekly, monthly, or session)
        start_time: Optional start time for custom period
        end_time: Optional end time for custom period
    
    Returns:
        A dictionary with token usage and cost statistics
    """
    # Calculate time range if not provided
    now = datetime.now()
    if not end_time:
        end_time = now
    
    if not start_time:
        if period == "daily":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "weekly":
            # Start of the week (Monday)
            start_time = (now - timedelta(days=now.weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        elif period == "monthly":
            # Start of the month
            start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            # Default to last 24 hours
            start_time = now - timedelta(days=1)
    
    # Format dates for claude stats command
    start_str = start_time.strftime("%Y-%m-%d")
    end_str = end_time.strftime("%Y-%m-%d")
    
    # Try to get stats directly from claude stats command for the time period
    if period in ["daily", "weekly", "monthly"]:
        cmd, success = run_command(["claude", "stats", "--period", period, "--format", "json"])
        
        if success:
            try:
                stats = json.loads(cmd)
                stats["period"] = period
                stats["start_time"] = start_time.isoformat()
                stats["end_time"] = end_time.isoformat()
                stats["total_tokens"] = stats.get("input_tokens", 0) + stats.get("output_tokens", 0)
                stats["cost"] = calculate_cost(stats.get("input_tokens", 0), stats.get("output_tokens", 0))
                return stats
            except json.JSONDecodeError:
                pass
    
    # If the direct period doesn't work, try using date range
    cmd, success = run_command(["claude", "stats", "--from", start_str, "--to", end_str, "--format", "json"])
    
    if success:
        try:
            stats = json.loads(cmd)
            stats["period"] = period
            stats["start_time"] = start_time.isoformat()
            stats["end_time"] = end_time.isoformat()
            stats["total_tokens"] = stats.get("input_tokens", 0) + stats.get("output_tokens", 0)
            stats["cost"] = calculate_cost(stats.get("input_tokens", 0), stats.get("output_tokens", 0))
            return stats
        except json.JSONDecodeError:
            pass
    
    # If stats commands failed, use logs as fallback
    input_tokens = 0
    output_tokens = 0
    
    # Get logs for the entire period with appropriate limit
    if period == "monthly":
        limit = MONTHLY_LOG_LIMIT
    elif period == "weekly":
        limit = WEEKLY_LOG_LIMIT
    elif period == "daily":
        limit = DAILY_LOG_LIMIT
    else:
        limit = SESSION_LOG_LIMIT
        
    cmd, success = run_command(["claude", "logs", "--format", "json", "--limit", str(limit)])
    
    if success:
        try:
            logs = json.loads(cmd)
            # Process logs to extract token usage within the time period
            for entry in logs:
                # Skip entries outside our time range
                timestamp = entry.get("timestamp")
                if not timestamp:
                    continue
                    
                try:
                    entry_time = datetime.fromisoformat(timestamp.replace("Z", ""))
                    if entry_time < start_time or entry_time > end_time:
                        continue
                        
                    # Add token counts for entries within our time range
                    if "tokens" in entry:
                        input_tokens += entry.get("tokens", {}).get("prompt", 0)
                        output_tokens += entry.get("tokens", {}).get("completion", 0)
                except (ValueError, TypeError):
                    continue
        except json.JSONDecodeError as e:
            print(f"Error processing logs: {e}")
    
    # Last resort - return zeros instead of estimates
    cost = calculate_cost(input_tokens, output_tokens)
    
    return {
        "period": period,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost,
        "start_time": start_time.isoformat() if start_time else None,
        "end_time": end_time.isoformat() if end_time else None
    }


def print_usage_report(
    current_stats: Dict[str, Any],
    daily_stats: Dict[str, Any],
    weekly_stats: Dict[str, Any],
    monthly_stats: Dict[str, Any]
) -> None:
    """Print a formatted usage report to the terminal."""
    print("\n" + "=" * 50)
    print("CLAUDE CODE USAGE STATISTICS")
    print("=" * 50)
    
    # Current Session
    current_cost = calculate_cost(
        current_stats.get("input_tokens", 0),
        current_stats.get("output_tokens", 0)
    )
    
    print("\nCURRENT SESSION:")
    print(f"  Input Tokens:  {current_stats.get('input_tokens', 0):,}")
    print(f"  Output Tokens: {current_stats.get('output_tokens', 0):,}")
    print(f"  Total Tokens:  {current_stats.get('input_tokens', 0) + current_stats.get('output_tokens', 0):,}")
    print(f"  Cost:          {format_cost(current_cost)}")
    
    if "session_start" in current_stats:
        try:
            start_time = datetime.fromisoformat(current_stats["session_start"].replace("Z", ""))
            duration = datetime.now() - start_time
            print(f"  Duration:      {duration}")
        except (ValueError, TypeError) as e:
            print(f"  Duration:      Unknown ({e})")
    
    # Time Period Stats
    print("\nUSAGE BY TIME PERIOD:")
    for stats in [daily_stats, weekly_stats, monthly_stats]:
        period = stats["period"].capitalize()
        print(f"  {period} Usage:")
        print(f"    Input Tokens:  {stats['input_tokens']:,}")
        print(f"    Output Tokens: {stats['output_tokens']:,}")
        print(f"    Total Tokens:  {stats['total_tokens']:,}")
        print(f"    Cost:          {format_cost(stats['cost'])}")
        
        if "start_time" in stats and stats["start_time"]:
            try:
                start_time = datetime.fromisoformat(stats["start_time"].replace("Z", ""))
                print(f"    Since:         {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            except (ValueError, TypeError):
                pass
    
    print("\nNOTE: Costs are estimates based on Claude 3 Opus pricing.")
    print("=" * 50 + "\n")


def main() -> None:
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description="Display Claude Code usage statistics")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    parser.add_argument("--days", "-d", type=int, help="Get stats for a specific number of days")
    args = parser.parse_args()
    
    # Get current session stats
    current_stats = get_current_session_stats()
    
    # Get custom period stats if requested
    if args.days:
        now = datetime.now()
        start_time = now - timedelta(days=args.days)
        period_stats = get_time_period_stats(f"last {args.days} days", start_time, now)
        daily_stats = weekly_stats = monthly_stats = period_stats
    else:
        # Get time period stats
        daily_stats = get_time_period_stats("daily")
        weekly_stats = get_time_period_stats("weekly")
        monthly_stats = get_time_period_stats("monthly")
    
    # Print the usage report
    print_usage_report(current_stats, daily_stats, weekly_stats, monthly_stats)
    
    if args.verbose:
        config = get_claude_config()
        # Remove sensitive information
        if "api_key" in config:
            config["api_key"] = "********"
        print("Claude Information:")
        print(f"Version: {get_claude_version()}")
        print("Configuration:")
        print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()