# Database Schema — Person A / Person B Contract

This document is the source-of-truth contract for the SQLite schema shared between
Person A (scraping + database + UI) and Person B (LLM extraction + aggregation +
summaries). Any change here must be agreed by both sides before the implementation
moves.

## Tables

### `restaurants`

Master list of restaurants tracked in the system.

| Column          | Type    | Notes                                |
|-----------------|---------|--------------------------------------|
| `restaurant_id` | INTEGER | Primary key.                         |
| `name`          | TEXT    | Display name of the restaurant.      |
| `menu_json`     | JSON    | JSON blob with the menu (dishes, sections). Used by Person B for canonical-dish matching. |

### `reviews_raw` — populated by Person A

One row per scraped review. Person B reads from this table and never writes to it.

| Column          | Type    | Notes                                                          |
|-----------------|---------|----------------------------------------------------------------|
| `review_id`     | INTEGER | Primary key.                                                   |
| `restaurant_id` | INTEGER | Foreign key → `restaurants.restaurant_id`.                     |
| `platform`      | TEXT    | `"google"` or `"tripadvisor"`.                                 |
| `review_date`   | DATE    | Date the review was posted on the source platform.             |
| `rating`        | INTEGER | Star rating as reported by the platform (typically 1–5).       |
| `review_text`   | TEXT    | Raw review body.                                               |
| `language`      | TEXT    | Nullable. ISO language code if detected at scrape time.        |
| `reviewer_name` | TEXT    | Nullable. Display name of the reviewer.                        |

### `extracted_data` — populated by Person B

One row per processed review. Person B writes here; Person A reads from it for the UI.

| Column            | Type     | Notes                                                                                |
|-------------------|----------|--------------------------------------------------------------------------------------|
| `review_id`       | INTEGER  | Primary key, foreign key → `reviews_raw.review_id`.                                  |
| `extraction_json` | JSON     | Structured extraction output. Schema below.                                          |
| `prompt_version`  | TEXT     | Version tag of the prompt used (e.g. `"v1.0"`). Lets us re-extract on prompt change. |
| `extracted_at`    | DATETIME | Timestamp of extraction.                                                             |
| `input_tokens`    | INTEGER  | Tokens sent to Gemini for this review.                                               |
| `output_tokens`   | INTEGER  | Tokens returned by Gemini for this review.                                           |

## `extraction_json` Schema

The `extraction_json` blob stored in `extracted_data.extraction_json` follows this shape:

```json
{
  "overall_sentiment": float,
  "language_detected": str,
  "dishes_mentioned": [
    {"raw_mention": str, "canonical_dish": str|null, "sentiment": float, "supporting_quote": str}
  ],
  "service_aspects": {
    "speed": {"sentiment": float, "mentioned": bool, "quote": str|null},
    "friendliness": {"sentiment": float, "mentioned": bool, "quote": str|null},
    "cleanliness": {"sentiment": float, "mentioned": bool, "quote": str|null},
    "staff_named": [str]
  },
  "atmosphere": {"sentiment": float, "mentioned": bool, "notes": str|null},
  "value_for_money": {"sentiment": float, "mentioned": bool},
  "specific_complaints": [str],
  "specific_praise": [str]
}
```

Sentiment values are floats in `[-1.0, 1.0]`. `canonical_dish` is `null` when the
mention cannot be matched against `restaurants.menu_json`.
