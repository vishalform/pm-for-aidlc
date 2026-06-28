#!/usr/bin/env python3
"""cost_calc.py — inference unit-economics calculator (AT-70/76/59).

"For an AI product, inference is COGS." This makes cost-per-task, margin, the
cost-quality frontier, and the gross-margin tail deterministic instead of
hand-computed. Prices are user-supplied (nothing fabricated); token prices are per
1,000,000 tokens unless you say otherwise.

Subcommands:
  per-task  cost of one task from tokens x price (+ tool/infra cost) x model calls
  margin    contribution margin from price and cost
  frontier  cost-quality Pareto front; cheapest model clearing a quality floor
  tail      project COGS / margin as usage grows (AT-76 "margin can invert")

Examples:
  python cost_calc.py per-task --in-tok 1800 --out-tok 350 --in-price 3.0 --out-price 15.0 \\
      --tool-cost 0.002 --calls 4
  python cost_calc.py margin --price 0.25 --cost 0.04
  python cost_calc.py frontier --data models.tsv --quality-floor 0.8   # cols: model quality cost
  python cost_calc.py tail --cost-per-task 0.04 --tasks-per-user 30 --users 50000 \\
      --price-per-user 20 --growth 2.0
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402


# ---------- pure helpers (golden-tested by `selftest`) ----------
def per_task_cost(in_tok, out_tok, in_price, out_price, tool_cost=0.0, calls=1, per_1k=False):
    """Return (per_call_cost, total_cost_per_task). Prices per 1M tokens (or 1k if per_1k)."""
    scale = 1_000.0 if per_1k else 1_000_000.0
    per_call = in_tok / scale * in_price + out_tok / scale * out_price
    return per_call, per_call * calls + tool_cost


def margin_of(price, cost):
    """Return (contribution, gross_margin_fraction)."""
    contribution = price - cost
    return contribution, (contribution / price if price else float("nan"))


def pareto_front(rows):
    """rows = [(model, quality, cost)]; return the non-dominated set, cheapest first."""
    front = [(m, q, c) for m, q, c in rows
             if not any((q2 >= q and c2 <= c and (q2 > q or c2 < c))
                        for m2, q2, c2 in rows if m2 != m)]
    front.sort(key=lambda r: r[2])
    return front


def cheapest_clearing(rows, floor):
    """Cheapest model whose quality clears `floor`, or None."""
    clearing = [r for r in rows if r[1] >= floor]
    return min(clearing, key=lambda r: r[2]) if clearing else None


def tail_projection(cost_per_task, tasks_per_user, users, price_per_user, growth):
    """Project COGS/margin now and at usage x growth (flat price => margin can invert)."""
    base_tasks = tasks_per_user * users
    out = {"base_tasks": base_tasks, "base_cogs": base_tasks * cost_per_task,
           "grown_tasks": base_tasks * growth, "grown_cogs": base_tasks * growth * cost_per_task}
    if price_per_user is not None:
        rev = price_per_user * users
        out["rev"] = rev
        out["base_gm"] = (rev - out["base_cogs"]) / rev if rev else float("nan")
        out["grown_gm"] = (rev - out["grown_cogs"]) / rev if rev else float("nan")
    return out


# ---------- subcommands ----------
def cmd_per_task(args) -> int:
    per_call, total = per_task_cost(args.in_tok, args.out_tok, args.in_price, args.out_price,
                                    args.tool_cost, args.calls, args.per_1k)
    model_cost = per_call * args.calls
    unit = "1k" if args.per_1k else "1M"
    print(f"per-call model cost: ${per_call:.6f}  (in {args.in_tok} + out {args.out_tok} tok @ per-{unit} prices)")
    print(f"model cost x {args.calls} call(s): ${model_cost:.6f}")
    print(f"+ tool/infra cost: ${args.tool_cost:.6f}")
    print(f"COST PER TASK: ${total:.6f}")
    if args.price is not None:
        margin = (args.price - total) / args.price if args.price else float("nan")
        print(f"at price ${args.price:.4f}: contribution ${args.price - total:.6f}  margin {margin*100:.1f}%")
        if total > args.price:
            print("  ! NEGATIVE margin — loved-and-unprofitable per call is a problem, not a win.")
    return 0


def cmd_margin(args) -> int:
    if args.price <= 0:
        raise SystemExit("--price must be > 0")
    contribution, margin = margin_of(args.price, args.cost)
    print(f"price=${args.price:.4f}  cost=${args.cost:.4f}")
    print(f"contribution=${contribution:.4f}  gross margin={margin*100:.1f}%")
    if contribution < 0:
        print("  ! negative contribution — every call loses money.")
    return 0


def cmd_frontier(args) -> int:
    rows = []
    with open(args.data, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            parts = ln.replace(",", "\t").split("\t") if ("\t" in ln or "," in ln) else ln.split()
            if len(parts) < 3:
                raise SystemExit(f"need 'model quality cost' per row: {ln!r}")
            rows.append((parts[0], float(parts[1]), float(parts[2])))
    if not rows:
        raise SystemExit("no model rows")
    front = pareto_front(rows)
    print("cost-quality Pareto front (cheapest first):")
    for m, q, c in front:
        print(f"  {m}: quality={q:.4f} cost=${c:.6f}")
    if args.quality_floor is not None:
        best = cheapest_clearing(rows, args.quality_floor)
        if best:
            print(f"\ncheapest model clearing quality>={args.quality_floor}: "
                  f"{best[0]} (quality={best[1]:.4f}, cost=${best[2]:.6f})")
            print("  -> the cheapest model that clears your bar wins.")
        else:
            print(f"\nno model clears quality>={args.quality_floor}.")
    return 0


def cmd_tail(args) -> int:
    t = tail_projection(args.cost_per_task, args.tasks_per_user, args.users,
                        args.price_per_user, args.growth)
    print(f"base: {args.users:,.0f} users x {args.tasks_per_user:,.0f} tasks = {t['base_tasks']:,.0f} tasks/period")
    print(f"base COGS: ${t['base_cogs']:,.2f}")
    if "rev" in t:
        print(f"base revenue: ${t['rev']:,.2f}   gross margin: {t['base_gm']*100:.1f}%")
    print(f"\nsensitivity (usage x{args.growth} as the feature succeeds):")
    print(f"  tasks: {t['grown_tasks']:,.0f}   COGS: ${t['grown_cogs']:,.2f}")
    if "rev" in t:
        print(f"  revenue (flat): ${t['rev']:,.2f}   gross margin: {t['grown_gm']*100:.1f}%")
        if t["grown_gm"] < 0:
            print("  ! margin INVERTED at scale — flat price on metered COGS loses money as usage grows.")
    return 0


def cmd_selftest(args) -> int:
    """Golden-value regression checks for the cost math (margin inversion incl.)."""
    def approx(a, b, tol=1e-9):
        return abs(a - b) <= tol

    checks = []

    def chk(name, ok):
        checks.append((name, bool(ok)))

    per_call, total = per_task_cost(1000, 1000, 3.0, 15.0)
    chk("per_task_cost(1k in/out @ $3/$15) per_call=$0.018", approx(per_call, 0.018))
    chk("per_task_cost total=$0.018 (1 call, no tool)", approx(total, 0.018))
    contribution, margin = margin_of(0.25, 0.04)
    chk("margin_of(0.25,0.04) contribution=0.21", approx(contribution, 0.21))
    chk("margin_of(0.25,0.04) margin=0.84", approx(margin, 0.84))
    rows = [("a", 0.70, 0.01), ("b", 0.90, 0.05), ("c", 0.80, 0.02)]
    chk("pareto_front order = a,c,b", [m for m, _, _ in pareto_front(rows)] == ["a", "c", "b"])
    chk("cheapest_clearing(floor=0.8)=c", cheapest_clearing(rows, 0.8)[0] == "c")
    chk("cheapest_clearing(floor=0.99)=None", cheapest_clearing(rows, 0.99) is None)
    # margin inversion: flat price, metered cost — positive now, negative at high growth
    base = tail_projection(0.04, 30, 1000, 20, 2)
    grown = tail_projection(0.04, 30, 1000, 20, 20)
    chk("tail base margin positive", base["grown_gm"] > 0)
    chk("tail margin INVERTS at x20 growth", grown["grown_gm"] < 0)

    failed = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {n}")
    print(f"cost_calc selftest: {len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pt = sub.add_parser("per-task", help="cost of one task")
    pt.add_argument("--in-tok", type=float, required=True)
    pt.add_argument("--out-tok", type=float, required=True)
    pt.add_argument("--in-price", type=float, required=True, help="price per 1M input tokens")
    pt.add_argument("--out-price", type=float, required=True, help="price per 1M output tokens")
    pt.add_argument("--tool-cost", type=float, default=0.0, help="tool/infra cost per task")
    pt.add_argument("--calls", type=int, default=1, help="model calls per task")
    pt.add_argument("--per-1k", action="store_true", help="prices are per 1k tokens, not 1M")
    pt.add_argument("--price", type=float, help="task price (to also show margin)")
    pt.set_defaults(func=cmd_per_task)

    mg = sub.add_parser("margin", help="contribution margin")
    mg.add_argument("--price", type=float, required=True)
    mg.add_argument("--cost", type=float, required=True)
    mg.set_defaults(func=cmd_margin)

    fr = sub.add_parser("frontier", help="cost-quality Pareto front")
    fr.add_argument("--data", required=True, help="rows of 'model quality cost'")
    fr.add_argument("--quality-floor", type=float, help="cheapest model clearing this quality")
    fr.set_defaults(func=cmd_frontier)

    tl = sub.add_parser("tail", help="COGS/margin as usage grows")
    tl.add_argument("--cost-per-task", type=float, required=True)
    tl.add_argument("--tasks-per-user", type=float, required=True)
    tl.add_argument("--users", type=float, required=True)
    tl.add_argument("--price-per-user", type=float, help="flat price/user (to show margin inversion)")
    tl.add_argument("--growth", type=float, default=2.0, help="usage multiplier at scale")
    tl.set_defaults(func=cmd_tail)

    st = sub.add_parser("selftest", help="golden-value regression checks (exit 1 on any failure)")
    st.set_defaults(func=cmd_selftest)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
