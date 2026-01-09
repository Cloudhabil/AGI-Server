#!/usr/bin/env python3
"""
Budget System Monitoring Dashboard

Real-time display of:
- Current resource utilization
- Active allocations
- Recent decisions
- Learning progress
"""

import time
import sys
from pathlib import Path


def monitor_budget_system():
    """Main monitoring loop."""
    print("\n" + "=" * 70)
    print("BUDGET ALLOCATOR SYSTEM - MONITORING DASHBOARD")
    print("=" * 70)
    print("\nStarting real-time monitoring...")
    print("Press Ctrl+C to stop.\n")

    try:
        from core.kernel.budget_service import get_budget_service
        budget_service = get_budget_service()

        while True:
            # Get snapshot
            snapshot = budget_service.get_resource_snapshot(force_refresh=True)
            is_safe, safety_reason = budget_service.check_safety(snapshot)
            stats = budget_service.get_usage_stats()

            # Clear screen and display
            print("\033[2J\033[H", end="")  # Clear screen (Unix)
            print("=" * 70)
            print("BUDGET ALLOCATOR SYSTEM - MONITORING DASHBOARD")
            print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)

            # Resources
            print("\n[RESOURCES]")
            print(f"  CPU:  {snapshot.cpu_percent:6.1f}% ", end="")
            cpu_bar = "█" * int(snapshot.cpu_percent / 5) + "░" * (20 - int(snapshot.cpu_percent / 5))
            print(f"[{cpu_bar}]")

            print(f"  RAM:  {snapshot.ram_util*100:6.1f}% ", end="")
            ram_bar = "█" * int(snapshot.ram_util * 20) + "░" * (20 - int(snapshot.ram_util * 20))
            print(f"[{ram_bar}] ({snapshot.ram_used_mb}/{snapshot.ram_total_mb} MB)")

            if snapshot.vram_total_mb:
                print(f"  VRAM: {snapshot.vram_util*100:6.1f}% ", end="")
                vram_bar = "█" * int((snapshot.vram_util or 0) * 20) + "░" * (20 - int((snapshot.vram_util or 0) * 20))
                print(f"[{vram_bar}] ({snapshot.vram_used_mb}/{snapshot.vram_total_mb} MB)")
            else:
                print(f"  VRAM: N/A")

            print(f"  Disk: R={snapshot.disk_read_mbps:6.1f} MB/s | W={snapshot.disk_write_mbps:6.1f} MB/s")
            print(f"  NPU:  {'✓ Available' if snapshot.npu_available else '✗ Not available'}")

            # Safety
            safety_icon = "✓" if is_safe else "✗"
            safety_color = "\033[92m" if is_safe else "\033[91m"  # Green or Red
            reset_color = "\033[0m"
            print(f"\n[SAFETY] {safety_color}{safety_icon}{reset_color} {safety_reason}")

            # Allocations
            print(f"\n[ALLOCATIONS]")
            print(f"  Total active tokens: {stats.get('total_active_tokens', 0)}")
            print(f"  Total allocations:   {stats.get('total_allocations', 0)}")

            by_agent = stats.get('by_agent', {})
            if by_agent:
                print("  By agent:")
                for agent, tokens in sorted(by_agent.items()):
                    print(f"    - {agent:<20} {tokens:>6} tokens")

            by_status = stats.get('by_status', {})
            if by_status:
                print("  By status:")
                for status, count in sorted(by_status.items()):
                    print(f"    - {status:<20} {count:>3} allocations")

            # Decision info
            print(f"\n[DECISION ENGINE]")
            try:
                from agents.budget_allocator_autonomous import get_allocator
                allocator = get_allocator()
                weights = allocator.weights
                print(f"  Decision Weights (learned):")
                print(f"    urgency:      {weights.urgency:.3f}")
                print(f"    agent_tier:   {weights.agent_tier:.3f}")
                print(f"    complexity:   {weights.complexity:.3f}")
                print(f"    success_rate: {weights.success_rate:.3f}")
                print(f"    load_factor:  {weights.load_factor:.3f}")
                print(f"    fairness:     {weights.fairness:.3f}")
                print(f"    efficiency:   {weights.efficiency:.3f}")
            except Exception as e:
                print(f"  (Allocator not ready: {e})")

            print("\n" + "-" * 70)
            print("Press Ctrl+C to stop | Updating in 5 seconds...")
            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    monitor_budget_system()
