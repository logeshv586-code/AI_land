# Land Area Automation API Documentation

## Overview

The Land Area Automation API provides comprehensive real estate analysis combining traditional land suitability analysis with advanced property valuation (AVM), beneficiary scoring, and AI-powered recommendations. This system integrates multiple data sources and machine learning models to provide actionable insights for real estate investment decisions.

## Key Features

- **Comprehensive Land Analysis**: Traditional suitability analysis enhanced with modern ML techniques
- **Automated Valuation Model (AVM)**: Property value prediction with uncertainty estimation
- **Beneficiary Scoring**: Multi-factor investment attractiveness scoring
- **Property Recommendations**: Content-based and collaborative filtering recommendations
- **SHAP Explainability**: Transparent AI decision making with feature attributions
- **Real-time Analysis**: Fast processing with confidence scoring

## Base URL

```
http://localhost:8000/api/v1/automation
```

## Authentication

All endpoints require authentication using Bearer tokens:

```http
Authorization: Bearer <your-token>
```

## Endpoints

### 1. Comprehensive Analysis

**POST** `/comprehensive-analysis`

Performs complete land area analysis combining all features.

#### Request Body

```json
{
  "address": "123 Main St, Chicago, IL",
  "latitude": 41.8781,
  "longitude": -87.6298,
  "property_type": "residential",
  "beds": 3,
  "baths": 2,
  "sqft": 1500,
  "year_built": 2000,
  "lot_size": 0.25,
  "investment_budget": 300000,
  "investment_timeline": "1-3 years",
  "risk_tolerance": "medium",
  "include_avm": true,
  "include_beneficiary_score": true,
  "include_recommendations": true,
  "include_explanations": true,
  "include_market_analysis": true,
  "custom_weights": {
    "value": 8.0,
    "school": 8.0,
    "crime_inv": 6.0,
    "env_inv": 5.0,
    "employer_proximity": 7.0
  },
  "max_recommendations": 10,
  "recommendation_radius_km": 10.0
}
```

#### Response

```json
{
  "analysis_id": 123,
  "location": {
    "id": 1,
    "address": "123 Main St, Chicago, IL",
    "latitude": 41.8781,
    "longitude": -87.6298,
    "city": "Chicago",
    "state": "IL"
  },
  "overall_score": 75.5,
  "recommendation": "buy",
  "confidence_level": 0.85,
  "scores": {
    "facility_score": 78.2,
    "safety_score": 72.1,
    "disaster_risk_score": 85.3,
    "market_potential_score": 68.9,
    "accessibility_score": 74.6
  },
  "beneficiary_score": {
    "overall_score": 78.2,
    "value_score": 75.0,
    "school_score": 85.0,
    "safety_score": 70.0,
    "environmental_score": 88.0,
    "accessibility_score": 72.0,
    "scoring_weights": {
      "value": 8.0,
      "school": 8.0,
      "crime_inv": 6.0,
      "env_inv": 5.0,
      "employer_proximity": 7.0
    }
  },
  "property_valuation": {
    "id": 456,
    "predicted_value": 275000.0,
    "value_uncertainty": 15000.0,
    "price_per_sqft": 183.33,
    "valuation_date": "2025-01-15T10:30:00Z"
  },
  "avm_confidence": 0.82,
  "predictions": {
    "predicted_value_change_1y": 0.05,
    "predicted_value_change_3y": 0.15,
    "predicted_value_change_5y": 0.28
  },
  "risk_factors": [
    {
      "factor": "High Crime Rate",
      "severity": "medium",
      "description": "Crime rate is above average with safety score of 70.0",
      "impact_score": 30.0
    }
  ],
  "opportunities": [
    {
      "opportunity": "Excellent School Access",
      "potential_impact": "high",
      "description": "Outstanding access to top-rated schools",
      "confidence": 0.9
    }
  ],
  "similar_properties": [
    {
      "id": 789,
      "recommended_property": {
        "id": 789,
        "predicted_value": 285000.0,
        "beds": 3,
        "baths": 2,
        "sqft": 1600
      },
      "recommendation_type": "content_based",
      "similarity_score": 0.87,
      "confidence_score": 0.75,
      "rank_position": 1,
      "recommendation_reason": "Similar property characteristics"
    }
  ],
  "feature_explanations": {
    "avm_explanation": {
      "base_value": 192500.0,
      "prediction_value": 275000.0,
      "top_positive_features": [
        {
          "feature_name": "sqft",
          "attribution_value": 45000.0,
          "feature_value": 1500,
          "impact_description": "Property size (1500 sq ft) increases property value by $45,000"
        }
      ],
      "explanation_type": "shap_tree"
    },
    "beneficiary_explanation": {
      "overall_score": 78.2,
      "component_explanations": [
        {
          "component": "school",
          "raw_score": 85.0,
          "weight": 8.0,
          "weighted_contribution": 6.8,
          "description": "School quality and accessibility: excellent (85.0%) with weight 8.0"
        }
      ]
    }
  },
  "created_at": "2025-01-15T10:30:00Z",
  "model_version": "2.0.0",
  "processing_time_ms": 1250
}
```

### 2. Property Valuation

**POST** `/property-valuation`

Get AVM-based property valuation with uncertainty estimation.

#### Request Body

```json
{
  "address": "123 Main St, Chicago, IL",
  "latitude": 41.8781,
  "longitude": -87.6298,
  "property_type": "residential",
  "beds": 3,
  "baths": 2,
  "sqft": 1500,
  "year_built": 2000,
  "lot_size": 0.25
}
```

#### Response

```json
{
  "id": 456,
  "location_id": 1,
  "property_type": "residential",
  "beds": 3,
  "baths": 2,
  "sqft": 1500,
  "year_built": 2000,
  "lot_size": 0.25,
  "predicted_value": 275000.0,
  "value_uncertainty": 15000.0,
  "price_per_sqft": 183.33,
  "comparable_sales_count": 12,
  "days_on_market_avg": 45.5,
  "valuation_date": "2025-01-15T10:30:00Z"
}
```

### 3. Beneficiary Score

**POST** `/beneficiary-score`

Calculate beneficiary score for investment attractiveness.

#### Request Body

```json
{
  "location_id": 1,
  "property_valuation_id": 456,
  "custom_weights": {
    "value": 8.0,
    "school": 9.0,
    "crime_inv": 7.0,
    "env_inv": 5.0,
    "employer_proximity": 6.0
  }
}
```

#### Response

```json
{
  "id": 789,
  "location_id": 1,
  "overall_score": 78.2,
  "value_score": 75.0,
  "school_score": 85.0,
  "safety_score": 70.0,
  "environmental_score": 88.0,
  "accessibility_score": 72.0,
  "scoring_weights": {
    "value": 8.0,
    "school": 9.0,
    "crime_inv": 7.0,
    "env_inv": 5.0,
    "employer_proximity": 6.0
  },
  "score_components": {
    "value": 6.0,
    "school": 7.65,
    "crime": 4.9,
    "env": 4.4,
    "employer": 4.32
  },
  "calculated_at": "2025-01-15T10:30:00Z",
  "model_version": "2.0.0"
}
```

### 4. Property Recommendations

**POST** `/recommendations`

Get property recommendations based on preferences or similar properties.

#### Request Body (by Property ID)

```json
{
  "property_id": 456,
  "max_recommendations": 5,
  "recommendation_type": "hybrid"
}
```

#### Request Body (by Location)

```json
{
  "location": {
    "lat": 41.8781,
    "lon": -87.6298
  },
  "radius_km": 10.0,
  "max_recommendations": 10,
  "user_preferences": {
    "min_beds": 2,
    "max_price": 350000,
    "property_type": "residential"
  }
}
```

#### Response

```json
[
  {
    "id": 789,
    "recommended_property": {
      "id": 789,
      "predicted_value": 285000.0,
      "beds": 3,
      "baths": 2,
      "sqft": 1600,
      "year_built": 2005
    },
    "recommendation_type": "content_based",
    "similarity_score": 0.87,
    "confidence_score": 0.75,
    "rank_position": 1,
    "recommendation_reason": "Similar property characteristics (similarity: 0.87)",
    "created_at": "2025-01-15T10:30:00Z"
  }
]
```

### 5. Property Explanation

**GET** `/property-valuation/{property_id}/explanation`

Get SHAP-based explanation for property valuation.

#### Response

```json
{
  "base_value": 192500.0,
  "prediction_value": 275000.0,
  "top_positive_features": [
    {
      "feature_name": "sqft",
      "attribution_value": 45000.0,
      "feature_value": 1500,
      "impact_description": "Property size (1500 sq ft) increases property value by $45,000"
    },
    {
      "feature_name": "norm_school",
      "attribution_value": 25000.0,
      "feature_value": 0.85,
      "impact_description": "School quality (0.85 rating) increases property value by $25,000"
    }
  ],
  "top_negative_features": [
    {
      "feature_name": "age",
      "attribution_value": -8000.0,
      "feature_value": 25,
      "impact_description": "Property age (25 years old) decreases property value by $8,000"
    }
  ],
  "explanation_type": "shap_tree",
  "model_version": "2.0.0",
  "generated_at": "2025-01-15T10:30:00Z"
}
```

### 6. User Interaction Logging

**POST** `/user-interaction`

Log user interactions for recommendation system improvement.

#### Request Body

```json
{
  "property_valuation_id": 456,
  "interaction_type": "view",
  "search_query": "3 bedroom house Chicago",
  "referrer_source": "google",
  "device_type": "desktop",
  "session_duration": 120
}
```

#### Response

```json
{
  "message": "Interaction logged successfully"
}
```

## Error Responses

All endpoints return standardized error responses:

```json
{
  "detail": "Error description",
  "status_code": 400
}
```

Common status codes:
- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Missing or invalid authentication
- `404`: Not Found - Resource not found
- `422`: Validation Error - Request validation failed
- `500`: Internal Server Error - Server processing error

## Rate Limiting

API requests are rate-limited to prevent abuse:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated requests

## Data Models

### Risk Tolerance Options
- `"low"`: Conservative investment approach
- `"medium"`: Balanced risk/reward approach  
- `"high"`: Aggressive investment approach

### Property Types
- `"residential"`: Single-family homes, condos, townhouses
- `"commercial"`: Office buildings, retail spaces
- `"industrial"`: Warehouses, manufacturing facilities

### Recommendation Types
- `"buy"`: Strong investment recommendation
- `"hold"`: Neutral/wait recommendation
- `"avoid"`: Not recommended for investment

### Interaction Types
- `"view"`: Property viewed
- `"save"`: Property saved/bookmarked
- `"contact"`: Contact made about property
- `"share"`: Property shared
- `"comprehensive_analysis"`: Full analysis performed

## Best Practices

1. **Include Location Data**: Always provide either address or coordinates
2. **Use Custom Weights**: Adjust scoring weights based on investment priorities
3. **Enable Explanations**: Include explanations for transparent decision making
4. **Log Interactions**: Track user behavior to improve recommendations
5. **Handle Uncertainty**: Consider value uncertainty in investment decisions
6. **Monitor Confidence**: Use confidence scores to assess analysis reliability

## Example Usage

See the `/examples` directory for complete code examples in various programming languages.
