# Lighthouse mobile median — web-studiya/index-clean.html

URL: `http://127.0.0.1:8767/web-studiya/index-clean.html`

Tool: lighthouse@11, form-factor=mobile, throttling-method=simulate, 3 runs.

Note: each run exited non-zero due to Windows EBUSY on Chrome profile cleanup after report write; JSON reports were produced.

## Median summary

| Metric | Median |
| --- | ---: |
| Performance score | **29** |
| First Contentful Paint | 4.5 s |
| Largest Contentful Paint | 6.9 s |
| Speed Index | 11.4 s |
| Total Blocking Time | 14.5 s |
| Cumulative Layout Shift | 0.026 |
| Time to Interactive | 22.7 s |
| Network requests (count) | 49 |
| Total byte weight | 932.1 KiB |
| CSS transfer (resource-summary) | 75.3 KiB |
| JS transfer (resource-summary) | 129.9 KiB |
| DOM size (elements) | 413 |

## Per-run raw

| Run | Score | FCP (ms) | LCP (ms) | SI (ms) | TBT (ms) | CLS | TTI (ms) | Reqs | Total bytes | CSS | JS | DOM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 32 | 3320 | 6687 | 9880 | 16331 | 0.003 | 22677 | 50 | 959355 | 77113 | 135246 | 413 |
| 2 | 25 | 7782 | 10309 | 17218 | 13899 | 0.026 | 27050 | 49 | 954421 | 77113 | 132976 | 413 |
| 3 | 29 | 4471 | 6854 | 11443 | 14459 | 0.026 | 21581 | 49 | 954386 | 77113 | 133007 | 413 |

## DOM size details (score-median run 3)

```json
{
  "type": "table",
  "headings": [
    {
      "key": "statistic",
      "valueType": "text",
      "label": "Statistic"
    },
    {
      "key": "node",
      "valueType": "node",
      "label": "Element"
    },
    {
      "key": "value",
      "valueType": "numeric",
      "label": "Value"
    }
  ],
  "items": [
    {
      "statistic": "Total DOM Elements",
      "value": {
        "type": "numeric",
        "granularity": 1,
        "value": 413
      }
    },
    {
      "node": {
        "type": "node",
        "lhId": "1-0-SPAN",
        "path": "1,HTML,1,BODY,3,MAIN,3,SECTION,0,DIV,1,DIV,0,DIV,2,DIV,2,FORM,0,DIV,0,LABEL,1,SPAN",
        "selector": "form#rk-form-studio-contacts > div.rk-field > label > span.rk-req",
        "boundingRect": {
          "top": 6463,
          "bottom": 6481,
          "left": 70,
          "right": 75,
          "width": 5,
          "height": 18
        },
        "snippet": "<span class=\"rk-req\" aria-hidden=\"true\">",
        "nodeLabel": "*"
      },
      "statistic": "Maximum DOM Depth",
      "value": {
        "type": "numeric",
        "granularity": 1,
        "value": 11
      }
    },
    {
      "node": {
        "type": "node",
        "lhId": "1-1-DIV",
        "path": "1,HTML,1,BODY,3,MAIN,2,SECTION,0,DIV,1,DIV",
        "selector": "main#main > section#cities > div.rk-container > div.rk-cities__grid",
        "boundingRect": {
          "top": 3888,
          "bottom": 6084,
          "left": 16,
          "right": 396,
          "width": 380,
          "height": 2197
        },
        "snippet": "<div class=\"rk-cities__grid\">",
        "nodeLabel": "Веб-студия в Астане\nВеб-студия в Алматы\nВеб-студия в Шымкенте\nВеб-студия в Акта…"
      },
      "statistic": "Maximum Child Elements",
      "value": {
        "type": "numeric",
        "granularity": 1,
        "value": 18
      }
    }
  ]
}
```

## Resource summary items (run 3)

```json
[
  {
    "resourceType": "total",
    "label": "Total",
    "requestCount": 48,
    "transferSize": 945610
  },
  {
    "resourceType": "image",
    "label": "Image",
    "requestCount": 30,
    "transferSize": 378609
  },
  {
    "resourceType": "font",
    "label": "Font",
    "requestCount": 5,
    "transferSize": 300793
  },
  {
    "resourceType": "script",
    "label": "Script",
    "requestCount": 4,
    "transferSize": 133007
  },
  {
    "resourceType": "stylesheet",
    "label": "Stylesheet",
    "requestCount": 4,
    "transferSize": 77113
  },
  {
    "resourceType": "document",
    "label": "Document",
    "requestCount": 1,
    "transferSize": 50524
  },
  {
    "resourceType": "other",
    "label": "Other",
    "requestCount": 4,
    "transferSize": 5564
  },
  {
    "resourceType": "media",
    "label": "Media",
    "requestCount": 0,
    "transferSize": 0
  },
  {
    "resourceType": "third-party",
    "label": "Third-party",
    "requestCount": 8,
    "transferSize": 113916
  }
]
```

