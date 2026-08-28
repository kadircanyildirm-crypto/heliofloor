---
license: cc-by-4.0
tags:
- flare
- space-weather
- GOES-flare
- binary-classification
- forecasting
configs:
- config_name: default
  default: true
  data_files:
  - split: train
    path: train.csv
  - split: validation
    path: validation.csv
  - split: test
    path: test.csv
  - split: leaky_validation
    path: leaky_validation.csv
---

# Full-disk Solar Flare Forecasting Dataset

## Dataset Summary

This dataset provides labels for solar flare forecasting derived from NOAA GOES flare events from May 2010 to December 2024. Labels are constructed using a 24h rolling prediction window sampled at an hourly cadence. Each window is annotated with both **max GOES class** (based on peak X-ray flux) and **cumulative flare index**.  

Two derived binary labels are included for forecasting tasks:  

- **`label_max`**: 1 if the maximum flare intensity in the window is ≥ M1.0.  
- **`label_cum`**: 1 if the cumulative flare intensity in the window is ≥ 10.  

For completeness, we also include (1) max GOES class, which is determined from the peak X-ray flux of the most intense flare in the prediction window; and (2) cumulative index determined from all ≥C-class flares in the prediction window.


## Supported Tasks and Applications

- `binary-classification`: Predict whether a time window will contain significant flaring activity.  
`ordinal-classification`: Predict flare-class of a given instance.  
- `regression`: Predict cumulative flare index of a given instance.  


## Dataset Structure

### Data Files

- `train.csv`: Instances from Feb 15 to Dec 31 in each year between 2010–2019  
- `validation.csv`: Instances from Jan 15–31 of each year between 2010–2019  
- `test.csv`: All instances from each year between 2020–2024  
- `leaky_validation.csv`: Instances from Jan 1–14 and Feb 1-14 of each year between 2010–2019

### Features

Each record includes four label fields:  
- **`max_goes_class`**: Maximum GOES flare class (e.g., C5.2, M1.0, X3.2) in the prediction window, or `FQ` if no flares are present.  
- **`cumulative_index`**: Weighted sum of flare subclasses ≥C-class in the prediction window.  
  - C-class contributes weight ×1, M-class ×10, X-class ×100.  
  - For example, an M2.0 flare adds 20, while an X3.5 flare adds 350.  
- **`label_max`**: Binary label, 1 if `goes_class` ≥ M1.0, else 0.  
- **`label_cum`**: Binary label, 1 if `cumulative_index` ≥ 10, else 0.  

Example entry (in JSON format):  

```json
{
  "timestamp": "2011-02-14 03:00:00",
  "goes_class": "X2.2",
  "cumulative_index": 297.1,
  "label_max": 1,
  "label_cum": 1
}
```

## Dataset Details

| Field | Description |
|------------------------|---------------------------------------------|
| **Temporal Coverage** | May 13, 2010 – Dec 31, 2024 |
| **Data Format** | CSV (.csv), string-based schema |
| **Data Shape** | (1, 4) per instance |
| **Data Size** | Total 128,328 instances |
| **Cadence** | 1 hour |
| **Total File Size** | ~4.4MB |

## License
This dataset is licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0) License.

## Authors
- Jinsu Hong, [jhong36@gsu.edu](mailto:jhong36@gsu.edu)
- Kang Yang, [kyang30@gsu.edu](mailto:kyang30@gsu.edu)
- Berkay Aydin, [baydin2@gsu.edu](mailto:baydin2@gsu.edu)