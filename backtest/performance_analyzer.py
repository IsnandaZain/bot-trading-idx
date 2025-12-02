import pandas as pd


def generate_performance_report(trades_list):
    """Buat laporan kinerja dari semua trade"""
    df = pd.DataFrame(trades_list)
    df.to_csv("backtest_report.csv", index=False)

    if df.empty:
        print("Tidak ada trade untuk dianalisis.")
        return
    
    total_trades = len(df)
    winning_trades = len(df[df['pnl'] > 0])
    winning_rate = (winning_trades / total_trades) * 100
    total_pnl = df["pnl"].sum()
    avg_pnl = df["pnl"].mean()
    
    print("📈 **LAPORAN BACKTEST**")
    print(f"Total Trades: {total_trades}")
    print(f"Winning Rate: {winning_rate:.2f}%")
    print(f"Total PnL: Rp {total_pnl:,.0f}")
    print(f"Average PnL per Trade: Rp {avg_pnl:,.0f}")
    print(f"\n📊 Breakdown Sinyal:")
    print(df.groupby('signal')['pnl'].agg(['count', 'mean', 'sum']).round())

    return df
