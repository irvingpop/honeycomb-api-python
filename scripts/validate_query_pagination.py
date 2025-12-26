#!/usr/bin/env python3
"""Validate query result pagination functionality against live Honeycomb API.

This script tests:
1. disable_series=True default (up to 10K results)
2. run_all_async() with sort-based pagination
3. Progress callbacks
4. Deduplication
5. Smart stopping

Usage:
    poetry run python scripts/validate_query_pagination.py \
        --api-key YOUR_KEY \
        --dataset YOUR_DATASET \
        [--api-url https://api.honeycomb.io]

    Or with environment variables:
    export HONEYCOMB_API_KEY=your_api_key
    export HONEYCOMB_DATASET=your_dataset
    poetry run python scripts/validate_query_pagination.py
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from honeycomb import HoneycombClient, QuerySpec


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate Honeycomb query pagination features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using CLI arguments
  %(prog)s --api-key hcaik_xxx --dataset my-dataset

  # Using environment variables
  export HONEYCOMB_API_KEY=hcaik_xxx
  export HONEYCOMB_DATASET=my-dataset
  %(prog)s

  # Override API URL (e.g., for EU region)
  %(prog)s --api-key hcaik_xxx --dataset my-dataset --api-url https://api.eu1.honeycomb.io

  # Custom breakdown fields
  %(prog)s --api-key hcaik_xxx --dataset my-dataset --breakdowns "trace.trace_id,name,service.name"
        """,
    )

    parser.add_argument(
        "--api-key",
        default=os.environ.get("HONEYCOMB_API_KEY"),
        help="Honeycomb API key (or set HONEYCOMB_API_KEY env var)",
    )
    parser.add_argument(
        "--dataset",
        default=os.environ.get("HONEYCOMB_DATASET"),
        help="Dataset slug to query (or set HONEYCOMB_DATASET env var)",
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("HONEYCOMB_API_URL", "https://api.honeycomb.io"),
        help="Honeycomb API base URL (default: https://api.honeycomb.io)",
    )
    parser.add_argument(
        "--breakdowns",
        default="name",
        help="Comma-separated list of breakdown fields to use in queries (default: name)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed request/response information for debugging",
    )

    args = parser.parse_args()

    # Validate required arguments
    if not args.api_key:
        parser.error(
            "API key is required. Provide --api-key or set HONEYCOMB_API_KEY env var"
        )
    if not args.dataset:
        parser.error(
            "Dataset is required. Provide --dataset or set HONEYCOMB_DATASET env var"
        )

    # Parse breakdowns into list
    args.breakdown_list = [b.strip() for b in args.breakdowns.split(",")]

    return args


async def test_basic_query_with_disable_series(args):
    """Test 1: Basic query with disable_series=True default."""
    print("\n" + "=" * 80)
    print("TEST 1: Basic Query with disable_series=True (up to 10K results)")
    print("=" * 80)

    try:
        async with HoneycombClient(api_key=args.api_key, base_url=args.api_url) as client:
            print(f"\n📊 Running COUNT query on dataset: {args.dataset}")
            print("   Time range: Last 1 hour")
            print("   Expected: disable_series=True, limit=10000 (automatic)")

            spec = QuerySpec(
                time_range=3600,  # Last hour
                calculations=[{"op": "COUNT"}],
            )

            if args.verbose:
                import json

                print(f"\n🔍 Query spec (saved query):")
                print(json.dumps(spec.model_dump_for_api(), indent=2))

                print(f"\n🔍 Query result execution params:")
                print(f"   disable_series: True")
                print(f"   limit: 10000 (set at execution, not in saved query)")

            query, result = await client.query_results.create_and_run_async(
                args.dataset, spec=spec
            )

            print(f"\n✅ Query completed!")
            print(f"   Saved as query ID: {query.id}")
            results = result.data.rows if result.data else []
            print(f"   Results returned: {len(results)}")
            print(f"   First few results: {results[:3]}")

        return True

    except Exception as e:
        from honeycomb.exceptions import HoneycombValidationError

        if isinstance(e, HoneycombValidationError):
            print(f"\n❌ Validation error: {e.message}")
            if e.errors:
                print(f"   Details: {e.errors}")
            print(f"   Request ID: {e.request_id}")
        raise


async def test_query_with_breakdowns(args):
    """Test 2: Query with breakdowns to test composite key deduplication."""
    print("\n" + "=" * 80)
    print("TEST 2: Query with Breakdowns (GROUP BY)")
    print("=" * 80)

    async with HoneycombClient(api_key=args.api_key, base_url=args.api_url) as client:
        print(f"\n📊 Running query with breakdowns on dataset: {args.dataset}")
        print("   Time range: Last 6 hours")
        print(f"   Breakdowns: {', '.join(args.breakdown_list)}")
        print("   Calculations: COUNT")

        query, result = await client.query_results.create_and_run_async(
            args.dataset,
            spec=QuerySpec(
                time_range=21600,  # 6 hours
                calculations=[{"op": "COUNT"}],
                breakdowns=args.breakdown_list,
            ),
        )

        print(f"\n✅ Query completed!")
        print(f"   Saved as query ID: {query.id}")
        results = result.data.rows if result.data else []
        print(f"   Unique groups: {len(results)}")
        if results:
            # Debug: Show actual keys in first result
            if args.verbose and len(results) > 0:
                print(f"\n🔍 Actual keys in first result: {list(results[0].keys())}")
                print(f"   First result data: {results[0]}")

            print(f"   Top 5 groups by count:")
            for row in results[:5]:
                # Show breakdown values
                breakdown_vals = " | ".join(
                    f"{bd}={row.get(bd, 'N/A')}" for bd in args.breakdown_list
                )
                count = row.get("COUNT", 0)
                print(f"     - {breakdown_vals}: {count}")

    return True


async def test_run_all_with_pagination(args):
    """Test 3: run_all_async() with multi-page pagination."""
    print("\n" + "=" * 80)
    print("TEST 3: run_all_async() with Sort-Based Pagination")
    print("=" * 80)

    async with HoneycombClient(api_key=args.api_key, base_url=args.api_url) as client:
        print(f"\n📊 Running paginated query on dataset: {args.dataset}")
        print("   Time range: Last 24 hours")
        print("   Expected behavior:")
        print("     - Multiple queries if > 10K results")
        print("     - Progress callbacks showing pages")
        print("     - Automatic deduplication")
        print("     - Smart stopping at 50% duplicates")

        # Track progress
        progress_log = []
        prev_total = 0

        def on_page(page_num, total_rows):
            nonlocal prev_total
            new_rows = total_rows - prev_total
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg = f"[{timestamp}] Page {page_num}: +{new_rows} new, {total_rows} total"
            print(f"   {msg}")
            progress_log.append((page_num, new_rows, total_rows))
            prev_total = total_rows

        print("\n⏳ Starting pagination (this may take a minute)...\n")

        try:
            if args.verbose:
                print("🔍 Calling run_all_async with:")
                print(f"   calculations: {[{'op': 'COUNT'}]}")
                print(f"   breakdowns: {args.breakdown_list}")
                print(f"   sort_order: descending")
                print(f"   max_results: 100,000")
                print()

            rows = await client.query_results.run_all_async(
                args.dataset,
                spec=QuerySpec(
                    time_range=86400,  # Last 24 hours
                    calculations=[{"op": "COUNT"}],
                    breakdowns=args.breakdown_list,
                ),
                sort_order="descending",  # Highest counts first
                max_results=100_000,
                on_page=on_page,
            )

            print(f"\n✅ Pagination completed!")
            print(f"   Total unique rows: {len(rows)}")
            print(f"   Pages fetched: {len(progress_log)}")

            # Debug: Show actual keys in first result
            if args.verbose and len(rows) > 0:
                print(f"\n🔍 Actual keys in first result: {list(rows[0].keys())}")
                print(f"   First result data: {rows[0]}")

            print(f"   Top 10 results:")
            for row in rows[:10]:
                # Show breakdown values
                breakdown_vals = " | ".join(
                    f"{bd}={row.get(bd, 'N/A')}" for bd in args.breakdown_list
                )
                count = row.get("COUNT", 0)
                print(f"     - {breakdown_vals}: {count}")

            # Verify deduplication
            if len(rows) > 0:
                print(f"\n🔍 Deduplication check:")
                # Build keys manually to verify
                seen = set()
                duplicates = 0
                for row in rows:
                    # Build key from all breakdowns + COUNT (uppercase)
                    key_parts = [row.get(bd) for bd in args.breakdown_list]
                    key_parts.append(row.get("COUNT"))
                    key = tuple(key_parts)
                    if key in seen:
                        duplicates += 1
                    seen.add(key)

                print(f"   Unique keys: {len(seen)}")
                print(f"   Duplicates found: {duplicates}")
                if duplicates == 0:
                    print("   ✅ No duplicates - deduplication working correctly!")
                else:
                    print(f"   ⚠️  Found {duplicates} duplicates")

        except ValueError as e:
            print(f"\n⚠️  Validation error: {e}")
            print("   This may happen if the query spec is invalid for this dataset")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            raise

    return True


async def test_disable_series_false(args):
    """Test 4: Verify disable_series=False works for timeseries data."""
    print("\n" + "=" * 80)
    print("TEST 4: disable_series=False (get timeseries data)")
    print("=" * 80)

    async with HoneycombClient(api_key=args.api_key, base_url=args.api_url) as client:
        print(f"\n📊 Running query with disable_series=False on dataset: {args.dataset}")
        print("   Time range: Last 1 hour")
        print("   Granularity: 5 minutes")
        print("   Expected: Timeseries data in results")

        query, result = await client.query_results.create_and_run_async(
            args.dataset,
            spec=QuerySpec(
                time_range=3600,
                granularity=300,  # 5-minute buckets
                calculations=[{"op": "COUNT"}],
            ),
            disable_series=False,  # Get timeseries data
        )

        print(f"\n✅ Query completed!")
        print(f"   Saved as query ID: {query.id}")
        results = result.data.rows if result.data else []
        series = result.data.series if result.data else None
        print(f"   Result rows: {len(results)}")

        # Check if timeseries data exists
        if series and len(series) > 0:
            print(f"   ✅ Timeseries data present (disable_series=False worked)")
            print(f"   Series buckets: {len(series)}")
        else:
            print(f"   ℹ️  No timeseries data in response")

    return True


async def main():
    """Run all validation tests."""
    # Parse arguments
    args = parse_args()

    # Enable debug logging if verbose (but only for our logger, not httpcore/httpx)
    if args.verbose:
        import logging

        # Only show DEBUG for honeycomb logger
        honeycomb_logger = logging.getLogger("honeycomb")
        honeycomb_logger.setLevel(logging.DEBUG)

        # Console handler
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        honeycomb_logger.addHandler(handler)

        # Silence noisy HTTP loggers
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)

    print("\n" + "=" * 80)
    print("HONEYCOMB QUERY PAGINATION VALIDATION")
    print("=" * 80)

    print(f"\n✅ Configuration:")
    print(f"   API URL: {args.api_url}")
    print(f"   API Key: {args.api_key[:20]}...")
    print(f"   Dataset: {args.dataset}")
    print(f"   Breakdowns: {', '.join(args.breakdown_list)}")

    # Run tests
    tests = [
        ("Basic Query (disable_series=True)", test_basic_query_with_disable_series),
        ("Query with Breakdowns", test_query_with_breakdowns),
        ("Advanced Pagination (run_all_async)", test_run_all_with_pagination),
        ("Timeseries Data (disable_series=False)", test_disable_series_false),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = await test_func(args)
            results.append((test_name, success))
        except Exception as e:
            from honeycomb.exceptions import HoneycombValidationError

            if isinstance(e, HoneycombValidationError):
                print(f"\n❌ Validation Error in '{test_name}':")
                print(f"   Message: {e.message}")
                print(f"   Status: {e.status_code}")
                if e.errors:
                    print(f"   Error details: {e.errors}")
                if e.request_id:
                    print(f"   Request ID: {e.request_id}")
                if hasattr(e, "response_body") and e.response_body:
                    print(f"   Response body: {e.response_body}")
            else:
                print(f"\n❌ Test '{test_name}' failed with exception: {e}")

            if args.verbose:
                import traceback

                print("\nFull traceback:")
                traceback.print_exc()

            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All validation tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
