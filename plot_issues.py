#!/usr/bin/env python3
import json, datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

_RESAMPLE, _ROLLWIN = 7, 60
CUTOFF_DATE = dt.datetime.fromisoformat("2019-01-01 00:00:00+00:00")

with open("issues.json") as f:
    data = json.load(f)

opened = [
    date for e in data
    if e.get("created_at")
    if (date := dt.datetime.fromisoformat(e["created_at"])) > CUTOFF_DATE
]
closed = [
    date for e in data
    if e.get("closed_at")
    if (date := dt.datetime.fromisoformat(e["closed_at"])) > CUTOFF_DATE
]

open_daily  = pd.Series(opened).dt.floor("D").value_counts().sort_index()
close_daily = pd.Series(closed).dt.floor("D").value_counts().sort_index()

start = min(open_daily.index.min(), close_daily.index.min())
end   = max(open_daily.index.max(), close_daily.index.max())
idx = pd.date_range(start, end, freq="D")
daily = pd.DataFrame({
    "opened": open_daily.reindex(idx, fill_value=0),
    "closed": close_daily.reindex(idx, fill_value=0),
})

daily["net"] = daily["opened"] - daily["closed"]
daily["backlog"] = daily["opened"].cumsum() - daily["closed"].cumsum()

RESAMPLE = f"{_RESAMPLE}D"
ROLLWIN  = f"{_ROLLWIN}D"
smooth = daily[["opened","closed"]].rolling(ROLLWIN).sum()/_ROLLWIN
agg    = daily[["opened","closed"]].resample(RESAMPLE).sum()/_RESAMPLE



fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10,7), sharex=True)

# activity (resampled + smoothed overlay)
ax1.plot(agg.index,    agg["opened"],  label=f"Opened/{RESAMPLE}", alpha=0.6, linestyle="--")
ax1.plot(agg.index,    agg["closed"],  label=f"Closed/{RESAMPLE}", alpha=0.6, linestyle="--")
ax1.plot(smooth.index, smooth["opened"],  label=f"Opened ({ROLLWIN} rolling)")
ax1.plot(smooth.index, smooth["closed"],  label=f"Closed ({ROLLWIN} rolling)")
ax1.set_ylabel("Count / period")
ax1.legend()

# cumulative backlog
ax2.plot(daily.index, daily["backlog"], label="Backlog (cum open − cum closed)")
ax2.axhline(0, linestyle="--", alpha=0.5)
ax2.set_ylabel("Open issues total")
ax2.legend()

major = mdates.YearLocator()
minor = mdates.MonthLocator()
for ax in (ax1, ax2):
    ax.xaxis.set_major_locator(major)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(minor)

    ax.grid(True, which="major", axis="x", alpha=0.6)
    ax.grid(True, which="minor", axis="x", linestyle=":", alpha=0.3)

plt.tight_layout()
plt.show()

