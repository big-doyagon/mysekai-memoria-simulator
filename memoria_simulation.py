#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""メモリアシミュレーター - プロジェクトセカイのメモリアドロップ確率をシミュレーション"""

import random
from typing import Dict, List, Set, Tuple, Optional, Union
import matplotlib.pyplot as plt
import numpy as np


class MemoriaSimulator:
    """メモリアシミュレーションのためのクラス
    
    プロセカのメモリア獲得確率をシミュレートするためのクラスで、
    ゲートレベルに応じた確率表の生成、1日のシミュレーション、複数日のシミュレーション、
    期待値の計算などの機能を提供します。
    """
    
    def __init__(self):
        """確率表を初期化してシミュレーターを準備"""
        self.prob_table = self._build_prob_table()

    def _build_prob_table(self) -> Dict[int, Dict[int, float]]:
        """ゲートレベルに応じた確率表を生成
        
        Returns:
            Dict[int, Dict[int, float]]: {ゲートレベル: {来場人数: 確率}}
        """
        tbl = {}
        for lv in range(1, 41):
            if lv <= 30:
                p2, p3, p4, p5 = 60 - 2*lv, 30, 10 + lv, lv
            else:
                delta = lv - 30
                p2, p3, p4, p5 = 0, 30 - delta, 40, 30 + delta
            tbl[lv] = {2: p2/100, 3: p3/100, 4: p4/100, 5: p5/100}
        return tbl

    def draw_visitors(self, level: int) -> int:
        """1セッション（5時 or 17時）の来場人数をサンプリング
        
        Args:
            level (int): ゲートレベル (1-40)
            
        Returns:
            int: 来場人数 (2-5)
        """
        r = random.random()
        acc = 0.0
        for k, p in self.prob_table[level].items():
            acc += p
            if r < acc:
                return k
        return 5  # 万一のフォールバック

    def simulate_one_day(self, level: int, unit_size: int, invited: bool) -> int:
        """1日のメモリア獲得数を計算
        
        Args:
            level (int): ゲートレベル (1-40)
            unit_size (int): ユニット人数
            invited (bool): 招待状を使用するか
            
        Returns:
            int: 1日のメモリア獲得数
        """
        chars = list(range(unit_size))
        invited_char = 0 if invited else None

        # 午前・午後 2 回の抽選
        sessions = [set(random.sample(chars, self.draw_visitors(level))) for _ in range(2)]
        unique_today = set.union(*sessions)
        gain = len(unique_today)

        # 招待中キャラが来ていれば +1
        if invited_char is not None and invited_char in unique_today:
            gain += 1
        return gain

    def run_simulations(self, n_runs: int, n_days: int, level: int, unit_size: int, invited: bool) -> List[int]:
        """N日×複数試行の累計メモリアをシミュレーション
        
        Args:
            n_runs (int): シミュレーション試行回数
            n_days (int): シミュレーション日数
            level (int): ゲートレベル (1-40)
            unit_size (int): ユニット人数
            invited (bool): 招待状を使用するか
            
        Returns:
            List[int]: 各試行の累計メモリア獲得数のリスト
        """
        totals = []
        for _ in range(n_runs):
            total = sum(self.simulate_one_day(level, unit_size, invited) for _ in range(n_days))
            totals.append(total)
        return totals

    def expected_daily_memoria(self, level: int, unit_size: int, invited: bool = False) -> float:
        """1日あたり期待値の解析計算
        
        Args:
            level (int): ゲートレベル (1-40)
            unit_size (int): ユニット人数
            invited (bool, optional): 招待状を使用するか. Defaults to False.
            
        Returns:
            float: 1日あたりの期待メモリア獲得数
        """
        probs = self.prob_table[level]
        M = unit_size
        e_unique = 0.0
        p_inv = 0.0
        for k1, p1 in probs.items():
            for k2, p2 in probs.items():
                p = p1 * p2
                q_not = (M - k1) / M * (M - k2) / M
                p_appear = 1 - q_not
                e_unique += M * p_appear * p
                p_inv += p_appear * p
        return e_unique + (p_inv if invited else 0.0)


class MemoriaResultVisualizer:
    """メモリアシミュレーション結果の表示クラス
    
    シミュレーション結果の表示と可視化を行うためのクラスです。
    """
    
    @staticmethod
    def print_results(n_days: int, theoretical: float, actual: List[int]) -> None:
        """シミュレーション結果を標準出力に表示
        
        Args:
            n_days (int): シミュレーション日数
            theoretical (float): 理論値
            actual (List[int]): 実際のシミュレーション結果
        """
        mean_val = np.mean(actual)
        std_val = np.std(actual)
        
        print(f"理論値（{n_days}日累計）: {theoretical:.2f}")
        print(f"シミュレーション平均    : {mean_val:.2f}")
        print(f"シミュレーション標準偏差: {std_val:.2f}")
    
    @staticmethod
    def plot_results(n_days: int, level: int, invited: bool, n_runs: int, 
                    theoretical: float, actual: List[int]) -> None:
        """シミュレーション結果をヒストグラムでプロット
        
        Args:
            n_days (int): シミュレーション日数
            level (int): ゲートレベル
            invited (bool): 招待状を使用したか
            n_runs (int): シミュレーション実行回数
            theoretical (float): 理論値
            actual (List[int]): 実際のシミュレーション結果
        """
        plt.figure(figsize=(8, 5))
        plt.hist(actual, bins=30, edgecolor='black', alpha=0.7)
        plt.axvline(
            theoretical,
            color='red',
            linestyle='--',
            linewidth=2,
            label=f'Theoretical total: {theoretical:.1f}'
        )
        plt.title(f'Distribution of cumulative memoria after {n_days} days\n'
                f'Level {level}, Invited={invited}, Runs={n_runs}')
        plt.xlabel('Cumulative Memoria')
        plt.ylabel('Frequency')
        plt.legend()
        plt.tight_layout()
        plt.show()


def run_simulation_with_params(gate_level: int = 10, unit_size: int = 6, n_days: int = 30, 
                             invited: bool = True, n_runs: int = 10000, 
                             show_plot: bool = True) -> Tuple[float, List[int]]:
    """指定パラメータでシミュレーションを実行
    
    Args:
        gate_level (int, optional): ゲートレベル. Defaults to 10.
        unit_size (int, optional): ユニット人数. Defaults to 6.
        n_days (int, optional): シミュレーション日数. Defaults to 30.
        invited (bool, optional): 招待状を使用するか. Defaults to True.
        n_runs (int, optional): シミュレーション試行回数. Defaults to 10000.
        show_plot (bool, optional): 結果をプロットするか. Defaults to True.
        
    Returns:
        Tuple[float, List[int]]: (理論値, シミュレーション結果リスト)
    """
    simulator = MemoriaSimulator()
    visualizer = MemoriaResultVisualizer()
    
    # 理論値計算
    daily_exp = simulator.expected_daily_memoria(gate_level, unit_size, invited)
    theoretical_total = daily_exp * n_days
    
    # シミュレーション実行
    totals = simulator.run_simulations(n_runs, n_days, gate_level, unit_size, invited)
    
    # 結果表示
    visualizer.print_results(n_days, theoretical_total, totals)
    
    # グラフ表示（オプション）
    if show_plot:
        visualizer.plot_results(n_days, gate_level, invited, n_runs, theoretical_total, totals)
    
    return theoretical_total, totals


# ------------------------------------------------------------
# メイン実行部
# ------------------------------------------------------------
if __name__ == "__main__":
    # ── パラメータ ──
    GATE_LEVEL = 10     # ゲートレベル (1–40)
    UNIT_SIZE  = 6      # ユニット人数
    N_DAYS     = 30     # シミュレーション日数
    INVITED    = True   # 招待状を常時使うか
    N_RUNS     = 1000  # モンテカルロ試行回数
    
    # シミュレーション実行
    run_simulation_with_params(
        gate_level=GATE_LEVEL,
        unit_size=UNIT_SIZE,
        n_days=N_DAYS,
        invited=INVITED,
        n_runs=N_RUNS,
        show_plot=True
    )
