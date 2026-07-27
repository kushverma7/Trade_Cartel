#!/usr/bin/env python3
"""
KRONOS SIGNAL FILTER / VALIDATOR — Trade Cartel integration
===========================================================
Kronos (github.com/shiyu-coder/Kronos, AAAI 2026) is a transformer
foundation model for candlesticks, trained on 45 global exchanges. It
takes an OHLCV history window and samples probable FUTURE candles.

WHAT THIS IS FOR (honest scope -- read before using):
  Kronos CANNOT run inside TradingView. Pine Script has no ML
  inference, no Python, no external calls. So Kronos is NOT a
  replacement for the .pine strategies -- it is the RESEARCH and
  FILTER layer that sits beside them:

    1. VALIDATOR (primary use right now). Six engines have tested at
       PF 0.82-0.89 on XAUUSD 5m. The open question is whether that
       timeframe has ANY predictable structure. Kronos answers it
       directly: if a model trained on 45 exchanges cannot beat a
       coin flip on 5m gold next-bar direction, the problem is the
       timeframe, not our entry logic -- and we stop tuning it.
    2. FILTER. Run Kronos on the current window, take the sampled
       distribution of future closes, and only allow the Pine
       strategy's signal direction that agrees with it. Delivered to
       the chart via alert/webhook, or used manually.
    3. TARGET SETTING. Kronos samples full OHLCV paths, so the
       predicted high/low envelope is a data-driven TP/SL map to
       compare against the current key-level targets.

USAGE
  python3 kronos_signal_filter.py --csv data.csv --mode validate
  python3 kronos_signal_filter.py --csv data.csv --mode filter

  CSV needs columns: timestamps, open, high, low, close, volume
  (export from TradingView: right-click chart -> Export chart data)

WEIGHTS
  Requires the pretrained weights from HuggingFace (NeoQuasar/*).
  In THIS container huggingface.co is blocked by network policy, so
  the weights must either be (a) allowed via the environment's
  network settings, or (b) downloaded elsewhere and placed in
  --model-dir. Everything else (code, torch) is installed and ready.
"""
import argparse
import os
import sys

KRONOS_PATH = "/home/user/Kronos"
sys.path.insert(0, KRONOS_PATH)


def load_predictor(model_dir=None, tokenizer_id="NeoQuasar/Kronos-Tokenizer-base",
                   model_id="NeoQuasar/Kronos-small", device="cpu", max_context=512):
    """Load Kronos. model_dir overrides the HF ids with local paths."""
    from model import Kronos, KronosTokenizer, KronosPredictor
    tok_src = os.path.join(model_dir, "tokenizer") if model_dir else tokenizer_id
    mdl_src = os.path.join(model_dir, "model") if model_dir else model_id
    tokenizer = KronosTokenizer.from_pretrained(tok_src)
    model = Kronos.from_pretrained(mdl_src)
    return KronosPredictor(model, tokenizer, device=device, max_context=max_context)


def load_csv(path):
    import pandas as pd
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    # TradingView exports use 'time'; Kronos wants 'timestamps'
    if "timestamps" not in df.columns:
        for cand in ("time", "date", "datetime"):
            if cand in df.columns:
                df = df.rename(columns={cand: "timestamps"})
                break
    df["timestamps"] = pd.to_datetime(df["timestamps"])
    need = ["timestamps", "open", "high", "low", "close", "volume"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise SystemExit(f"CSV missing columns: {missing}. Have: {list(df.columns)}")
    if "amount" not in df.columns:
        df["amount"] = df["close"] * df["volume"]
    return df.reset_index(drop=True)


def predict_window(predictor, df, i, lookback, pred_len, samples):
    """Predict pred_len bars starting at index i. Returns pred DataFrame."""
    x_df = df.loc[i - lookback:i - 1, ["open", "high", "low", "close", "volume", "amount"]]
    x_ts = df.loc[i - lookback:i - 1, "timestamps"]
    y_ts = df.loc[i:i + pred_len - 1, "timestamps"]
    return predictor.predict(
        df=x_df, x_timestamp=x_ts, y_timestamp=y_ts,
        pred_len=pred_len, T=1.0, top_p=0.9, sample_count=samples, verbose=False,
    )


def mode_validate(predictor, df, lookback, pred_len, samples, step, limit):
    """
    THE decisive test: walk forward, ask Kronos for the next pred_len
    bars, score directional accuracy vs. what actually happened.
    Baseline to beat is 50%. Anything at ~50% means this timeframe
    has no exploitable structure for THIS model -- which is a real
    answer, not a failure.
    """
    import numpy as np
    hits, total, moves = 0, 0, []
    start = lookback
    end = len(df) - pred_len
    idxs = list(range(start, end, step))
    if limit:
        idxs = idxs[:limit]
    print(f"Walk-forward: {len(idxs)} windows, lookback={lookback}, horizon={pred_len}")
    for n, i in enumerate(idxs, 1):
        try:
            pred = predict_window(predictor, df, i, lookback, pred_len, samples)
        except Exception as e:
            print(f"  window {i}: {e}")
            continue
        anchor = float(df.loc[i - 1, "close"])
        pred_dir = np.sign(float(pred["close"].iloc[-1]) - anchor)
        real_end = float(df.loc[i + pred_len - 1, "close"])
        real_dir = np.sign(real_end - anchor)
        if pred_dir != 0 and real_dir != 0:
            total += 1
            hits += int(pred_dir == real_dir)
            moves.append(abs(real_end - anchor))
        if n % 10 == 0 or n == len(idxs):
            acc = hits / total * 100 if total else float("nan")
            print(f"  [{n}/{len(idxs)}] directional accuracy: {acc:.1f}% ({hits}/{total})")
    if total:
        acc = hits / total * 100
        print("\n=== KRONOS VALIDATION RESULT ===")
        print(f"Windows scored      : {total}")
        print(f"Directional accuracy: {acc:.2f}%  (50% = no edge)")
        print(f"Median move size    : {np.median(moves):.2f}")
        print("\nINTERPRETATION")
        if acc < 52:
            print("  ~coin flip. A model trained on 45 exchanges finds no")
            print("  directional structure at this timeframe/horizon. Stop")
            print("  tuning entry logic here; change timeframe or horizon.")
        elif acc < 55:
            print("  marginal. Real but thin -- likely eaten by spread+")
            print("  commission at 5m. Retest on a higher timeframe.")
        else:
            print("  material edge present. Worth using as a Pine signal")
            print("  filter (mode=filter) and re-running the strategy.")
    else:
        print("No scoreable windows.")


def mode_filter(predictor, df, lookback, pred_len, samples):
    """Current-bar bias: what does Kronos expect next? Use to gate signals."""
    import numpy as np
    i = len(df) - pred_len
    pred = predict_window(predictor, df, i, lookback, pred_len, samples)
    anchor = float(df.loc[i - 1, "close"])
    closes = pred["close"].values
    end = float(closes[-1])
    print("=== KRONOS BIAS ===")
    print(f"Anchor close   : {anchor:.2f}")
    print(f"Predicted close: {end:.2f}  ({end - anchor:+.2f})")
    print(f"Predicted high : {float(pred['high'].max()):.2f}")
    print(f"Predicted low  : {float(pred['low'].min()):.2f}")
    bias = "LONG" if end > anchor else "SHORT" if end < anchor else "FLAT"
    print(f"BIAS           : {bias}")
    print("\nUse: allow only Pine signals matching this bias; the")
    print("predicted high/low is a data-driven TP/SL envelope to compare")
    print("against the key-level targets.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--mode", choices=["validate", "filter"], default="validate")
    ap.add_argument("--model-dir", default=None, help="local weights dir (bypasses HuggingFace)")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--lookback", type=int, default=400)
    ap.add_argument("--pred-len", type=int, default=12, help="bars ahead (12 = 1h on 5m)")
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--step", type=int, default=24, help="walk-forward stride")
    ap.add_argument("--limit", type=int, default=100, help="max windows (0 = all)")
    a = ap.parse_args()

    df = load_csv(a.csv)
    print(f"Loaded {len(df)} bars: {df['timestamps'].iloc[0]} -> {df['timestamps'].iloc[-1]}")
    if len(df) < a.lookback + a.pred_len + 1:
        raise SystemExit(f"Need >= {a.lookback + a.pred_len + 1} bars, have {len(df)}")

    predictor = load_predictor(model_dir=a.model_dir, device=a.device,
                               max_context=max(512, a.lookback))
    if a.mode == "validate":
        mode_validate(predictor, df, a.lookback, a.pred_len, a.samples, a.step, a.limit)
    else:
        mode_filter(predictor, df, a.lookback, a.pred_len, a.samples)


if __name__ == "__main__":
    main()
