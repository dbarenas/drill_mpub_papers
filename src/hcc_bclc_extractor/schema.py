from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, List, Dict, Any

EvidenceLevel = Literal["high", "moderate", "low"]

class StudyMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pmid: Optional[str] = None
    title: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None

    study_design: Optional[str] = None  # e.g., RCT, Phase II, Observational, Systematic Review
    phase: Optional[str] = None         # Phase I/II/III/IV if applicable
    sample_size_total: Optional[int] = None

    arms: Optional[List[str]] = None
    comparator: Optional[str] = None

class Treatment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    category: Optional[Literal["Surgical", "Locoregional", "Systemic", "Palliative", "Other"]] = None
    line_of_therapy: Optional[str] = None  # first-line, second-line...
    duration: Optional[str] = None
    combination: Optional[bool] = None
    components: Optional[List[str]] = None

class TumorBurden(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nodules: Optional[Literal["single", "2-3", ">3", "not_reported"]] = None
    largest_nodule_cm: Optional[float] = None
    vascular_invasion: Optional[bool] = None
    extrahepatic_spread: Optional[bool] = None
    afp_ng_ml: Optional[float] = None
    afp_gt_400: Optional[bool] = None

class ChildPugh(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bilirubin_mg_dl: Optional[float] = None
    albumin_g_dl: Optional[float] = None
    inr: Optional[float] = None
    ascites: Optional[Literal["none", "mild_controlled", "moderate_severe"]] = None
    encephalopathy: Optional[Literal["none", "grade_1_2", "grade_3_4"]] = None
    class_letter: Optional[Literal["A", "B", "C"]] = None
    score: Optional[int] = None

class PerformanceStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ecog: Optional[int] = Field(None, ge=0, le=4)

class BCLCBaseline(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tumor_burden: TumorBurden = Field(default_factory=TumorBurden)
    child_pugh: ChildPugh = Field(default_factory=ChildPugh)
    performance_status: PerformanceStatus = Field(default_factory=PerformanceStatus)

class BCLC2025CUSE(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mentioned: bool = False
    cuse_criteria: Optional[List[str]] = None
    personalized_factors: Optional[List[str]] = None
    decision_logic: Optional[str] = None

class OutcomeMetric(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: Optional[str] = None  # keep as string to preserve units/format like "12.3 mo"
    ci: Optional[str] = None  # e.g., "95% CI, 12.0-15.2"
    p_value: Optional[str] = None # e.g., "p<0.001"
    hr: Optional[float] = None
    hr_ci: Optional[str] = None # e.g., "0.75-0.95"
    follow_up: Optional[str] = None

    # Evidence fields
    evidence_section: Optional[str] = None # e.g., "Results - Survival Analysis"
    evidence_page: Optional[int] = None
    table_figure: Optional[str] = None # e.g., "Table 2"
    verbatim_excerpt: Optional[str] = None

class EvidenceSpan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    field_path: str
    value_json: str
    evidence_section: Optional[str] = None
    evidence_page: Optional[int] = None
    table_figure: Optional[str] = None
    verbatim_excerpt: Optional[str] = None
    locator: Optional[str] = None

class Results(BaseModel):
    model_config = ConfigDict(extra="forbid")
    response_criteria: Optional[str] = None  # RECIST/mRECIST
    os: OutcomeMetric = Field(default_factory=OutcomeMetric)
    pfs: OutcomeMetric = Field(default_factory=OutcomeMetric)
    orr: OutcomeMetric = Field(default_factory=OutcomeMetric)
    dcr: OutcomeMetric = Field(default_factory=OutcomeMetric)
    ttp: OutcomeMetric = Field(default_factory=OutcomeMetric)
    other: Optional[Dict[str, Any]] = None

class AdverseEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    grade: Optional[str] = None   # "3-4", "any", etc.
    frequency: Optional[str] = None  # "12/100 (12%)"
    notes: Optional[str] = None

class Safety(BaseModel):
    model_config = ConfigDict(extra="forbid")
    any_adverse_events_reported: Optional[bool] = None
    grade_3_4_events: Optional[List[AdverseEvent]] = None
    saes: Optional[List[AdverseEvent]] = None
    discontinuation_due_to_toxicity: Optional[str] = None
    treatment_related_deaths: Optional[str] = None
    narrative: Optional[str] = None

class ExperimentArm(BaseModel):
    model_config = ConfigDict(extra="forbid")
    arm_name: Optional[str] = None
    treatment: Treatment = Field(default_factory=Treatment)
    bclc_baseline: BCLCBaseline = Field(default_factory=BCLCBaseline)
    bclc_stage_reported: Optional[Literal["0", "A", "B", "C", "D"]] = None
    bclc_2025_cuse: BCLC2025CUSE = Field(default_factory=BCLC2025CUSE)
    results: Results = Field(default_factory=Results)
    safety: Safety = Field(default_factory=Safety)

class ExtractionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    study_metadata: StudyMetadata
    experiments: List[ExperimentArm]
    evidence_level: EvidenceLevel
    evidence_spans: List[EvidenceSpan]
