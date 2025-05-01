#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
memoria_calc.py
招待状の有無によるメモリア期待値とシミュレーション

使い方（スクリプト先頭のパラメータを書き換えて実行）:
    python memoria_calc.py
"""

from __future__ import annotations
import random
import itertools
from typing import Dict, Tuple, List

import numpy as np
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────
# 0. ゲートレベル → {来場人数: 確率} のテーブル
# ──────────────────────────────────────────────────────────
def build_prob_table() -> Dict[int, Dict[int, float]]:
    tbl: Dict[int, Dict[int, float]] = {}
    for lv in range(1, 41):
        if lv <= 30:
            p2, p3, p4, p5 = 60 - 2 * lv, 30, 10 + lv, lv
        else:
            d = lv - 30
            p2, p3, p4, p5 = 0, 30 - d, 40, 30 + d
        tbl[lv] = {2: p2 / 100, 3: p3 / 100, 4: p4 / 100, 5: p5 / 100}
    return tbl


PROB_TABLE = build_prob_table()

# ──────────────────────────────────────────────────────────
# 1. 解析的期待値
# ──────────────────────────────────────────────────────────
def daily_expectation(
    level: int,
    unit_size: int,
    invited: bool = False,
) -> Tuple[float, Dict[str, float]]:
    """
    level      : ゲートレベル (1–40)
    unit_size  : ユニットのキャラクター人数
    invited    : 招待状を常時使用するか

    戻り値
    -------
    total_exp  : 1 日あたり総獲得メモリア期待値
    per_char   : {キャラ種別: 期待値} の辞書
                 invited が False の場合 -> {'all': μ}
                 invited が True  の場合 -> {'invited': 2, 'others': μ}
    """
    probs = PROB_TABLE[level]

    if not invited:
        # 任意キャラが 1 日に少なくとも 1 回来る確率
        per_char = sum(
            p1 * p2 * (1 - ((unit_size - k1) / unit_size) * ((unit_size - k2) / unit_size))
            for k1, p1 in probs.items()
            for k2, p2 in probs.items()
        )
        total = unit_size * per_char
        return total, {"all": per_char}

    # ── 招待状あり ──────────────────────────────
    invited_gain = 2.0  # 1 日 2 個確定

    per_other = sum(
        p1
        * p2
        * (
            1
            - ((unit_size - k1) / (unit_size - 1))
            * ((unit_size - k2) / (unit_size - 1))
        )
        for k1, p1 in probs.items()
        for k2, p2 in probs.items()
    )
    total = invited_gain + (unit_size - 1) * per_other
    return total, {"invited": invited_gain, "others": per_other}


def expectation_after_days(
    days: int,
    level: int,
    unit_size: int,
    invited: bool = False,
) -> Tuple[float, Dict[str, float]]:
    """
    指定日数後の累計期待値を返す（招待キャラを固定している前提。
    72 時間ルール等は無視）
    """
    daily_total, per_char = daily_expectation(level, unit_size, invited)
    total_after = daily_total * days
    per_char_after = {k: v * days for k, v in per_char.items()}
    return total_after, per_char_after


# ──────────────────────────────────────────────────────────
# 2. シミュレーション（オプション）
# ──────────────────────────────────────────────────────────
def _draw_k(level: int) -> int:
    r = random.random()
    acc = 0.0
    for k, p in PROB_TABLE[level].items():
        acc += p
        if r < acc:
            return k
    return 5  # fallback


def simulate_one_day(level: int, unit_size: int, invited: bool) -> Tuple[int, List[int]]:
    """
    1 日シミュレーション
    戻り値:
        total_gain … その日の総メモリア
        gains_by_id … 各キャラごとのメモリア (長さ unit_size)
    """
    characters = list(range(unit_size))
    invited_id = 0 if invited else None

    gains = [0] * unit_size

    # 午前・午後の 2 セッション
    for _ in range(2):
        k_total = _draw_k(level)

        if invited_id is not None:
            gains[invited_id] = 2  # 日ごとに上書きしても OK（1 日 2 個確定）
            remaining_slots = k_total - 1
            pool = [c for c in characters if c != invited_id]
        else:
            remaining_slots = k_total
            pool = characters

        if remaining_slots > 0:
            visitors = random.sample(pool, remaining_slots)
            for vid in visitors:
                gains[vid] = 1  # 複数回来ても 1 日 1 個

    total_gain = sum(gains)
    return total_gain, gains


def run_simulations(
    runs: int,
    days: int,
    level: int,
    unit_size: int,
    invited: bool = False,
) -> List[int]:
    """
    returns: 各 run の累計メモリア
    """
    totals = []
    for _ in range(runs):
        total = 0
        for _ in range(days):
            g, _ = simulate_one_day(level, unit_size, invited)
            total += g
        totals.append(total)
    return totals


def plot_distribution(
    totals: List[int],
    theoretical_total: float,
    title: str,
    bins: int = 30,
) -> None:
    plt.figure(figsize=(8, 5))
    
    # 整数値データに適したビン設定
    min_val, max_val = min(totals), max(totals)
    # 整数の範囲を使用してビンを設定
    bins_range = np.arange(min_val, max_val + 2) - 0.5  # 各整数値の中心にビンを配置
    
    plt.hist(totals, bins=bins_range, edgecolor="black", alpha=0.7)
    plt.axvline(
        theoretical_total,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Theoretical: {theoretical_total:.1f}"
    )
    plt.title(title, fontsize=14)
    plt.xlabel("Total Memoria", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()


# ──────────────────────────────────────────────────────────
# 3. 動作サンプル  (ここを書き換えて実行)
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    # ===== パラメータ設定 =====
    GATE_LEVEL = 32       # ゲートレベル
    UNIT_SIZE  = 6        # ユニット人数
    INVITED    = True     # 招待状を使うか
    DAYS       = 30       # 期待値／シミュレーション日数
    RUNS       = 1000        # モンテカルロ試行回数
    # =========================

    # 期待値計算
    daily_total, daily_per = daily_expectation(GATE_LEVEL, UNIT_SIZE, INVITED)
    cum_total, cum_per = expectation_after_days(
        DAYS, GATE_LEVEL, UNIT_SIZE, INVITED
    )

    print("● 解析的期待値")
    print(f"  1日あたり総メモリア期待値 : {daily_total:.3f}")
    print(f"  1日あたりキャラ別期待値   : {daily_per}")
    print(f"  {DAYS}日後累計期待値       : {cum_total:.3f}")
    print(f"  {DAYS}日後キャラ別累計期待値: {cum_per}")

    # シミュレーション（必要ない場合はRUNS=0にしてください）
    if RUNS > 0:
        totals = run_simulations(RUNS, DAYS, GATE_LEVEL, UNIT_SIZE, INVITED)
        mean_val, std_val = np.mean(totals), np.std(totals)
        print("\n● シミュレーション結果")
        print(f"  平均={mean_val:.3f},  標準偏差={std_val:.3f}")

        plot_distribution(
            totals,
            theoretical_total=cum_total,
            title=f"{DAYS}-Day Total Memoria Distribution\n"
                  f"Gate Level {GATE_LEVEL}, Invited={INVITED}, Runs={RUNS}"
        )
