#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
app.py
メモリア期待値計算のStreamlitアプリケーション

使い方:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
from memoria_simulation import (
    daily_expectation,
    expectation_after_days,
    PROB_TABLE,
)





def show_probability_table(level):
    """指定されたゲートレベルの確率テーブルを表示"""
    st.subheader(f"ゲートレベル {level} の確率分布")
    
    probs = PROB_TABLE[level]
    data = {
        "来場人数": list(probs.keys()),
        "確率 (%)": [p * 100 for p in probs.values()]
    }
    df = pd.DataFrame(data)
    st.table(df)


def main():
    st.set_page_config(
        page_title="メモリア期待値計算",
        page_icon="📊",
        layout="wide",
    )

    st.title("プロセカ メモリア期待値計算")
    st.markdown("""
    ゲートレベル、ユニット人数、招待状の有無に応じたメモリア期待値を計算するアプリです。
    """)

    # サイドバーにパラメータ設定
    st.sidebar.header("パラメータ設定")
    
    gate_level = st.sidebar.number_input(
        "ゲートレベル", 
        min_value=1, 
        max_value=40, 
        value=30,
        help="ゲートレベル (1-40)"
    )
    
    unit_size = st.sidebar.number_input(
        "ユニット人数", 
        min_value=5, 
        max_value=10, 
        value=6,
        help="キャラクターユニットの人数"
    )

    invited = st.sidebar.checkbox(
        "招待状を使用", 
        value=True,
        help="招待状キャラを固定するかどうか"
    )
    
    days = st.sidebar.number_input(
        "日数", 
        min_value=1, 
        max_value=365, 
        value=30,
        help="期待値計算期間（日）"
    )
    
    # サイドバーにボタンを追加
    # st.sidebar.divider()
    # st.sidebar.button("計算実行", type="primary")

    # 期待値計算
    daily_total, daily_per = daily_expectation(gate_level, unit_size, invited)
    cum_total, cum_per = expectation_after_days(days, gate_level, unit_size, invited)

    # メイン領域を二分割
    col1, col2 = st.columns(2)
    
    with col1:
        # 日ごとの期待値
        st.header("1日あたりの期待値")
        st.metric(
            label="総メモリア期待値", 
            value=f"{daily_total:.3f}"
        )
        
        # キャラ別期待値の表示
        if invited:
            st.markdown(f"**キャラ別期待値:**")
            st.markdown(f"- 招待キャラ: **{daily_per['invited']:.3f}** / 日")
            st.markdown(f"- その他キャラ: **{daily_per['others']:.3f}** / 日")
        else:
            st.markdown(f"**キャラ別期待値:** 全キャラ **{daily_per['all']:.3f}** / 日")
        
        # 確率テーブル表示
        st.divider()
        show_probability_table(gate_level)
    
    with col2:
        # 累計期待値
        st.header(f"{days}日後の累計期待値")
        st.metric(
            label=f"総メモリア期待値", 
            value=f"{cum_total:.3f}"
        )
        
        # キャラ別累計期待値の表示
        if invited:
            st.markdown(f"**キャラ別累計期待値:**")
            st.markdown(f"- 招待キャラ: **{cum_per['invited']:.3f}**")
            st.markdown(f"- その他キャラ: **{cum_per['others']:.3f}**")
        else:
            st.markdown(f"**キャラ別累計期待値:** 全キャラ **{cum_per['all']:.3f}**")


if __name__ == "__main__":
    main()
