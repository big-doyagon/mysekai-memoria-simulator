import random
from collections import Counter
from typing import List, Tuple

# ------------------------------------------------------------
# 0. ゲートレベル → {人数: 確率} の辞書を作る
#    表の規則性:
#       1 ≤ L ≤ 30 : P(2)=60-2L, P(3)=30, P(4)=10+L, P(5)=L
#      31 ≤ L ≤ 40 : P(2)=0, P(3)=30-(L-30), P(4)=40, P(5)=30+(L-30)
# ------------------------------------------------------------
def build_prob_table() -> dict[int, dict[int, float]]:
    tbl = {}
    for lv in range(1, 41):
        if lv <= 30:
            p2, p3, p4, p5 = 60-2*lv, 30, 10+lv, lv
        else:
            delta = lv - 30
            p2, p3, p4, p5 = 0, 30-delta, 40, 30+delta
        tbl[lv] = {2: p2/100, 3: p3/100, 4: p4/100, 5: p5/100}
    return tbl

PROB_TABLE = build_prob_table()

# ------------------------------------------------------------
# 1. 1 日の期待値を解析計算
# ------------------------------------------------------------
def expected_daily_memoria(level: int,
                           unit_size: int,
                           invited: bool = False) -> float:
    """ゲートレベル level（1–40）, ユニットの人数 unit_size
       invited=True なら 1 人だけ招待中（重複ボーナス+1）"""
    probs = PROB_TABLE[level]
    M = unit_size

    e_unique = 0.0          # 一日あたり重複を除いた来場人数
    p_invited = 0.0         # 招待キャラが 1 回以上来る確率

    # 5時・17時の 2 回抽選するので (k1,k2) を全探索
    for k1, p1 in probs.items():
        for k2, p2 in probs.items():
            p = p1 * p2
            # 特定キャラが両方とも来ない確率
            q_not = (M - k1) / M * (M - k2) / M
            p_appear = 1.0 - q_not
            e_unique += M * p_appear * p
            p_invited += p_appear * p

    # 招待キャラは出現した日だけ +1 される
    return e_unique + (p_invited if invited else 0.0)

# ------------------------------------------------------------
# 2. N 日シミュレーション
# ------------------------------------------------------------
def _draw_k(level: int) -> int:
    """レベル level で 1 回（5時 or 17時）に来る人数 k を返す"""
    r = random.random()
    acc = 0.0
    for k, prob in PROB_TABLE[level].items():
        acc += prob
        if r < acc:
            return k
    return 5  # 端数誤差対策

def simulate_memoria(days: int,
                     level: int,
                     unit_size: int,
                     invited: bool = False,
                     seed: int | None = None) -> Tuple[List[int], List[int]]:
    """N 日間のモンテカルロ
       戻り値:
         daily  … 各日の獲得メモリア
         cum    … 日次累積
    """
    if seed is not None:
        random.seed(seed)

    characters = list(range(unit_size))        # 0～M-1 の ID
    invited_char = 0 if invited else None      # 単純化: 常にキャラ0 を招待中
    daily, cum = [], []
    total = 0

    for _ in range(days):
        # 5 時・17 時で集合を作る
        today_sets = []
        for _ in range(2):
            k = _draw_k(level)
            today_sets.append(set(random.sample(characters, k)))

        unique_today = set.union(*today_sets)
        gain = len(unique_today)

        # 招待キャラが来ていれば +1
        if invited_char is not None and invited_char in unique_today:
            gain += 1

        total += gain
        daily.append(gain)
        cum.append(total)

    return daily, cum

# ------------------------------------------------------------
# 3. 使い方例
# ------------------------------------------------------------
if __name__ == "__main__":
    LV, SIZE, DAYS = 30, 6, 30  # レベル30, ユニット6人, 30日
    print(f"理論期待値 (招待なし): {expected_daily_memoria(LV, SIZE):.3f}")
    print(f"理論期待値 (招待あり) : {expected_daily_memoria(LV, SIZE, True):.3f}")

    d, c = simulate_memoria(DAYS, LV, SIZE, invited=True, seed=42)
    print(f"\nシミュレーション ({DAYS} 日, 招待あり)")
    print(f"  平均={sum(d)/DAYS:.3f}, 合計={c[-1]}")
