# mysekai-memoria-simulator

## 概要
ゲートレベル、ユニット人数、招待キャラの有無に応じた
メモリアドロップ数をシミュレーションします。

## 機能
- ゲートレベル1〜40の確率表自動生成
- モンテカルロ法による1日／複数日シミュレーション
- 理論的期待値（1日あたり、累計）の計算
- ヒストグラムによる実測値と理論値の可視化

## 動作環境
- Python 3.8以上
- numpy
- matplotlib

## インストール
```bash
pip install numpy matplotlib
```

## 使用方法
1. `memoria_simulation.py` の `__main__` ブロックでパラメータを設定:
   ```python
   GATE_LEVEL = 10    # ゲートレベル (1–40)
   UNIT_SIZE = 6      # ユニット人数
   DAYS = 30          # 期待値／シミュレーション日数
   INVITED = True     # 招待状を使用するか
   RUNS = 10000       # モンテカルロ試行回数（0でシミュレーションなし）
   ```
2. 以下を実行:
   ```bash
   python memoria_simulation.py
   ```
3. 別スクリプトから呼び出し:
   ```python
   from memoria_simulation import daily_expectation, expectation_after_days, run_simulations

   # 解析的期待値
   daily_total, daily_per = daily_expectation(
       level=10, unit_size=6, invited=True
   )
   cum_total, cum_per = expectation_after_days(
       days=30, level=10, unit_size=6, invited=True
   )

   # シミュレーション
   totals = run_simulations(
       runs=10000, days=30, level=10, unit_size=6, invited=True
   )
   ```
