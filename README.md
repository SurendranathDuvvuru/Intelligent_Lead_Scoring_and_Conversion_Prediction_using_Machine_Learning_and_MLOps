# Intelligent Lead Scoring and Conversion Prediction using Machine Learning and MLOps

## Project Overview

This project explores how historical lead-acquisition information and website-engagement activity can be used to estimate whether a prospective lead will complete an application. It brings together data preparation, feature engineering, model experimentation, and an intended MLOps workflow for training and inference.

The business objective is to help sales and marketing teams prioritise prospective customers. A lead-scoring model can identify leads that appear more likely to complete an application, allowing teams to focus follow-up activity and counselling effort more effectively.

**Prediction target:** `app_complete_flag` — the application-completion indicator in the dataset.

---

## Problem Statement

The problem is to use historical lead attributes and engagement signals to learn patterns associated with application completion and prepare a repeatable workflow that can:

1. ingest lead records and validate their structure;
2. transform acquisition and engagement fields into model-ready features;
3. experiment with machine-learning models and select a candidate;
4. prepare new lead records for inference; and
5. monitor input structure and the distribution of predictions.

The model's output is intended to support lead prioritisation. It should complement, not replace, business judgement and sales-team follow-up.

## Dataset and Important Fields

The repository contains a raw lead dataset at:

`Lead_scoring_data_pipeline/Lead_scoring_data_pipeline/data/leadscoring.csv`

The model experimentation notebook uses a prepared dataset at:

`notebooks/Data/cleaned_data.csv`

The raw-data schema includes lead creation date, mapped city, acquisition platform, UTM medium and source, referral and dropped-lead fields, website interaction events, and the application-completion target.

| Field | Purpose |
|---|---|
| `created_date` | Lead creation timestamp; retained for data processing but excluded from the modelling features in the notebook. |
| `city_mapped` / `city_tier` | Geographic information. City names are mapped to tiers 1, 2, or 3. |
| `first_platform_c` | Platform through which the lead was first acquired. |
| `first_utm_medium_c` | Marketing medium associated with the acquisition. |
| `first_utm_source_c` | Marketing source associated with the acquisition. |
| `total_leads_droppped` | Lead-drop count/indicator field, using the spelling found in the source code. |
| `referred_lead` | Referral-related indicator. |
| Website interaction fields | Engagement signals such as syllabus, career, payment, social, and support interactions. |
| `app_complete_flag` | Target indicating whether the application was completed. |


---

## End-to-End Workflow

### Phase 1 — Data ingestion

The data-pipeline utility module provides functions to create/ connect to a SQLite database, load the source CSV, inspect database tables, and read sample records. The configured database is named `utils_output.db`, and the raw file is named `leadscoring.csv`.

The raw records are loaded into an intermediate table named `loaded_data`.

This phase brings lead information into a common storage location so that subsequent preparation steps can work on a consistent dataset.

### Phase 2 — Data validation and preparation

The repository defines a raw-data schema and a model-input schema. These describe the columns expected in the source data and the reduced set of fields expected by the modelling workflow. 
Validation-related modules and test assets are available under `unit_test/`.

#### 2.1 City-tier mapping

The city mapping dictionary assigns known cities to three tiers:

- **Tier 1:** Major cities such as Bengaluru, Chennai, Hyderabad, Kolkata, Mumbai, NCR, and Pune.
- **Tier 2:** Other specifically mapped cities.
- **Tier 3:** Smaller or other mapped cities.

The data utility assigns tier 3 when a city is not present in the mapping dictionary. A large number of city names is converted into a smaller, consistent geographic feature that can be used by the model.

#### 2.2 Acquisition-category consolidation

The project maintains lists of significant values for `first_platform_c`, `first_utm_medium_c`, and `first_utm_source_c`. The data-preparation code calculates the cumulative frequency of values and uses a 90% frequency-coverage approach to identify commonly occurring categories. Values outside the retained lists are grouped under `others` during the interaction/data transformation stage. Rare campaign, platform, and source values are consolidated rather than being treated as many separate categories.

#### 2.3 Missing values and duplicate records

The transformation utility fills missing values in `total_leads_droppped` and `referred_lead` with zero. It removes the original `city_mapped` field after creating `city_tier` and removes duplicate records before producing the interaction-level data.

#### 2.4 Website-interaction aggregation

The file `mapping/interaction_mapping.csv` maps detailed website events into five broader engagement categories:

| Aggregated feature | Example source events |
|---|---|
| `assistance_interaction` | Call-us, chat, live-chat, callback, support-number, and student-support events. |
| `career_interaction` | Career assistance, career coach, hiring partners, placement support, and job-opportunity events. |
| `payment_interaction` | EMI partner, EMI plan, fee-component, and payment-amount events. |
| `social_interaction` | Shorts-entry and social-referral events. |
| `syllabus_interaction` | Syllabus downloads, curriculum, programme structure, specialisation, and programme-page events. |

The utility reshapes the interaction columns into rows, joins the mapping file, and pivots the grouped values into aggregate interaction columns. Many individual website clicks become a smaller set of meaningful engagement indicators, such as interest in career support, payment options, or course information.

### Phase 3 — Exploratory Data analysis and feature selection

The notebook `notebooks/lead_scoring_model_experimentation.ipynb` reads the cleaned CSV and prepares data for model experimentation. `created_date` has been removed from the modelling data and a 10% samplehas been reserved as unseen data using `random_state=42`. The remaining 90% is used for experimentation.

The notebook has the following selected fields:

- `total_leads_droppped`
- `city_tier`
- `referred_lead`
- `first_platform_c`
- `first_utm_medium_c`
- `first_utm_source_c`
- `app_complete_flag` — the target, not a predictor

The `app_complete_flag` has been seperated using training utility as the target when preparing the training tables.

### Phase 4 — Model experimentation and training

PyCaret has been used in the notebook to compare candidate models, create a LightGBM model, and tune its hyperparameters. The principal experimentation calls are:

```python
best = compare_models(
    sort="RMSE",
    exclude=["knn", "dummy", "svm", "ada"],
    fold=5
)

lgbm = create_model("lightgbm", fold=10)

tuned_lgbm = tune_model(
    lgbm,
    fold=5,
    optimize="RMSE"
)
```

The training utility used a fixed session seed (`42`) and configured an 80/20 train-validation split in its PyCaret setup. It compared models and explicitly created and tuned LightGBM.

**Model pursued in the code:** LightGBM.

**Important modelling clarification:** The committed training utility imports `pycaret.regression`, and the notebook's comparison/tuning calls optimise RMSE. Although the project is described as a lead-classification/conversion-prediction problem and `app_complete_flag` is a binary outcome, the visible experimentation code uses PyCaret's regression interface. The modelling setup should be reviewed and, if the intended output is a binary class/probability, migrated to a classification workflow with appropriate metrics such as ROC-AUC, precision, recall, F1-score, and a confusion matrix. Comments in the notebook mention AUC, but the actual tuning call shown optimises RMSE.

`pycaret.regression` has been imported by training utility, and RMSE optimization was called in the notebook's comparison/tuning. This is a lead-classification/ conversion-prediction problem and `app_complete_flag` is a binary outcome, and PyCaret's regression interface has been used and experimented. The modelling setup has been reviewed and the intended output is a binary class/ probability, a classification workflow was migrated with appropriate metrics such as ROC-AUC, precision, recall, F1-score, and a confusion matrix.

### Phase 5 — Inference preparation

A feature-preparation path is defined in inference utility for new lead data. Its visible `encode_features()` function:

1. reads the incoming CSV;
2. applies one-hot encoding to configured fields using `pandas.get_dummies()`;
3. assembles the expected input columns;
4. fills missing values with zero;
5. removes the timestamp, target, and aggregate interaction columns from the inference feature set; and
6. writes the resulting features to a SQLite table named `features`.

It has been documented that the inference module's intention is to load the production model from the MLflow Model Registry and generate predictions. The checks for prediction distribution and required input fields were also described.

### Phase 6 — MLOps and workflow orchestration design

The repository separates the intended workflow into three pipeline areas:

| Pipeline | Intended responsibility | Schedule currently declared |
|---|---|---|
| Data pipeline | Ingest, validate, clean, map, and prepare lead data. | Daily (`@daily`) in the DAG file under `unit_test/`. |
| Training pipeline | Encode features, compare/train models, and support periodic retraining. | Monthly (`@monthly`). |
| Inference pipeline | Prepare new records and generate lead predictions. | Hourly (`@hourly`). |

The training and inference utilities import MLflow components. Their comments describe experiment tracking, model registration, and loading a model from the MLflow Production stage.
MLflow components were imported from training and inference utilities. Experiment tracking, model registration, and loading a model from the MLflow Production stage have been described.

---

## Repository Structure

```text
CodePros_Lead_Classification-assignment/
│
├── AssignmentToSuubmit.pdf
│
├── Lead_scoring_data_pipeline/
│   └── Lead_scoring_data_pipeline/
│       ├── constants.py
│       ├── schema.py
│       ├── utils.py
│       ├── data/
│       │   └── leadscoring.csv
│       └── mapping/
│           ├── city_tier_mapping.py
│           ├── significant_categorical_level.py
│           └── interaction_mapping.csv
│
├── Lead_scoring_training_pipeline/
│   ├── constants.py
│   ├── lead_scoring_training_pipeline.py
│   └── utils.py
│
├── Lead_scoring_inference_pipeline/
│   ├── constants.py
│   ├── lead_scoring_inference_pipeline.py
│   └── utils.py
│
├── notebooks/
│   ├── Data/
│   │   └── cleaned_data.csv
│   ├── lead_scoring_model_experimentation.ipynb
│   └── lead_scoring_model_experimentation.db
│
└── unit_test/
    ├── city_tier_mapping.py
    ├── constants.py
    ├── data_validation_checks.py
    ├── interaction_mapping.csv
    ├── lead_scoring_data_pipeline.py
    ├── leadscoring_test.csv
    ├── schema.py
    ├── significant_categorical_level.py
    ├── test_with_pytest.py
    ├── unit_test_cases.db
    └── utils.py
```

---

## Technology Stack

| Area | Tools / libraries | Purpose |
|---|---|---|
| Programming | Python 3.8.12 | Data processing and pipeline logic. |
| Data manipulation | Pandas, NumPy | Read, clean, transform, and prepare lead data. |
| Storage | SQLite | Store intermediate pipeline tables. |
| Machine learning | PyCaret 2.3.8, LightGBM, scikit-learn | Model comparison, model creation, and tuning. |
| Experiment tracking / model registry (intended) | MLflow | Experiment logging and model lifecycle management. |
| Workflow orchestration (intended) | Apache Airflow | Schedule data, training, and inference workflows. |
| Testing | pytest | Unit-test framework and pipeline test cases. |
| Development | Jupyter Notebook | Exploratory analysis and model experimentation. |

---

## Testing

The `unit_test/` directory contains pytest-oriented tests and supporting test data, schemas, mapping files, and SQLite test databases. The tests cover data-pipeline transformations such as city-tier mapping, categorical mapping, and interaction aggregation.

A starting command is:

```bash
pytest unit_test/test_with_pytest.py -v
```
---

## Key Learning Outcomes

- Structured a lead-data preparation workflow covering ingestion, schema definitions, cleaning, mapping, and feature generation.
- Applied business-oriented feature engineering through city-tier assignment, acquisition-category consolidation, and website-interaction aggregation.
- Used PyCaret experimentation to compare candidate estimators and develop a LightGBM-based modelling approach.
- Organised separate data, training, and inference components with the intention of supporting scheduled machine-learning workflows.
- Included pytest-oriented test assets and MLflow/ Airflow integration points as part of an MLOps-focused project structure.

## Project Summary

**Intelligent Lead Scoring and Conversion Prediction using Machine Learning and MLOps** demonstrates how lead-acquisition attributes and website-engagement signals can be transformed into structured features for modelling application completion. The repository combines Python-based data engineering, SQLite storage, feature engineering, PyCaret experimentation, LightGBM model development, pytest-oriented test assets, and an intended Airflow/ MLflow lifecycle design.

## Author

**Surendranath Duvvuru**

- GitHub: [SurendranathDuvvuru](https://github.com/SurendranathDuvvuru)
- LinkedIn: [Surendranath Duvvuru](https://www.linkedin.com/in/surendranathduvvuru)
