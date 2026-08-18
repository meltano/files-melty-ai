# DatasetML

Reference for the dataset definition file (`analyze/datasets/*.yml`) used to create and format insights (charts, tables, metrics) in a Meltano Cloud workspace, including metadata, query, and visualisation configuration, with worked examples.

## Overview

Use the dataset YAML to create and format insights in your workspace as code. Dataset files are stored in YAML format.

### Example: `analyze/datasets/tap-google-analytics/google_analytics_daily_users_last_14_days.yml`

```yaml
version: datasets/v0.2
source: Google Analytics
title: "Google Analytics Daily Users Last 14 Days"
questions: 'How many users has there been over the last 14 days?'
description: |-
    Daily users over the last 14 days.

    #google-analytics
metadata: |-
    {
        "name": "google_analytics_locations",
        "label": "Daily Users",
        "related_table": {
        "columns": [
            {"name": "report_date", "label": "Date", "description": "Date"}
        ],
        "aggregates": [
            {"name": "total_users", "label": "Total Users", "description": "Total Users"}
        ]
        }
    }
visualisation: |-
    {"chartjs-chart": {"chartType": "bar"}}
query: |-
    SELECT
    report_date "google_analytics_locations.report_date"
    , sum(users) "google_analytics_locations.total_users"
    FROM google_analytics_locations
    WHERE report_date >= current_date - interval '14' day
    AND report_date < current_date
    GROUP BY report_date
    ORDER BY report_date
```

### Key Information

| Path | JSON Type | Description |
|---|---|---|
| `version` | `string` | The version determines how the CLI handles publishing the dataset. |
| `source` | `string` | A channel name to be used to group related datasets in your workspace. |
| `title` | `string` | The title at the top of the insight. |
| `questions` | `string` | Questions that your dataset answers, so people can find the dataset just by asking questions. |
| `description` | `string` | Information about what the dataset is, how it's being filtered or displayed, and other relevant information. You can also add `#tags`. |
| `metadata` | `string` of JSON | Details about how the dataset's chart is laid out. See Metadata below. |
| `visualisation` | `string` of JSON | Details about the precise visualisation of the dataset's chart. See Visualisation below. |
| `query` | `string` of SQL | The query that returns the data from your datastore for use in the dataset's chart and related table. See Query below. |
| `rawData` | `string` of a List | The `rawData` key allows you to hard-code data directly into your dataset. |

### String Formatting

You may use any of the following string formats:

```yaml
title: Google Analytics Daily Users Last 14 Days

title: 'Google Analytics Daily Users Last 14 Days'

title: "Google Analytics Daily Users Last 14 Days"

title: |-
    Google Analytics Daily Users Last 14 Days
    Multi-line string, remember to indent
```

The multiline string is generally the best way to display the `string` of JSON or SQL.

### Further Reading (Overview)

- API Datasets: `/reference/cloud/api/resources/datasets`
- Example Charts: see Examples sections below

---

## Metadata

You can change the format and display of your chart by using the `metadata` key of the dataset YAML file. The `metadata` key relates to how the data from the `query` within the dataset is displayed as an insight.

### Example

```yaml
metadata: |-
    {
        "name": "google_analytics_locations",
        "label": "Daily Users",
        "related_table": {
            "columns": [
                {
                    "name": "report_date",
                    "label": "Date",
                    "description": "Date"
                }
            ],
            "aggregates": [
                {
                    "name": "total_users",
                    "label": "Total Users",
                    "description": "Total Users"
                }
            ]
        }
    }
```

### Metadata Keys

| Metadata Key | Details |
|---|---|
| `name` | Name of the SQL table you are querying, or its alias if assigned. |
| `label` | Chart label. |
| `related_table` | Columns and aggregates to display in the chart. |
| `columns` | x-axis categories, usually dates or groups. |
| `aggregates` | Bars, points, lines that show the information over the `columns` categories. |
| `links` | Can be defined to connect datasets or external links, either by clicking on specific aggregates, or defining a link globally. |

### Post-Processing

`columns` and `aggregates` support post-processing to modify values before they are rendered by the visualisation. This can be supplied in one of two ways:

- A named post-processor: `post_process`
- An expression: `post_process_expr`

When both `post_process` and `post_process_expr` are supplied for a single column or aggregate, `post_process_expr` takes precedence.

#### Named Post-Processors

Named post-processors are aliases for common processing methods. A named post-processor can be specified using `post_process`.

| Name | Description |
|---|---|
| `json_parse` | Parse a JSON string. |

```yaml
metadata: |-
    {
        "name": "test_failures",
        "label": "Test failures",
        "related_table": {
            "columns": [
                {
                    "name": "rows_json",
                    "label": "Rows JSON",
                    "post_process": "json_parse"
                }
            ]
        }
    }
```

#### Expressions

Expressions can be used to modify values with a JavaScript function that accepts a single argument as the value and returns the processed value. This function can be named (e.g. `JSON.parse`) or anonymous (e.g. `value => value.toUpperCase()`). An expression can be specified using `post_process_expr`.

```yaml
metadata: |-
    {
        "name": "test_failures",
        "label": "Test failures",
        "related_table": {
            "columns": [
                {
                    "name": "rows_json",
                    "label": "Rows JSON",
                    "post_process_expr": "JSON.parse"
                }
            ]
        }
    }
```

### Examples of Links

#### Global Link Example (Dataset)

With a global link, if you click on any of the data in the visualisation you have the option of viewing what is linked. You can use a global link to drill down to another dataset, or link to an external source.

```yaml
metadata: |-
    {
        "name": "google_analytics_locations",
        "label": "Daily Users",
        "related_table": {
        "columns": [
            {"name": "report_date", "label": "Date", "description": "Date"}
        ],
        "aggregates": [
            {"name": "total_users", "label": "Total Users", "description": "Total Users"}
        ]
        },
        "links": [{"dataset": "another_datasets_file_name_without_file_extension"}]
    }
```

#### Aggregate Link Example (External Link)

With an aggregate link, if you click on the specific aggregate data in the visualisation you have the option of viewing what is linked. You can use an aggregate link to drill down to another dataset, or link to an external source.

```yaml
metadata: |-
    {
        "name": "google_analytics_locations",
        "label": "Daily Users",
        "related_table": {
        "columns": [
            {"name": "report_date", "label": "Date", "description": "Date"}
        ],
        "aggregates": [
            {"name": "total_users", "label": "Total Users", "description": "Total Users", "links": [
                    {"href": "https://developers.google.com/analytics", "target": "_blank"}]
            }
        ]
        }
    }
```

### Further Reading (Metadata)

- API Datasets: `/reference/cloud/api/resources/datasets`
- Example Charts: see Basic Examples below

---

## Query

You select the data for your chart by using the `query` key of the dataset YAML file. The `query` key in the dataset file is the SQL query that is run against your chosen data store to retrieve data for use in displaying the insight.

You use the `metadata` key to format how you are displaying the returned information.

### Example

```yaml
query: |-
    SELECT
    report_date "google_analytics_locations.report_date"
    , sum(users) "google_analytics_locations.total_users"
    FROM google_analytics_locations
    WHERE report_date >= current_date - interval '14' day
    AND report_date < current_date
    GROUP BY report_date
    ORDER BY report_date
```

### Further Reading (Query)

- API Datasets: `/reference/cloud/api/resources/datasets`

---

## Visualisation

You can use different chart types by utilizing the `visualisation` key of the dataset YAML file. The `visualisation` key contains information about displaying the chart for the insight.

### Example

```yaml
visualisation: |-
    {"chartjs-chart": {"chartType": "bar"}}
```

### ChartJS Charts

Beautiful ChartJS data visualisations can be achieved with the `chartjs-chart` visualisation type.

```yaml
visualisation: |-
    {"chartjs-chart": {"chartType": "bar"}}
```

| Value | Description |
|---|---|
| `bar` | Bar Chart |
| `line` | Line Chart |
| `doughnut` | Doughnut Chart |
| `pie` | Pie Chart |
| `bubble` | Bubble Chart |
| `scatter` | Scatter Chart |
| `treemap` | Treemap Chart |

For more information on Chart.js, see their documentation at https://www.chartjs.org/docs/latest/

### Mermaid Diagrams

Mermaid diagrams (https://mermaid.js.org/intro/#diagram-types) are supported with the `mermaid` visualisation type. The diagram syntax (https://mermaid.js.org/intro/syntax-reference.html) should be provided in `rawData`.

```yaml
visualisation: |-
    {"mermaid": {}}
rawData: |-
    erDiagram
        CUSTOMER }|..|{ DELIVERY-ADDRESS : has
        CUSTOMER ||--o{ ORDER : places
        CUSTOMER ||--o{ INVOICE : "liable for"
        DELIVERY-ADDRESS ||--o{ ORDER : receives
        INVOICE ||--|{ ORDER : covers
        ORDER ||--|{ ORDER-ITEM : includes
        PRODUCT-CATEGORY ||--|{ PRODUCT : contains
        PRODUCT ||--o{ ORDER-ITEM : "ordered in"
```

### Carousel

You can display images side-by-side with back/next buttons using the `carousel` visualisation type.

```yaml
visualisation: |-
    {"carousel": {}}
```

#### Options

**`style`** — CSS overrides to set on the main carousel container element, to override its default styling.

Type: object. Default: none.

```yaml
visualisation: |-
    {"carousel": {"style": {
        "max-width": "600px",
        "padding": "12px",
        "background-color": "rgba(0, 0, 0, 0.1)"
    }}}
```

### HTML Table

Basic table layout for datasets can be achieved with the `html-table` visualisation type.

```yaml
visualisation: |-
    {"html-table": {}}
```

### HTML Metric

Metric layout for datasets can be achieved with the `html-metric` visualisation type.

```yaml
visualisation: |-
    {"html-metric": {}}
```

This visualisation is designed to be used as either a single metric of a total, or to display a total and its breakdown.

The first value you pass will be displayed as a big centered value, and every subsequent value will be smaller and in a row below the first. This lets you do things like show the total number of tests run, then the number of passed and failed below.

#### Color Options

By default the background is white and the text is black, but in all datasets you can pass a `palette` setting through the chart's `metadata`:

```yaml
metadata: |-
  {
      "name": "elementary_test_results",
      "label": "metric",
      "related_table": {
        "columns": [
        ],
        "aggregates": [
            {"name": "total", "label": "Total", "description": "Total"},
            {"name": "pass", "label": "Pass", "description": "Pass"},
            {"name": "fail", "label": "Fail", "description": "Fail"}
        ]
      },
    "palette": [[255, 255, 255],[0, 0, 0],[0, 255, 0],[255, 0, 0]]
  }
```

For `html-metric`, the first color is always the background, then every other color applies in order to each of the aggregates you are visualising. If you only provide 2 colors and 2 aggregates then you get:

- The first color as background.
- The second color on the first aggregate.
- The default black text color for the second aggregate.

### Further Reading (Visualisation)

- API Datasets: `/reference/cloud/api/resources/datasets`
- Example Charts: see Basic Examples below

---

## Basic Examples

These charts are the output of the dataset YAML files listed below each of them. Original YAML files are available in the examples GitHub repo: https://github.com/Matatika/matatika-examples/tree/master/example_datasets

### Basic Bar Chart

```yaml
version: datasets/v0.2
title: Example Basic Bar Chart
questions: How many Earth-years does it take for Jupiter to orbit the sun?
description: |-
  #Example

  Sun orbit data for some planets within our solar system.
metadata: |-
  {
    "name": "planet",
    "related_table": {
      "columns": [
        {"name": "name", "label": "Planet Name", "description": "Planet Name"}
      ],
      "aggregates": [
        {"name": "orbitduration", "label": "Orbit Duration (Earth Years)", "description": "Orbit Duration (Earth Years)"}
      ]
    }
  }
rawData: |-
  [
    {"planet.name": "Earth", "planet.orbitduration": 1},
    {"planet.name": "Mars", "planet.orbitduration": 1.9167},
    {"planet.name": "Jupiter", "planet.orbitduration": 11.8333},
    {"planet.name": "Saturn", "planet.orbitduration": 29.5}
  ]
visualisation: '{"chartjs-chart": {"chartType": "bar"}}'
```

### Grouped Bar Chart

```yaml
version: datasets/v0.2
title: Example Grouped Bar Chart
questions: How many Earth-years does it take for Jupiter to orbit the sun?
description: |-
  #Example

  Sun orbit data for some planets within our solar system.
metadata: |-
  {
    "name": "planet",
    "related_table": {
      "columns": [
        {"name": "name", "label": "Planet Name", "description": "Planet Name"}
      ],
      "aggregates": [
        {"name": "orbitduration", "label": "Orbit Duration (Earth Years)", "description": "Orbit Duration (Earth Years)"},
        {"name": "orbitdistance", "label": "Orbit Distance (Light Years)", "description": "Orbit Distance (Light Years)"}
      ]
    }
  }
rawData: |-
  [
    {"planet.name": "Earth", "planet.orbitdistance": 0.8708, "planet.orbitduration": 1},
    {"planet.name": "Mars", "planet.orbitdistance": 1.3242, "planet.orbitduration": 1.9167},
    {"planet.name": "Jupiter", "planet.orbitdistance": 4.5287, "planet.orbitduration": 11.8333},
    {"planet.name": "Saturn", "planet.orbitdistance": 8.2997, "planet.orbitduration": 29.5}
  ]
visualisation: '{"chartjs-chart": {"chartType": "bar"}}'
```

### Stacked Bar Chart

```yaml
version: datasets/v0.2
title: Example Stacked Bar Chart
questions: How many Earth-years does it take for Jupiter to orbit the sun?
description: |-
  #Example

  Sun orbit data for some planets within our solar system.
metadata: |-
  {
    "name": "planet",
    "related_table": {
      "columns": [
        {"name": "name", "label": "Planet Name", "description": "Planet Name"}
      ],
      "aggregates": [
        {"name": "orbitduration", "label": "Orbit Duration (Earth Years)", "description": "Orbit Duration (Earth Years)"},
        {"name": "orbitdistance", "label": "Orbit Distance (Light Years)", "description": "Orbit Distance (Light Years)"}
      ]
    }
  }
rawData: |-
  [
    {"planet.name": "Earth", "planet.orbitdistance": 0.8708, "planet.orbitduration": 1},
    {"planet.name": "Mars", "planet.orbitdistance": 1.3242, "planet.orbitduration": 1.9167},
    {"planet.name": "Jupiter", "planet.orbitdistance": 4.5287, "planet.orbitduration": 11.8333},
    {"planet.name": "Saturn", "planet.orbitdistance": 8.2997, "planet.orbitduration": 29.5}
  ]
visualisation: |-
  {
    "chartjs-chart": {
      "chartType": "bar",
      "options": {
        "scales": {
          "x": {
            "stacked": true
          }
        }
      }
    }
  }
```

### Doughnut Chart

```yaml
version: datasets/v0.2
title: Example Basic Doughnut Chart
questions: What shop had the most visitors?
description: |-
  #Example

  Stats for shops and visitor amount.
metadata: |-
  {
    "name": "customer",
    "related_table": {
      "columns": [
      ],
      "aggregates": [
        {"name": "visitors", "label": "Visitors", "description": "Number of Visitors"},
        {"name": "sales", "label": "Sales", "description": "Number of Sales"}
      ]
    }
  }
rawData: |-
  [
    {"customer.visitors": 1150, "customer.sales": 1040}
  ]
visualisation: '{"chartjs-chart": {"chartType": "doughnut"}}'
```

### Pie Chart

```yaml
version: datasets/v0.2
title: Example Basic Pie Chart
questions: For the last 7 days, how many visitors did Shop One have?
description: |-
  #Example

  Shop One visitors for the last 7 days.
metadata: |-
  {
    "name": "customer",
    "related_table": {
      "columns": [
      ],
      "aggregates": [
        {"name": "visitors_monday", "label": "Monday Visitors", "description": "Monday Visitors"},
        {"name": "visitors_tuesday", "label": "Tuesday Visitors", "description": "Tuesday Visitors"},
        {"name": "visitors_wednesday", "label": "Wednesday Visitors", "description": "Wednesday Visitors"},
        {"name": "visitors_thursday", "label": "Thursday Visitors", "description": "Thursday Visitors"},
        {"name": "visitors_friday", "label": "Friday Visitors", "description": "Friday Visitors"},
        {"name": "visitors_saturday", "label": "Saturday Visitors", "description": "Saturday Visitors"},
        {"name": "visitors_sunday", "label": "Sunday Visitors", "description": "Sunday Visitors"}
      ]
    }
  }
rawData: |-
  [
    {"customer.visitors_monday": 1090,
    "customer.visitors_tuesday": 980,
    "customer.visitors_wednesday": 1020,
    "customer.visitors_thursday": 1030,
    "customer.visitors_friday": 1150,
    "customer.visitors_saturday": 1430,
    "customer.visitors_sunday": 1290}
  ]
visualisation: '{"chartjs-chart": {"chartType": "doughnut"}}'
```

### Line Chart

```yaml
version: datasets/v0.2
title: Example Basic Line Chart
questions: Which shop had the most sales?
description: |-
  #Example

  Stats for shops, visitor amount, and sales.
metadata: |-
  {
    "name": "customer",
    "related_table": {
      "columns": [
        {"name": "name", "label": "Shop Name", "description": "Shop Name"}
      ],
      "aggregates": [
        {"name": "visitors", "label": "Visitors", "description": "Number of Visitors"},
        {"name": "sales", "label": "Sales", "description": "Number of Sales"}
      ]
    }
  }
rawData: |-
  [
    {"customer.name": "Shop One", "customer.visitors": 1150, "customer.sales": 1040},
    {"customer.name": "Shop Two", "customer.visitors": 980, "customer.sales": 670},
    {"customer.name": "Shop Three", "customer.visitors": 1020, "customer.sales": 990},
    {"customer.name": "Shop Four", "customer.visitors": 1410, "customer.sales": 1020},
    {"customer.name": "Shop Five", "customer.visitors": 890, "customer.sales": 800}
  ]
visualisation: '{"chartjs-chart": {"chartType": "line"}}'
```

---

## Advanced Examples

These charts are the output of the dataset YAML files listed below each of them. Original YAML files are available in the examples GitHub repo: https://github.com/Matatika/matatika-examples/tree/master/example_datasets

### Labeled Axis

```yaml
version: datasets/v0.2
title: Example Labeled Line Chart
questions: How do the shops compare against visitors and sales?
description: |-
  #Example

  Stats for shops, visitor amount, and sales.
metadata: |-
  {
    "name": "customer",
    "related_table": {
      "columns": [
        {"name": "sales", "label": "Sales", "description": "Number of Sales"}
      ],
      "aggregates": [
        {"name": "visitors", "label": "Visitors", "description": "Number of Visitors"}
      ]
    }
  }
rawData: |-
  [
    {"customer.name": "Shop One", "customer.visitors": 1150, "customer.sales": 1040},
    {"customer.name": "Shop Two", "customer.visitors": 980, "customer.sales": 670},
    {"customer.name": "Shop Three", "customer.visitors": 1020, "customer.sales": 990},
    {"customer.name": "Shop Four", "customer.visitors": 1410, "customer.sales": 1020},
    {"customer.name": "Shop Five", "customer.visitors": 890, "customer.sales": 800}
  ]
visualisation: |-
  {"chartjs-chart":
    {"chartType": "line",
      "options": {
        "scales": {
          "y": {
            "title": {
              "display": true,
              "text": "Number of Visitors"
            }
          },
          "x": {
            "title": {
              "display": true,
              "text": "Number of Sales"
            }
          }
        }
      }
    }
  }
```

### Max Axis Scale

```yaml
version: datasets/v0.2
title: Example Max Scale Line Chart
questions: Are shops meeting their sales target percentage.
description: |-
  #Example

  Stats for shops, their sales target percentage and their actual sales percentage.
metadata: |-
  {
    "name": "customer",
    "related_table": {
      "columns": [
        {"name": "name", "label": "Shop Name", "description": "Shop Name"}
      ],
      "aggregates": [
        {"name": "sales_target_percent", "label": "Sales Target Percentage", "description": "Sales Target Percentage"},
        {"name": "sales_percent", "label": "Sales Percentage", "description": "Sales Percentage"}
      ]
    }
  }
rawData: |-
  [
    {"customer.name": "Shop One", "customer.sales_target_percent": 80, "customer.sales_percent": 67},
    {"customer.name": "Shop Two", "customer.sales_target_percent": 80, "customer.sales_percent": 81},
    {"customer.name": "Shop Three", "customer.sales_target_percent": 80, "customer.sales_percent": 85},
    {"customer.name": "Shop Four", "customer.sales_target_percent": 80, "customer.sales_percent": 64},
    {"customer.name": "Shop Five", "customer.sales_target_percent": 80, "customer.sales_percent": 74}
  ]
visualisation: |-
  {"chartjs-chart":
    {"chartType": "line",
      "options": {
        "scales": {
          "y": {
            "max": 100
          }
        }
      }
    }
  }
```

### Scale Start At 0

```yaml
version: datasets/v0.2
title: Example Start At 0 Line Chart
questions: Which shop had the most sales?
description: |-
  #Example

  Stats for shops, visitor amount, and sales.
metadata: |-
  {
    "name": "customer",
    "related_table": {
      "columns": [
        {"name": "name", "label": "Shop Name", "description": "Shop Name"}
      ],
      "aggregates": [
        {"name": "visitors", "label": "Visitors", "description": "Number of Visitors"},
        {"name": "sales", "label": "Sales", "description": "Number of Sales"}
      ]
    }
  }
rawData: |-
  [
    {"customer.name": "Shop One", "customer.visitors": 1150, "customer.sales": 1040},
    {"customer.name": "Shop Two", "customer.visitors": 980, "customer.sales": 670},
    {"customer.name": "Shop Three", "customer.visitors": 1020, "customer.sales": 990},
    {"customer.name": "Shop Four", "customer.visitors": 1410, "customer.sales": 1020},
    {"customer.name": "Shop Five", "customer.visitors": 890, "customer.sales": 800}
  ]
visualisation: |-
  {"chartjs-chart":
    {"chartType": "line",
      "options": {
        "scales": {
          "y": {
            "beginAtZero": true
          }
        }
      }
    }
  }
```

### Tick Scaling

```yaml
version: datasets/v0.2
title: Example Tick Scaling Bar Chart
questions: How many deliveries does each shop have?
description: |-
  #Example

  This dataset show the shop and how many daily deliveries they receive.
metadata: |-
  {
    "name": "shop",
    "related_table": {
      "columns": [
        {"name": "name", "label": "Shop Name", "description": "Shop Name"}
      ],
      "aggregates": [
        {"name": "daily_deliveries", "label": "Daily Deliveries", "description": "Daily Deliveries"}
      ]
    }
  }
rawData: |-
  [
    {"shop.name": "Shop One", "shop.daily_deliveries": 1},
    {"shop.name": "Shop Two", "shop.daily_deliveries": 2},
    {"shop.name": "Shop Three", "shop.daily_deliveries": 1}
  ]
visualisation: |-
  {"chartjs-chart":
    {"chartType": "bar",
      "options": {
        "scales": {
          "y": {
            "beginAtZero": true,
            "ticks": {
              "stepSize": 1
            }
          }
        }
      }
    }
  }
```
